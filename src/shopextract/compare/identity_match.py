"""Evidence-backed pair classification and one-to-one catalog reports.

Semantic candidate providers are optional callbacks; no network/model is required.
Candidates never authorize an exact match by themselves.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Callable, Iterable

from .._models import Product
from ..identity import supplier_scope
from .match import title_similarity


class MatchRelation(str, Enum):
    EXACT = "exact"
    VARIANT = "variant"
    BUNDLE = "bundle"
    SUBSTITUTE = "substitute"
    UNMATCHED = "unmatched"
    UNCERTAIN = "uncertain"


@dataclass
class MatchDecision:
    relation: MatchRelation
    confidence: float
    evidence: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    needs_review: bool = False
    index_a: int | None = None
    index_b: int | None = None
    candidate_method: str = "rules"


def _record(product: Product | dict) -> dict:
    return asdict(product) if isinstance(product, Product) else product


def _text(value: object) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).casefold().split())


def _gtin(value: object) -> str:
    digits = re.sub(r"[\s-]", "", str(value or ""))
    if not digits.isascii() or not digits.isdigit() or len(digits) not in (8, 12, 13, 14) or not int(digits):
        return ""
    # Invalid check digits must never authorize an exact match.
    total = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits[:-1])))
    return digits.zfill(14) if (10 - total % 10) % 10 == int(digits[-1]) else ""


def normalized_attributes(product: Product | dict) -> dict[str, str]:
    """Normalize explicit attributes plus conservative capacity/pack title cues."""
    p = _record(product)
    aliases = {"colour": "color", "ram": "memory", "capacity": "capacity", "pack_size": "pack_quantity"}
    result = {}
    for key, value in (p.get("attributes") or {}).items():
        key = aliases.get(_text(key), _text(key))
        if value is not None and _text(value):
            result[key] = _text(value)
    for key in ("color", "size", "memory", "storage", "capacity", "model", "pack_quantity"):
        if p.get(key) is not None and _text(p[key]):
            result[key] = _text(p[key])
    for key in ("memory", "storage", "capacity"):
        if key in result:
            result[key] = re.sub(r"\s+", "", result[key])
    variants = p.get("variants") or []
    if variants:
        options = [v.get("attributes") or {"title": _text(v.get("title"))} for v in variants]
        result["variant_options"] = str(sorted(str(sorted((str(k), _text(v)) for k, v in o.items())) for o in options))
    title = _text(p.get("title"))
    for key, cues in (("memory", "ram|memory"), ("storage", "storage|ssd|hdd")):
        match = re.search(rf"\b(?:{cues})\s*(\d+(?:\.\d+)?)\s*(gb|tb|mb)\b", title)
        if not match:
            match = re.search(rf"\b(\d+(?:\.\d+)?)\s*(gb|tb|mb)\s*(?:{cues})\b", title)
        if match:
            result.setdefault(key, match.group(1) + match.group(2))
    capacities = re.findall(r"\b(\d+(?:\.\d+)?)\s*(gb|tb|mb|ml|kg|litres?|liters?)\b", title)
    if capacities:
        result["title_capacity"] = ",".join(sorted(n + unit for n, unit in capacities))
    pack = re.search(r"\b(?:pack of|set of)\s*(\d+)\b|\b(\d+)\s*[- ]?\s*(?:pack|pk)\b", title)
    if pack:
        result.setdefault("pack_quantity", pack.group(1) or pack.group(2))
    elif re.search(r"\b(single|single item)\b", title):
        result.setdefault("pack_quantity", "1")
    if p.get("bundle_components") or re.search(r"\b(bundle|kit|multipack)\b", title):
        result["bundle"] = "yes"
    if p.get("bundle_components"):
        result["bundle_components"] = ",".join(sorted(_text(x) for x in p["bundle_components"]))
    return result


def classify_match(a: Product | dict, b: Product | dict, *, threshold: float = 0.8,
                   publisher_aliases: dict[str, list[str]] | None = None) -> MatchDecision:
    """Classify a pair. Conflicts always override agreeing identifiers."""
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    a, b = _record(a), _record(b)
    aa, ab = normalized_attributes(a), normalized_attributes(b)
    conflicts = [f"{k}: {aa[k]} != {ab[k]}" for k in sorted(aa.keys() & ab.keys()) if aa[k] != ab[k]]
    missing = sorted(aa.keys() ^ ab.keys())
    brand_a, brand_b = _text(a.get("vendor") or a.get("brand")), _text(b.get("vendor") or b.get("brand"))
    if a.get("condition") and b.get("condition") and _text(a["condition"]) != _text(b["condition"]):
        conflicts.append("condition differs")
    evidence = []
    ga = _gtin(a.get("gtin") or a.get("ean") or a.get("upc"))
    gb = _gtin(b.get("gtin") or b.get("ean") or b.get("upc"))
    approved = False
    if ga and ga == gb and publisher_aliases:
        for identifier, publishers in publisher_aliases.items():
            if _gtin(identifier) == ga:
                names = {_text(name) for name in publishers}
                approved = bool(brand_a and brand_b and brand_a in names and brand_b in names)
                break
    if brand_a and brand_b and brand_a != brand_b:
        if approved:
            evidence.append("explicit GTIN-scoped publisher alias approved")
        else:
            conflicts.append("brand differs")
    if ga and gb:
        if ga == gb:
            evidence.append("validated GTIN agrees")
            for side, record in (("a", a), ("b", b)):
                raw = record.get("raw_data") or {}
                if raw.get("_identifier_normalization"):
                    evidence.append(f"supplier UPC leading-zero policy applied ({side})")
                for source in raw.get("_identifier_sources", []):
                    source_gtin = _gtin(source.get("value"))
                    if not source_gtin:
                        for note in raw.get("_identifier_normalization", []):
                            if str(note.get("source_barcode")) == str(source.get("value")) and note.get("variant_id") == source.get("variant_id"):
                                source_gtin = _gtin(note.get("normalized_gtin"))
                                break
                    if source_gtin == ga:
                        evidence.append(f"GTIN source ({side}): {source.get('url')}")
        else:
            conflicts.append("GTIN differs")
    scope_a, scope_b = supplier_scope(str(a.get("supplier_id") or "")), supplier_scope(str(b.get("supplier_id") or ""))
    if scope_a and scope_a == scope_b and a.get("external_id") and b.get("external_id"):
        if a.get("platform", "generic") == b.get("platform", "generic") and str(a["external_id"]) != str(b["external_id"]):
            conflicts.append("supplier source ID differs")
    for key in ("canonical_product_id", "external_id", "sku"):
        if a.get(key) and b.get(key) and str(a[key]).strip() == str(b[key]).strip():
            if scope_a and scope_a == scope_b:
                if key != "external_id" or a.get("platform", "generic") == b.get("platform", "generic"):
                    evidence.append(f"supplier-scoped {key} agrees")
    ma, mb = _text(a.get("mpn")), _text(b.get("mpn"))
    if ma and mb and brand_a and brand_a == brand_b:
        if ma == mb:
            evidence.append("brand and MPN agree")
        else:
            conflicts.append("MPN differs")
    ta, tb = _text(a.get("title")), _text(b.get("title"))
    similarity = title_similarity(ta, tb) if ta and tb else 0.0
    def family_title(title: str) -> str:
        title = re.sub(r"\b\d+(?:\.\d+)?\s*(?:gb|tb|mb|ml|kg|litres?|liters?)\b", "", title)
        title = re.sub(r"\b(?:pack of|set of)\s*\d+\b|\b\d+\s*[- ]?\s*(?:pack|pk)\b|\bsingle(?: item)?\b", "", title)
        return " ".join(title.split())
    fa, fb = family_title(ta), family_title(tb)
    family_similarity = title_similarity(fa, fb) if fa and fb else 0.0
    related = bool(evidence) or max(similarity, family_similarity) >= threshold
    if not related:
        # Category alone is too broad to suggest interchangeability. Require
        # an explicit shared purpose or compatibility attribute as well.
        category_a = a.get("product_type") or a.get("category_path")
        category_b = b.get("product_type") or b.get("category_path")
        shared_use = [key for key in ("purpose", "compatibility") if aa.get(key) and aa.get(key) == ab.get(key)]
        if category_a and _text(category_a) == _text(category_b) and shared_use:
            return MatchDecision(MatchRelation.SUBSTITUTE, 0.4, ["category agrees", "shared " + ", ".join(shared_use)], conflicts, True)
        return MatchDecision(MatchRelation.UNMATCHED, 0.0, [], conflicts)
    # A missing pack cue means unknown, never an assumed single item.
    pack_conflict = any(c.startswith(("pack_quantity:", "bundle_components:")) for c in conflicts)
    if pack_conflict or aa.get("bundle") != ab.get("bundle"):
        return MatchDecision(MatchRelation.BUNDLE, 0.7, evidence or ["title candidate"], conflicts +
                             (["bundle composition differs or unknown"] if not pack_conflict else []), True)
    if conflicts:
        variant_keys = {"memory", "storage", "capacity", "title_capacity", "color", "size"}
        variant_conflict = any(c.split(":")[0] in variant_keys for c in conflicts)
        relation = MatchRelation.VARIANT if variant_conflict and "brand differs" not in conflicts else MatchRelation.UNCERTAIN
        return MatchDecision(relation, 0.7, evidence or ["title candidate"], conflicts, True)
    if missing:
        return MatchDecision(MatchRelation.UNCERTAIN, 0.5, evidence or ["title candidate"],
                             ["missing attributes: " + ", ".join(missing)], True)
    if evidence:
        return MatchDecision(MatchRelation.EXACT, 1.0, evidence)
    # Exact normalized titles/attributes remain review candidates without identifiers.
    return MatchDecision(MatchRelation.UNCERTAIN, similarity, ["normalized title/attribute candidate"], [], True)


SemanticCandidates = Callable[[dict, list[dict]], Iterable[int]]


def match_products(products_a: list[Product | dict], products_b: list[Product | dict], *,
                   threshold: float = 0.8, publisher_aliases: dict[str, list[str]] | None = None,
                   semantic_candidates: SemanticCandidates | None = None) -> list[MatchDecision]:
    """Report all related candidates and unmatched records, reserving unique exact pairs.

    Ambiguous exact edges require review. Semantic callbacks run only for sources
    lacking rule candidates and return target indices, not authorization decisions.
    """
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    report = []
    for i, a in enumerate(products_a):
        candidates = []
        for j, b in enumerate(products_b):
            decision = classify_match(a, b, threshold=threshold, publisher_aliases=publisher_aliases)
            if decision.relation != MatchRelation.UNMATCHED:
                decision.index_a, decision.index_b = i, j
                candidates.append(decision)
        exact = [d for d in candidates if d.relation == MatchRelation.EXACT]
        if exact:
            candidates = exact
        if not candidates and semantic_candidates:
            for j in dict.fromkeys(semantic_candidates(_record(a), [_record(b) for b in products_b])):
                if not isinstance(j, int) or not 0 <= j < len(products_b):
                    raise ValueError("Semantic candidate index outside target catalog")
                d = classify_match(a, products_b[j], threshold=threshold, publisher_aliases=publisher_aliases)
                if d.relation == MatchRelation.UNMATCHED:
                    d = MatchDecision(MatchRelation.UNCERTAIN, 0.0, ["semantic candidate only"], d.conflicts, True)
                d.index_a, d.index_b, d.candidate_method = i, j, "semantic"
                candidates.append(d)
        report.extend(candidates or [MatchDecision(MatchRelation.UNMATCHED, 0.0, index_a=i)])
    exact = [d for d in report if d.relation == MatchRelation.EXACT]
    for d in exact:
        if sum(x.index_a == d.index_a for x in exact) > 1 or sum(x.index_b == d.index_b for x in exact) > 1:
            d.relation, d.needs_review = MatchRelation.UNCERTAIN, True
            d.conflicts.append("ambiguous exact candidates")
    targeted = {d.index_b for d in report if d.index_b is not None}
    report.extend(MatchDecision(MatchRelation.UNMATCHED, 0.0, index_b=j)
                  for j in range(len(products_b)) if j not in targeted)
    return report
