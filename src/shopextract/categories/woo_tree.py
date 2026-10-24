"""Bounded opt-in Woo category acquisition, tree evidence and membership lookup."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Literal

import httpx

from .contracts import CategoryObservation, CategoryScope, CategoryTermRef
from ..tools.context import Resolver


@dataclass(frozen=True)
class WooTreeLimits:
    requests: int = 10
    per_page: int = 100
    categories: int = 1000
    response_bytes: int = 2 * 1024 * 1024
    retained_bytes: int = 8 * 1024 * 1024
    depth: int = 8
    seconds: float = 30.0


@dataclass(frozen=True)
class TreeFact:
    facet: Literal['id', 'name', 'slug', 'parent']
    pointer: str
    raw_value: object
    value: str | None
    state: Literal['observed', 'missing', 'null', 'malformed']
    source_url: str
    observed_at: datetime


@dataclass(frozen=True)
class TreeDeclaration:
    page: int
    index: int
    native_id: str | None
    facts: tuple[TreeFact, ...]


@dataclass(frozen=True)
class TreeNode:
    native_id: str
    declarations: tuple[TreeDeclaration, ...]
    conflicted: bool


@dataclass(frozen=True)
class TreeIssue:
    code: str
    node_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class TreePage:
    number: int
    source_url: str
    observed_at: datetime
    body: str
    total: str | None
    total_pages: str | None


@dataclass(frozen=True)
class TreeAttempt:
    number: int
    url_sha256: str
    status_code: int | None
    error: str | None


@dataclass(frozen=True)
class WooCategoryTree:
    scope: CategoryScope
    limits: WooTreeLimits
    outcome: Literal['complete', 'partial', 'unavailable', 'malformed']
    confirmed_empty: bool
    reasons: tuple[str, ...]
    pages: tuple[TreePage, ...]
    nodes: tuple[TreeNode, ...]
    rejected: tuple[TreeDeclaration, ...]
    parent_edges: tuple[tuple[str, str], ...]  # child, parent; roots have no edge
    issues: tuple[TreeIssue, ...]
    attempts: tuple[TreeAttempt, ...]
    schema_version: int = 1


@dataclass(frozen=True)
class TreeMembershipLink:
    observation_id: str
    term: CategoryTermRef
    status: Literal['linked', 'missing', 'conflicting', 'scope_mismatch', 'unsupported']
    node_id: str | None


# One module owns the opt-in snapshot; default extraction never imports it.
from collections import defaultdict
from contextlib import suppress
from dataclasses import fields, replace
from datetime import timezone
import hashlib
import json
import math
from urllib.parse import urlsplit, urlencode, parse_qsl

from .._models import Platform
from .._portable import validate_tree
from ..tools.context import OperationBudget, OperationContext
from ..tools.contracts import ToolError
from ..tools.execution import OwnedProcess
from ..tools.runtime import Limits, ToolConfig
from ..tools.security import GuardedTransport, SourceGuard, normalized
from ._codec import canonical, digest, typed, wire
from .contracts import CategoryError
from .helpers import merchant_scope, native_id, nonblank_text
from .mapping import _supported
from .validation import validate_observations

_CODES = ('cancelled', 'deadline', 'request_limit', 'category_limit', 'response_limit',
    'retention_limit', 'zero_budget', 'unsafe_url', 'url_limit', 'transport_error',
    'http_status', 'unsupported_content_encoding', 'malformed_json', 'malformed_collection',
    'malformed_facet', 'missing_headers', 'malformed_headers', 'totals_changed',
    'count_mismatch', 'repeated_page', 'duplicate_id', 'conflicting_id', 'missing_parent',
    'self_parent', 'cycle', 'depth_limit', 'unknown_parent')
_MAX_BYTES = 8 * 1024 * 1024


class _Stop(Exception):
    def __init__(self, code):
        self.code = code


def _validate_limits(limits):
    if not isinstance(limits, WooTreeLimits):
        raise CategoryError('WooTreeLimits required')
    for field in fields(limits):
        value, maximum = getattr(limits, field.name), getattr(WooTreeLimits(), field.name)
        if field.name == 'seconds':
            valid = type(value) in (float, int) and math.isfinite(value) and 0 <= value <= maximum
        else:
            valid = type(value) is int and 0 <= value <= maximum
        if not valid:
            raise CategoryError('Invalid Woo tree limit: ' + field.name)


def _validate_scope(scope):
    if not isinstance(scope, CategoryScope) or not isinstance(scope.platform, Platform) or scope.platform != Platform.WOOCOMMERCE:
        raise CategoryError('WooCommerce CategoryScope required')
    if not isinstance(scope.store_url, str) or not scope.store_url.strip():
        raise CategoryError('Store URL text required')
    if any(value is not None and (not isinstance(value, str) or not value.strip())
           for value in (scope.catalog, scope.channel, scope.locale)):
        raise CategoryError('Invalid merchant scope dimensions')


def _endpoint(scope):
    _validate_scope(scope)
    try:
        if urlsplit(scope.store_url).query:
            raise _Stop('unsafe_url')
        base, origin, _, _ = normalized(scope.store_url)
        endpoint = base.rstrip('/') + '/wp-json/wc/store/v1/products/categories'
        if len(endpoint.encode()) + 96 > 4096:
            raise _Stop('url_limit')
        return endpoint, origin
    except (ToolError, ValueError):
        raise _Stop('unsafe_url') from None


def _page_url(url, endpoint, number, limits):
    try:
        norm, origin, _, _ = normalized(url)
        _, expected_origin, _, _ = normalized(endpoint)
    except ToolError:
        raise _Stop('unsafe_url') from None
    if len(norm.encode()) > 4096:
        raise _Stop('url_limit')
    actual, expected = urlsplit(norm), urlsplit(endpoint)
    query = [('page', str(number)), ('per_page', str(limits.per_page)),
             ('hide_empty', 'false'), ('orderby', 'slug'), ('order', 'asc')]
    if (origin != expected_origin or actual.path.rstrip('/') != expected.path
        or sorted(parse_qsl(actual.query, keep_blank_values=True)) != sorted(query)):
        raise _Stop('unsafe_url')
    return norm


def _utc(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise CategoryError('Aware UTC receipt timestamp required')
    return value


def _reject_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result


def _rows(page):
    try:
        value = json.loads(page.body, object_pairs_hook=_reject_pairs,
                           parse_constant=lambda value: (_ for _ in ()).throw(ValueError()))
        validate_tree(value)
        # JSON accepts escaped lone surrogates; the portable UTF-8 evidence
        # contract does not. Validate before hashing or retaining any page.
        pending = [value]
        while pending:
            item = pending.pop()
            if isinstance(item, str):
                item.encode('utf-8')
            elif isinstance(item, dict):
                pending.extend(item.keys())
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
    except (ValueError, TypeError, RecursionError):
        raise _Stop('malformed_json') from None
    if not isinstance(value, list):
        raise _Stop('malformed_collection')
    return value


def _project(pages, limits, check=lambda: None):
    groups, rejected, reasons, issues = defaultdict(list), [], set(), set()
    for page in pages:
        for index, entry in enumerate(_rows(page)):
            check()
            facts = []
            for facet in ('id', 'name', 'slug', 'parent'):
                present = isinstance(entry, dict) and facet in entry
                raw = entry[facet] if present else None
                state, value = ('missing', None) if not present else ('null', None) if raw is None else ('observed', None)
                if state == 'observed':
                    try:
                        value = ('0' if type(raw) is int and raw == 0 else native_id(raw)) if facet == 'parent' else native_id(raw) if facet == 'id' else nonblank_text(raw)
                    except ValueError:
                        state = 'malformed'
                if state == 'malformed' or (facet != 'parent' and state != 'observed'):
                    reasons.add('malformed_facet')
                facts.append(TreeFact(facet, f'/{index}/{facet}', raw, value, state, page.source_url, page.observed_at))
            identity = facts[0].value
            declaration = TreeDeclaration(page.number, index, identity, tuple(facts))
            if identity is None:
                rejected.append(declaration)
            else:
                groups[identity].append(declaration)
    nodes, parents, unknown, roots = [], {}, set(), set()
    for identity in sorted(groups):
        check()
        declarations = groups[identity]
        # Compare normalized facets and states, not page-specific provenance.
        variants = {tuple((f.facet, f.state, f.value, f.facet == 'parent' and type(f.raw_value) is int and f.raw_value == 0) for f in d.facts) for d in declarations}
        conflict = len(variants) > 1
        nodes.append(TreeNode(identity, tuple(declarations), conflict))
        if len(declarations) > 1:
            reasons.add('duplicate_id')
        if conflict:
            reasons.add('conflicting_id')
            issues.add(('conflicting_id', (identity,)))
            continue
        parent = declarations[0].facts[3]
        if parent.state == 'observed':
            parents[identity] = parent.value
            if type(parent.raw_value) is int and parent.raw_value == 0:
                roots.add(identity)
        else:
            unknown.add(identity)
            issues.add(('unknown_parent', (identity,)))
    conflicts = {n.native_id for n in nodes if n.conflicted}
    candidates = {}
    for child, parent in parents.items():
        if child in roots:
            continue
        if child == parent:
            issues.add(('self_parent', (child,)))
        elif parent not in groups:
            issues.add(('missing_parent', (child, parent)))
        elif parent in conflicts:
            issues.add(('conflicting_id', (child, parent)))
        else:
            candidates[child] = parent
    # Iterative functional-graph walk detects long cycles independently of depth.
    finished, cycles = set(), set()
    for node in candidates:
        check()
        path, positions = [], {}
        at = node
        while at in candidates and at not in finished and at not in positions:
            positions[at] = len(path)
            path.append(at)
            at = candidates[at]
        if at in positions:
            cycle = tuple(sorted(path[positions[at]:]))
            cycles.update(cycle)
            issues.add(('cycle', cycle))
        finished.update(path)
    edges = []
    for child, parent in candidates.items():
        check()
        at, depth, invalid = child, 0, False
        while at in candidates:
            if at in cycles:
                invalid = True
                break
            depth += 1
            if depth > limits.depth:
                issues.add(('depth_limit', (child,)))
                invalid = True
                break
            at = candidates[at]
        if not invalid:
            edges.append((child, parent))
    return (tuple(nodes), tuple(rejected), tuple(sorted(edges)),
            tuple(TreeIssue(code, ids) for code, ids in sorted(issues)), reasons)


def _coverage(pages, limits):
    reasons, counts, baseline = set(), [], None
    for page in pages:
        rows = _rows(page)
        counts.append(len(rows))
        pair = (page.total, page.total_pages)
        if pair == (None, None):
            if page.number == 1 and len(rows) < limits.per_page:
                continue
            reasons.add('missing_headers')
            return False, False, reasons
        if any(v is None or not v.isascii() or not v.isdecimal() or len(v) > 20 for v in pair):
            return False, False, {'malformed_headers'}
        total, total_pages = map(int, pair)
        if total_pages != (total + limits.per_page - 1) // limits.per_page:
            return False, False, {'malformed_headers'}
        if baseline is not None and baseline != (total, total_pages):
            return False, False, {'totals_changed'}
        baseline = total, total_pages
    if baseline is None:
        return False, False, set()  # Eligible first short/empty headerless page.
    total, total_pages = baseline
    for page, count in zip(pages, counts):
        expected = min(limits.per_page, max(0, total - (page.number - 1) * limits.per_page))
        if count != expected:
            return False, False, {'count_mismatch'}
    terminal = len(pages) >= max(1, total_pages)
    if terminal and sum(counts) != total:
        return False, False, {'count_mismatch'}
    return terminal, terminal and total == 0, reasons


def _envelope(tree):
    payload = wire(tree)
    return {'schema_version': 1, 'payload': payload, 'sha256': digest(payload)}


def _reserved_bytes(tree):
    """Exact conservative admission size, including all final local metadata."""
    attempt = TreeAttempt(10, 'f' * 64, 599, 'unsupported_content_encoding')
    reserved = replace(tree, outcome='unavailable', confirmed_empty=False,
        reasons=tuple(sorted(_CODES)), attempts=(attempt,) * 10)
    return len(canonical(_envelope(reserved)).encode())


def _empty(scope, limits, reasons=()):
    return WooCategoryTree(scope, limits, 'unavailable', False, tuple(sorted(reasons)), (), (), (), (), (), ())


def _classify(error):
    if isinstance(error, _Stop):
        return error.code
    if isinstance(error, ToolError):
        message = error.message
        if 'unsupported_content_encoding' in message:
            return 'unsupported_content_encoding'
        if error.code == 'permission_denied':
            return 'unsafe_url'
        if error.code == 'timeout':
            return 'deadline'
        if error.code == 'resource_limit':
            return 'response_limit' if 'byte cap' in message else 'request_limit'
    return 'transport_error'


async def fetch_woocommerce_category_tree(
    scope: CategoryScope, *, limits: WooTreeLimits = WooTreeLimits(),
    cancelled: asyncio.Event | None = None, resolver: Resolver | None = None,
    wire_transport: httpx.AsyncBaseTransport | None = None,
    utc_now: Callable[[], datetime] | None = None,
) -> WooCategoryTree:
    """Acquire sequential captured pages, preserving incomplete evidence explicitly."""
    _validate_limits(limits)
    limits = replace(limits, seconds=float(limits.seconds))
    # Validate scope even for zero work; malformed scope is a caller error.
    _validate_scope(scope)
    loop = asyncio.get_running_loop()
    deadline = loop.time() + limits.seconds
    value = _empty(scope, limits)
    cancelled = cancelled or asyncio.Event()
    if cancelled.is_set():
        return replace(value, reasons=('cancelled',))
    if any(getattr(limits, key) == 0 for key in ('requests', 'per_page', 'categories', 'response_bytes', 'retained_bytes', 'seconds')):
        return replace(value, reasons=('zero_budget',))
    try:
        endpoint, origin = _endpoint(scope)
    except _Stop as error:
        return replace(value, reasons=(error.code,))
    if _reserved_bytes(value) > limits.retained_bytes:
        return replace(value, reasons=('retention_limit',))
    transport_limits = Limits(requests=limits.requests, redirects=limits.requests,
        response_bytes=limits.response_bytes, timeout_seconds=float(limits.seconds),
        graph_bytes=limits.retained_bytes)
    config = ToolConfig(allowed_origins=(origin,), limits=transport_limits)
    auxiliary = OwnedProcess(transport_limits)
    attempts = []
    actual_urls = []
    number = 1

    class Accounting:
        def before_request(self, method, url):
            try:
                _page_url(url, endpoint, number, limits)
            except _Stop:
                raise ToolError('permission_denied', 'Invalid category route/query') from None
            actual_urls.append(url)
            attempts.append(TreeAttempt(len(attempts) + 1, hashlib.sha256(url.encode()).hexdigest(), None, 'transport_error'))
        def after_request(self, method, url, status):
            attempts[-1] = replace(attempts[-1], status_code=status, error=None)

    context = OperationContext('woo-tree', deadline, cancelled,
        OperationBudget(transport_limits), auxiliary, datetime.now(timezone.utc), Accounting())
    guard = SourceGuard(config, resolver=resolver)
    transport = GuardedTransport(config, context, guard, wire_transport)
    utc_now = utc_now or (lambda: datetime.now(timezone.utc))

    def check():
        if cancelled.is_set():
            raise _Stop('cancelled')
        if loop.time() >= deadline:
            raise _Stop('deadline')

    async def get(client, url):
        check()
        fetch = asyncio.create_task(client.get(url))
        watcher = asyncio.create_task(cancelled.wait())
        try:
            done, _ = await asyncio.wait((fetch, watcher), timeout=max(0, deadline - loop.time()), return_when=asyncio.FIRST_COMPLETED)
            if fetch in done:
                return await fetch
            raise _Stop('cancelled' if watcher in done else 'deadline')
        finally:
            for task in (fetch, watcher):
                if not task.done():
                    task.cancel()
            for task in (fetch, watcher):
                with suppress(asyncio.CancelledError, Exception):
                    await task

    seen, reasons, number = set(), set(), 1
    try:
        async with httpx.AsyncClient(transport=transport, trust_env=False,
            follow_redirects=False, timeout=None, headers={'User-Agent': 'ShopExtract/0.1.2'}) as client:
            while True:
                check()
                if context.budget.requests_used >= limits.requests:
                    raise _Stop('request_limit')
                current_count = sum(len(_rows(p)) for p in value.pages)
                if current_count >= limits.categories:
                    raise _Stop('category_limit')
                query = urlencode({'page': number, 'per_page': limits.per_page,
                    'hide_empty': 'false', 'orderby': 'slug', 'order': 'asc'})
                response = await get(client, endpoint + '?' + query)
                check()
                if response.status_code != 200:
                    raise _Stop('http_status')
                try:
                    body = response.content.decode('utf-8')
                except UnicodeError:
                    raise _Stop('malformed_json') from None
                at = _utc(utc_now())
                raw_headers = (response.headers.get('x-wp-total'), response.headers.get('x-wp-totalpages'))
                invalid_header = any(v is not None and (len(v) > 20 or not v.isascii() or not v.isdecimal()) for v in raw_headers)
                total, pages = (None, None) if invalid_header else raw_headers
                page = TreePage(number, actual_urls[-1], at, body, total, pages)
                rows = _rows(page)
                if len(rows) + current_count > limits.categories:
                    raise _Stop('category_limit')
                signature = digest(wire(rows))
                repeated = bool(rows) and signature in seen
                newpages = value.pages + (page,)
                nodes, rejected, edges, issues, projection_reasons = _project(newpages, limits, check)
                complete, empty, coverage_reasons = _coverage(newpages, limits)
                next_reasons = reasons | projection_reasons | coverage_reasons
                if repeated:
                    next_reasons.add('repeated_page')
                if invalid_header:
                    next_reasons.add('malformed_headers')
                if complete and len(nodes) != sum(len(_rows(p)) for p in newpages):
                    next_reasons.add('count_mismatch')
                complete = complete and not next_reasons
                candidate = WooCategoryTree(scope, limits, 'complete' if complete else 'partial',
                    complete and empty, tuple(sorted(next_reasons)), newpages, nodes, rejected, edges, issues, tuple(attempts))
                if _reserved_bytes(candidate) > limits.retained_bytes:
                    raise _Stop('retention_limit')
                check()
                value, reasons = candidate, next_reasons
                seen.add(signature)
                if complete or coverage_reasons or repeated or invalid_header:
                    break
                # A full headerless first page is anomalous; never probe past it.
                if total is None and pages is None and (number > 1 or len(rows) >= limits.per_page):
                    reasons.add('missing_headers')
                    break
                # Terminal count with malformed/duplicate facets is still partial.
                terminal, _, _ = _coverage(newpages, limits)
                if terminal:
                    break
                number += 1
    except (_Stop, ToolError, httpx.HTTPError, OSError) as error:
        code = _classify(error)
        reasons.add(code)
        if attempts and attempts[-1].error is None and code in ('http_status', 'unsupported_content_encoding', 'response_limit', 'deadline', 'cancelled', 'transport_error'):
            attempts[-1] = replace(attempts[-1], error=code)
        if not value.pages and code in ('malformed_json', 'malformed_collection'):
            value = replace(value, outcome='malformed')
    finally:
        await transport.aclose()
        await auxiliary.cancel_and_reap(context)
    outcome = 'complete' if value.outcome == 'complete' and not reasons else 'partial' if value.pages else value.outcome
    return replace(value, outcome=outcome, confirmed_empty=value.confirmed_empty and outcome == 'complete',
                   reasons=tuple(sorted(reasons)), attempts=tuple(attempts))


def _supported_membership(observation, term):
    # Validate each candidate separately so a malformed sibling or label cannot
    # erase independently inspectable native-ID support.
    for fact in _supported(term, 'native_id', term.ref.native_id):
        try:
            if len(fact.outcome.source_values) != 1 or native_id(fact.raw_value) != term.ref.native_id:
                continue
            candidate = replace(observation, terms=(replace(term, facts=(fact,)),),
                                facts=(), parent_edges=())
            validate_observations((candidate,))
            return True
        except (ValueError, TypeError, AttributeError, KeyError, RecursionError):
            continue
    return False


def link_tree_memberships(tree: WooCategoryTree, observations: tuple[CategoryObservation, ...]) -> tuple[TreeMembershipLink, ...]:
    """Require bound observed accepted native-ID evidence, matching existing mapping."""
    nodes = {node.native_id: node for node in tree.nodes}
    result = []
    for observation in observations:
        if observation.relation != 'memberships':
            continue
        for term in observation.terms:
            if observation.scope != tree.scope or term.ref.merchant_scope != merchant_scope(tree.scope):
                status = 'scope_mismatch'
            elif term.ref.namespace != 'woocommerce:product_cat' or term.ref.native_id is None or not _supported_membership(observation, term):
                status = 'unsupported'
            elif term.ref.native_id not in nodes:
                status = 'missing'
            else:
                status = 'conflicting' if nodes[term.ref.native_id].conflicted else 'linked'
            result.append(TreeMembershipLink(observation.observation_id, term.ref, status,
                term.ref.native_id if status in ('linked', 'conflicting') else None))
    return tuple(result)


def _validate_result(tree):
    _validate_scope(tree.scope)
    _validate_limits(tree.limits)
    if tree.schema_version != 1 or tree.scope.platform != Platform.WOOCOMMERCE:
        raise CategoryError('Unsupported Woo tree scope/version')
    if not set(tree.reasons) <= set(_CODES) or tuple(sorted(set(tree.reasons))) != tree.reasons:
        raise CategoryError('Invalid tree reasons')
    if len(tree.attempts) > tree.limits.requests:
        raise CategoryError('Attempt budget exceeded')
    for index, attempt in enumerate(tree.attempts, 1):
        if (attempt.number != index or len(attempt.url_sha256) != 64
            or any(c not in '0123456789abcdef' for c in attempt.url_sha256)
            or (attempt.error is not None and attempt.error not in _CODES)
            or (attempt.status_code is not None and not 100 <= attempt.status_code <= 599)):
            raise CategoryError('Invalid attempt metadata')
    if tree.pages:
        try:
            endpoint, origin = _endpoint(tree.scope)
        except _Stop:
            raise CategoryError('Invalid retained scope URL') from None
        count = 0
        if len(tree.pages) > len(tree.attempts):
            raise CategoryError('Pages exceed attempts')
        for number, page in enumerate(tree.pages, 1):
            _utc(page.observed_at)
            try:
                norm, actual_origin, _, _ = normalized(page.source_url)
            except ToolError:
                raise CategoryError('Invalid page URL') from None
            if page.number != number or actual_origin != origin or len(norm.encode()) > 4096:
                raise CategoryError('Invalid page provenance')
            _page_url(page.source_url, endpoint, number, tree.limits)
            source_hash = hashlib.sha256(page.source_url.encode()).hexdigest()
            if not any(a.url_sha256 == source_hash and a.status_code == 200 and a.error is None for a in tree.attempts):
                raise CategoryError('Page lacks matching successful attempt')
            if len(page.body.encode()) > tree.limits.response_bytes:
                raise CategoryError('Page body cap exceeded')
            count += len(_rows(page))
            if any(v is not None and (len(v) > 20 or not v.isascii() or not v.isdecimal()) for v in (page.total, page.total_pages)):
                raise CategoryError('Invalid retained headers')
        if count > tree.limits.categories or tree.limits.per_page == 0:
            raise CategoryError('Category budget exceeded')
        nodes, rejected, edges, issues, projection_reasons = _project(tree.pages, tree.limits)
        if (nodes, rejected, edges, issues) != (tree.nodes, tree.rejected, tree.parent_edges, tree.issues):
            raise CategoryError('Tree projection differs from retained pages')
        complete, empty, coverage_reasons = _coverage(tree.pages, tree.limits)
        repeated = len({digest(wire(_rows(p))) for p in tree.pages if _rows(p)}) != sum(bool(_rows(p)) for p in tree.pages)
        forbidden = projection_reasons | coverage_reasons | ({'repeated_page'} if repeated else set())
        if not forbidden <= set(tree.reasons):
            raise CategoryError('Missing incomplete-coverage reason')
        if tree.outcome == 'complete' and (not complete or forbidden or tree.reasons or len(nodes) != count):
            raise CategoryError('Unsupported complete coverage')
        if tree.outcome not in ('partial', 'complete'):
            raise CategoryError('Retained pages require complete/partial outcome')
        if tree.confirmed_empty != (tree.outcome == 'complete' and empty):
            raise CategoryError('Unsupported confirmed empty state')
    elif tree.nodes or tree.rejected or tree.parent_edges or tree.issues or tree.confirmed_empty or tree.outcome not in ('unavailable', 'malformed'):
        raise CategoryError('Invalid unretained result')


def woo_tree_to_record(tree: WooCategoryTree) -> dict:
    """Validate the full bounded envelope including evidence and derived metadata."""
    try:
        typed(WooCategoryTree, wire(tree))
        _validate_result(tree)
        result = _envelope(tree)
        if len(canonical(result).encode()) > tree.limits.retained_bytes:
            raise CategoryError('Tree retained envelope cap exceeded')
        return result
    except (ValueError, TypeError, AttributeError, _Stop, RecursionError) as error:
        raise CategoryError(str(error)) from error


def woo_tree_from_record(record: dict) -> WooCategoryTree:
    """Strict replay validates raw-page-derived facts, graph, scope and coverage."""
    try:
        validate_tree(record, encoded=True)
        if not isinstance(record, dict) or set(record) != {'schema_version', 'payload', 'sha256'} or type(record['schema_version']) is not int or record['schema_version'] != 1:
            raise CategoryError('Invalid tree envelope')
        if len(canonical(record).encode()) > _MAX_BYTES or digest(record['payload']) != record['sha256']:
            raise CategoryError('Invalid tree digest/absolute cap')
        tree = typed(WooCategoryTree, record['payload'])
        if woo_tree_to_record(tree) != record:
            raise CategoryError('Noncanonical tree envelope')
        return tree
    except (ValueError, TypeError, KeyError, AttributeError, _Stop, RecursionError) as error:
        raise CategoryError(str(error)) from error
