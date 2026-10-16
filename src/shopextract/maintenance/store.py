"""Local transactional jobs, immutable evidence and conservative external intents."""
from __future__ import annotations

import contextlib
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from ..categories.contracts import CategoryPolicySnapshot, CategoryRuntimeConfig
from uuid import uuid4

from .contracts import Budgets, Goal, MaintenanceError
from .profiles import CategoryProfile, FieldRule, profile

SHIPPED = ('hardware-v1', 'footwear-v1', 'generic-v1')
STATES = {'queued', 'running', 'paused', 'partial', 'completed', 'cancelled', 'failed'}


def packed(value):
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                          separators=(',', ':'))
    except (TypeError, ValueError, RecursionError) as error:
        raise MaintenanceError('invalid_argument', 'Finite JSON values required') from error


def digest(value):
    return hashlib.sha256(packed(value).encode()).hexdigest()


def _profile_record(value):
    if not isinstance(value, CategoryProfile) or not isinstance(value.name, str) or not value.name.endswith('-v1'):
        raise MaintenanceError('invalid_argument', 'Profile must have a supported versioned name')
    result = {'name': value.name, 'fields': {}}
    for path, rule in value.fields.items():
        if (not isinstance(path, str) or not path or '*' in path
            or (path not in {'description', 'title', 'price', 'currency'} and
                not (path.startswith('attributes/') and len(path.split('/')) == 2 and path[11:]))):
            raise MaintenanceError('invalid_argument', 'Unsupported profile field')
        # Reject malformed JSON Pointer escapes rather than accidentally alias keys.
        import re
        if re.search(r'~(?![01])', path):
            raise MaintenanceError('invalid_argument', 'Malformed field escape')
        if not isinstance(rule, FieldRule):
            raise MaintenanceError('invalid_argument', 'Invalid field rule')
        try:
            item = asdict(rule)
        except TypeError as error:
            raise MaintenanceError('invalid_argument', 'Invalid field rule') from error
        allowed = {'text': {'exact'}, 'decimal': {'decimal'}, 'mass': {'mass_kg'}}
        if (item.get('kind') not in allowed or item.get('normalization') not in allowed[item['kind']]
            or item.get('role') not in {'comparable', 'identity_variant', 'price_context'}):
            raise MaintenanceError('invalid_argument', 'Unsupported field rule')
        result['fields'][path] = item
    if not result['fields']:
        raise MaintenanceError('invalid_argument', 'Empty category profile')
    return result


class MaintenanceStore:
    def __init__(self, path, *, custom_profiles: Mapping[str, CategoryProfile] | None = None,
                 category_config: CategoryRuntimeConfig | None = None):
        from ..categories.contracts import CategoryPolicySnapshot
        self._category_creation = CategoryPolicySnapshot('legacy')
        if category_config is not None:
            from ..categories.config import runtime_record
            from ..categories._codec import canonical
            from ..categories.maintenance import category_policy_digest
            self._category_creation = CategoryPolicySnapshot('enabled', 1,
                canonical(runtime_record(category_config)), category_policy_digest(category_config))
        self.path = str(Path(path).expanduser().resolve())
        self._lock = None
        self._db = None
        self.registry = {name: _profile_record(profile(name)) for name in SHIPPED}
        for name, configured in (custom_profiles or {}).items():
            value = _profile_record(configured)
            if name in self.registry or name != value['name']:
                raise MaintenanceError('invalid_argument', 'Profile registry name collision')
            self.registry[name] = value
        if category_config is not None and any(name not in self.registry for _,name in category_config.profile_bindings):
            raise MaintenanceError('invalid_argument','Unknown category profile binding')

    def _connect(self):
        if self._db is None:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            try:
                db = sqlite3.connect(self.path, timeout=1, isolation_level=None)
                db.row_factory = sqlite3.Row
                db.execute('PRAGMA foreign_keys=ON')
                version = db.execute('PRAGMA user_version').fetchone()[0]
                if version not in (0, 1, 2):
                    db.close()
                    raise MaintenanceError('unsupported_version')
                if version == 0:
                    if self._lock is None:
                        db.close()
                        raise MaintenanceError('not_found')
                    # Refuse an unrelated SQLite database rather than adding tables.
                    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone():
                        db.close()
                        raise MaintenanceError('unsupported_version')
                    db.executescript('''BEGIN IMMEDIATE;
                    CREATE TABLE jobs(id TEXT PRIMARY KEY, goal TEXT NOT NULL, fingerprint TEXT NOT NULL,
                      profiles TEXT NOT NULL, state TEXT NOT NULL, cancel_requested INTEGER NOT NULL DEFAULT 0,
                      stop_reason TEXT, coverage TEXT NOT NULL DEFAULT '{}');
                    CREATE TABLE steps(job TEXT REFERENCES jobs(id), id TEXT, ordinal INTEGER, kind TEXT,
                      state TEXT NOT NULL DEFAULT 'pending', result TEXT, PRIMARY KEY(job,id));
                    CREATE TABLE attempts(id TEXT PRIMARY KEY, job TEXT, step TEXT, number INTEGER,
                      state TEXT NOT NULL, reserved TEXT NOT NULL, usage TEXT, error TEXT, retry_at TEXT,
                      FOREIGN KEY(job,step) REFERENCES steps(job,id));
                    CREATE TABLE evidence(job TEXT REFERENCES jobs(id), id TEXT, payload TEXT NOT NULL,
                      PRIMARY KEY(job,id));
                    CREATE TABLE findings(job TEXT REFERENCES jobs(id), id TEXT, ordinal INTEGER,
                      payload TEXT NOT NULL, PRIMARY KEY(job,id));
                    CREATE TABLE advisories(job TEXT REFERENCES jobs(id), step TEXT, number INTEGER,
                      attempt TEXT UNIQUE, finding TEXT NOT NULL, payload TEXT NOT NULL,
                      PRIMARY KEY(job,step,number));
                    CREATE TABLE cache(key TEXT PRIMARY KEY, payload TEXT NOT NULL, expires TEXT NOT NULL,
                      bytes INTEGER NOT NULL);
                    PRAGMA user_version=1; COMMIT;''')
                if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='advisories'").fetchone():
                    db.close()
                    raise MaintenanceError('unsupported_version')
                self._db = db
            except sqlite3.Error as error:
                raise MaintenanceError('storage_error') from error
        return self._db

    @contextlib.contextmanager
    def _transaction(self, *, control=False):
        if not control and self._lock is None:
            raise MaintenanceError('owner_busy', 'Execution ownership required')
        db = self._connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.execute('COMMIT')
        except BaseException as error:
            if db.in_transaction:
                db.execute('ROLLBACK')
            if isinstance(error, sqlite3.Error):
                raise MaintenanceError('storage_error') from error
            raise

    @contextlib.contextmanager
    def _temporary_owner(self):
        owned = self._lock is not None
        if not owned:
            self.acquire()
        try:
            yield
        finally:
            if not owned:
                self.release()

    def acquire(self):
        if self._lock is not None:
            return
        try:
            import fcntl
        except ImportError as error:
            raise MaintenanceError('unsupported_version', 'POSIX flock required') from error
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path + '.lock', os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            os.close(fd)
            raise MaintenanceError('owner_busy') from error
        self._lock = fd
        try:
            with self._transaction() as db:
                db.execute("UPDATE jobs SET state='paused' WHERE state='running'")
                db.execute("UPDATE attempts SET state='unknown' WHERE state='intent'")
        except BaseException:
            self.release()
            raise

    def release(self):
        if self._lock is not None:
            import fcntl
            fcntl.flock(self._lock, fcntl.LOCK_UN)
            os.close(self._lock)
            self._lock = None

    def close(self):
        self.release()
        if self._db is not None:
            self._db.close()
            self._db = None

    def _job(self, job_id):
        row = self._connect().execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None:
            raise MaintenanceError('not_found')
        return row

    def _validated(self, goal):
        from ..tools.security import normalized
        if not isinstance(goal, Goal) or goal.schema_version != '1.0':
            raise MaintenanceError('unsupported_version')
        if goal.baseline_mode not in {'supplied', 'captured'}:
            raise MaintenanceError('invalid_argument')
        if (not isinstance(goal.baseline, (list, tuple)) or not isinstance(goal.product_urls, (list, tuple))
            or not isinstance(goal.fields, (list, tuple)) or any(not isinstance(k, str) for k in goal.fields)
            or not isinstance(goal.profiles, Mapping)
            or any(not isinstance(k, str) or not isinstance(v, str) for k, v in goal.profiles.items())):
            raise MaintenanceError('invalid_argument')
        try:
            deadline = datetime.fromisoformat(goal.deadline.replace('Z', '+00:00'))
            if deadline.tzinfo is None:
                raise ValueError()
            origin = normalized(goal.supplier_origin)[1]
            if normalized(goal.supplier_origin)[0].rstrip('/') != origin:
                raise ValueError()
            urls = [normalized(url)[0] for url in goal.product_urls]
            if len(set(urls)) != len(urls) or any(normalized(url)[1] != origin for url in urls):
                raise ValueError()
        except (ValueError, AttributeError, TypeError) as error:
            raise MaintenanceError('invalid_argument') from error
        except Exception as error:
            raise MaintenanceError('permission_denied') from error
        if not isinstance(goal.budgets, Budgets):
            raise MaintenanceError('invalid_argument')
        limits = asdict(goal.budgets)
        maximum = {'requests': 1000, 'products': 1000, 'tokens': 1_000_000,
                   'cost_micros': 1_000_000_000, 'input_bytes': 256 * 1024,
                   'evidence_bytes': 16 * 1024 * 1024, 'report_bytes': 2 * 1024 * 1024,
                   'attempt_seconds': 120}
        for key, val in limits.items():
            if key == 'attempt_seconds':
                valid = type(val) in (int, float) and math.isfinite(val) and 0 < val <= maximum[key]
            else:
                valid = type(val) is int and 0 <= val <= maximum[key]
            if not valid:
                raise MaintenanceError('invalid_argument')
        if (type(goal.freshness_seconds) not in (int, float) or not math.isfinite(goal.freshness_seconds)
            or not 0 <= goal.freshness_seconds <= 86400):
            raise MaintenanceError('invalid_argument')
        if not goal.fields or len(set(goal.fields)) != len(goal.fields):
            raise MaintenanceError('invalid_argument')
        keys = []
        for index, record in enumerate(goal.baseline):
            if not isinstance(record, dict):
                raise MaintenanceError('invalid_argument')
            if goal.baseline_mode == 'captured':
                from .._portable import product_from_record
                try:
                    if self._category_creation.mode == 'enabled':
                        from ..categories.portable import categorized_product_from_record
                        captured = categorized_product_from_record(record).product
                    else:
                        captured = product_from_record(record)
                except (ValueError, TypeError) as error:
                    raise MaintenanceError('invalid_argument', 'Invalid captured baseline') from error
                key = str(captured.external_id or captured.canonical_product_id or index)
            else:
                key = str(record.get('external_id') or record.get('canonical_product_id') or index)
            if key in keys:
                raise MaintenanceError('invalid_argument', 'Duplicate baseline key')
            keys.append(key)
        if len(keys) > 1000 or len(urls) > 1000 or set(goal.profiles) - set(keys):
            raise MaintenanceError('invalid_argument')
        allowed_fields = {path for definition in self.registry.values() for path in definition['fields']}
        if any(path not in allowed_fields for path in goal.fields):
            raise MaintenanceError('invalid_argument', 'Unsupported selected field')
        selected = {}
        for key, name in goal.profiles.items():
            if name not in self.registry:
                raise MaintenanceError('invalid_argument', 'Unknown profile')
            definition = self.registry[name]
            if any(path not in definition['fields'] for path in goal.fields):
                raise MaintenanceError('invalid_argument', 'Unsupported selected field')
            selected[name] = definition
        record = asdict(goal)
        record['product_urls'] = urls
        record['baseline'] = list(goal.baseline)
        record['fields'] = list(goal.fields)
        record['deadline'] = deadline.astimezone(timezone.utc).isoformat()
        record['supplier_origin'] = origin
        # Exact JSON roundtrip copies caller mappings before defaults reconstruction.
        serialized = packed(record)
        if len(serialized.encode()) > limits['input_bytes']:
            raise MaintenanceError('invalid_argument', 'Input byte cap exceeded')
        frozen = json.loads(packed(selected))
        return json.loads(serialized), frozen

    def create(self, goal: Goal) -> str:
        record, definitions = self._validated(goal)
        key = uuid4().hex
        with self._temporary_owner(), self._transaction() as db:
            policy = self._category_creation
            fingerprint = {'goal': record, 'profiles': definitions}
            if policy.mode == 'enabled':
                db.execute('CREATE TABLE IF NOT EXISTS category_job_policies (job TEXT PRIMARY KEY REFERENCES jobs(id), mode TEXT NOT NULL, schema_version INTEGER NOT NULL, config_json TEXT, config_digest TEXT)')
                db.execute('PRAGMA user_version=2')
                fingerprint['category_policy'] = asdict(policy)
            db.execute('INSERT INTO jobs(id,goal,fingerprint,profiles,state) VALUES(?,?,?,?,?)',
                (key, packed(record), digest(fingerprint), packed(definitions), 'queued'))
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='category_job_policies'").fetchone():
                db.execute('INSERT INTO category_job_policies VALUES(?,?,?,?,?)',
                    (key,policy.mode,policy.schema_version,policy.config_json,policy.config_digest))
        return key

    def category_policy(self, job_id: str) -> CategoryPolicySnapshot:
        """Read exact creation-time mode/config; missing legacy policy never enables it."""
        from ..categories.contracts import CategoryPolicySnapshot
        self._job(job_id)
        db = self._connect()
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='category_job_policies'").fetchone():
            return CategoryPolicySnapshot('legacy')
        row = db.execute('SELECT * FROM category_job_policies WHERE job=?',(job_id,)).fetchone()
        if row is None:
            return CategoryPolicySnapshot('legacy')
        snapshot = CategoryPolicySnapshot(row['mode'],row['schema_version'],row['config_json'],row['config_digest'])
        if snapshot.schema_version != 1:
            raise MaintenanceError('category_policy_mismatch')
        if snapshot.mode == 'legacy':
            if snapshot.config_json is not None or snapshot.config_digest is not None:
                raise MaintenanceError('category_policy_mismatch')
            return snapshot
        if snapshot.mode != 'enabled' or snapshot.schema_version != 1:
            raise MaintenanceError('category_policy_mismatch')
        try:
            from ..categories.config import runtime_from_record
            from ..categories._codec import canonical
            from ..categories.maintenance import category_policy_digest
            if not isinstance(snapshot.config_json,str) or len(snapshot.config_json.encode()) > 262144:
                raise ValueError()
            record = json.loads(snapshot.config_json)
            config = runtime_from_record(record)
            if canonical(record) != snapshot.config_json or category_policy_digest(config) != snapshot.config_digest:
                raise ValueError()
        except (ValueError,TypeError,KeyError) as error:
            raise MaintenanceError('category_policy_mismatch') from error
        return snapshot

    def goal(self, job_id):
        return json.loads(self._job(job_id)['goal'])

    def validate_profiles(self, job_id):
        definitions = json.loads(self._job(job_id)['profiles'])
        if any(self.registry.get(name) != definition for name, definition in definitions.items()):
            raise MaintenanceError('profile_mismatch')
        return definitions

    def status(self, job_id: str) -> dict:
        row = self._job(job_id)
        return {'job_id': job_id, 'state': row['state'], 'stop_reason': row['stop_reason'],
            'cancel_requested': bool(row['cancel_requested']), 'goal_fingerprint': row['fingerprint'],
            'profile_definitions': json.loads(row['profiles'])}

    def usage(self, job_id):
        self._job(job_id)
        usage = {'requests': 0, 'tokens': 0, 'cost_micros': 0, 'reserved_tokens': 0,
                 'reserved_cost_micros': 0, 'unknown_requests': 0, 'violations': 0}
        for row in self._connect().execute('SELECT * FROM attempts WHERE job=?', (job_id,)):
            if row['state'] == 'violation':
                usage['violations'] += 1
            reserved = json.loads(row['reserved'])
            settled = json.loads(row['usage']) if row['usage'] is not None else None
            values = settled if settled is not None else reserved
            for key in ('requests', 'tokens', 'cost_micros'):
                usage[key] += values.get(key, 0)
            if settled is None:
                usage['reserved_tokens'] += reserved.get('tokens', 0)
                usage['reserved_cost_micros'] += reserved.get('cost_micros', 0)
            if row['state'] == 'unknown':
                usage['unknown_requests'] += reserved.get('requests', 0)
        return usage

    def steps(self, job_id):
        self._job(job_id)
        return [dict(row, result=json.loads(row['result']) if row['result'] else None)
                for row in self._connect().execute('SELECT * FROM steps WHERE job=? ORDER BY ordinal', (job_id,))]

    def add_steps(self, job_id, steps):
        with self._transaction() as db:
            self._job(job_id)
            for ordinal, (step_id, kind) in enumerate(steps):
                old = db.execute('SELECT kind,ordinal FROM steps WHERE job=? AND id=?', (job_id, step_id)).fetchone()
                if old and (old['kind'] != kind or old['ordinal'] != ordinal):
                    raise MaintenanceError('invalid_state')
                db.execute('INSERT OR IGNORE INTO steps(job,id,ordinal,kind) VALUES(?,?,?,?)',
                           (job_id, step_id, ordinal, kind))

    def add_step(self, job_id, step_id, kind):
        """Append a discovered physical boundary, or return its immutable identity."""
        with self._transaction() as db:
            self._job(job_id)
            old = db.execute('SELECT kind FROM steps WHERE job=? AND id=?', (job_id, step_id)).fetchone()
            if old:
                if old['kind'] != kind:
                    raise MaintenanceError('invalid_state')
                return
            ordinal = db.execute('SELECT COALESCE(MAX(ordinal),-1)+1 FROM steps WHERE job=?', (job_id,)).fetchone()[0]
            db.execute('INSERT INTO steps(job,id,ordinal,kind) VALUES(?,?,?,?)', (job_id, step_id, ordinal, kind))

    def begin(self, job_id, *, now):
        if self._lock is None:
            raise MaintenanceError('owner_busy')
        row = self._job(job_id)
        if row['state'] in {'cancelled', 'failed'}:
            raise MaintenanceError('invalid_state')
        if row['state'] == 'completed':
            return False
        self.validate_profiles(job_id)
        if row['state'] == 'running':
            raise MaintenanceError('already_running')
        goal = json.loads(row['goal'])
        if now >= datetime.fromisoformat(goal['deadline']):
            self.finish(job_id, 'partial', 'deadline')
            return False
        with self._transaction() as db:
            self.check_cancel(job_id)
            db.execute("UPDATE jobs SET state='running',stop_reason=NULL WHERE id=?", (job_id,))
        return True

    def request_cancel(self, job_id: str) -> dict:
        with self._transaction(control=True) as db:
            row = self._job(job_id)
            if row['state'] not in {'completed', 'cancelled', 'failed'}:
                state = 'running' if row['state'] == 'running' else 'cancelled'
                db.execute('UPDATE jobs SET cancel_requested=1,state=? WHERE id=?', (state, job_id))
        return self.status(job_id)

    def check_cancel(self, job_id):
        if self._job(job_id)['cancel_requested']:
            raise MaintenanceError('cancelled')

    def finish(self, job_id, state, reason=None, coverage=None):
        if state not in STATES:
            raise MaintenanceError('invalid_argument')
        with self._transaction() as db:
            row = self._job(job_id)
            if row['state'] in {'completed', 'cancelled', 'failed'}:
                return
            if row['cancel_requested']:
                state, reason = 'cancelled', 'cancelled'
            db.execute('UPDATE jobs SET state=?,stop_reason=?,coverage=? WHERE id=?',
                (state, reason, packed(coverage) if coverage is not None else row['coverage'], job_id))

    def reserve(self, job_id, step_id, amount, *, now, explicit_retry=False):
        """One reservation is one physical source/model boundary attempt."""
        with self._transaction() as db:
            self.check_cancel(job_id)
            job = self._job(job_id)
            goal = json.loads(job['goal'])
            if job['state'] != 'running':
                raise MaintenanceError('invalid_state')
            if now >= datetime.fromisoformat(goal['deadline']):
                raise MaintenanceError('deadline')
            step = db.execute('SELECT * FROM steps WHERE job=? AND id=?', (job_id, step_id)).fetchone()
            if not step or (step['state'] == 'committed' and not (explicit_retry and step['kind'].startswith('advisor:'))):
                raise MaintenanceError('invalid_state')
            previous = list(db.execute('SELECT * FROM attempts WHERE job=? AND step=? ORDER BY number', (job_id, step_id)))
            if len(previous) >= 2:
                raise MaintenanceError('retry_exhausted')
            if any(row['state'] in {'intent', 'unknown'} for row in previous) and not explicit_retry:
                raise MaintenanceError('outcome_unknown')
            if previous:
                last = previous[-1]
                if last['state'] == 'failed' and last['error'] not in {'timeout', 'source_error', 'transient'}:
                    raise MaintenanceError('retry_exhausted')
                if last['retry_at'] and now < datetime.fromisoformat(last['retry_at']):
                    raise MaintenanceError('retry_wait')
            totals = self.usage(job_id)
            for key, value in amount.items():
                if key not in {'requests', 'tokens', 'cost_micros'} or type(value) is not int or value < 0:
                    raise MaintenanceError('invalid_argument')
                if totals[key] + value > goal['budgets'][key]:
                    raise MaintenanceError({'requests': 'request_budget', 'tokens': 'token_budget',
                                            'cost_micros': 'cost_budget'}[key])
            key = uuid4().hex
            db.execute('INSERT INTO attempts(id,job,step,number,state,reserved) VALUES(?,?,?,?,?,?)',
                (key, job_id, step_id, len(previous) + 1, 'intent', packed(amount)))
            return key

    def checkpoint(self, job_id, step_id, result, *, evidence=(), findings=(), settlements=None, violations=(), advisories=()):
        result_json = packed(result)
        with self._transaction() as db:
            self.check_cancel(job_id)
            job = self._job(job_id)
            if job['state'] != 'running':
                raise MaintenanceError('invalid_state')
            step = db.execute('SELECT * FROM steps WHERE job=? AND id=?', (job_id, step_id)).fetchone()
            if step is None:
                raise MaintenanceError('not_found')
            if step['state'] == 'committed':
                if step['result'] != result_json:
                    raise MaintenanceError('invalid_state')
                if not settlements and not advisories:
                    return
            budgets = json.loads(job['goal'])['budgets']
            for value in evidence:
                encoded = packed(value)
                old = db.execute('SELECT payload FROM evidence WHERE job=? AND id=?',
                                 (job_id, value['evidence_id'])).fetchone()
                if old and old['payload'] != encoded:
                    raise MaintenanceError('invalid_state', 'Immutable evidence collision')
                db.execute('INSERT OR IGNORE INTO evidence VALUES(?,?,?)', (job_id, value['evidence_id'], encoded))
            retained_bytes = sum(len(row[0].encode()) for row in db.execute('SELECT payload FROM evidence WHERE job=?', (job_id,)))
            retained_bytes += sum(len(row[0].encode()) for row in db.execute('SELECT result FROM steps WHERE job=? AND result IS NOT NULL AND id!=?', (job_id, step_id)))
            retained_bytes += len(result_json.encode())
            if retained_bytes > budgets['evidence_bytes']:
                raise MaintenanceError('evidence_budget')
            for value in findings:
                encoded = packed(value)
                old = db.execute('SELECT payload FROM findings WHERE job=? AND id=?', (job_id, value['finding_id'])).fetchone()
                if old and old['payload'] != encoded:
                    raise MaintenanceError('invalid_state', 'Immutable finding collision')
                ordinal = value.get('ordinal', db.execute('SELECT COUNT(*) FROM findings WHERE job=?', (job_id,)).fetchone()[0])
                db.execute('INSERT OR IGNORE INTO findings VALUES(?,?,?,?)', (job_id, value['finding_id'], ordinal, encoded))
            if sum(len(row[0].encode()) for row in db.execute('SELECT payload FROM findings WHERE job=?', (job_id,))) > budgets['report_bytes']:
                raise MaintenanceError('report_budget')
            for publication in advisories:
                child = db.execute('SELECT * FROM steps WHERE job=? AND id=?', (job_id, publication['step'])).fetchone()
                if child is None or child['kind'] != 'advisor:' + step_id:
                    raise MaintenanceError('invalid_argument')
                attempt_id = publication.get('attempt_id')
                if attempt_id:
                    attempt = db.execute('SELECT * FROM attempts WHERE id=? AND job=? AND step=?',
                        (attempt_id, job_id, publication['step'])).fetchone()
                    if attempt is None:
                        raise MaintenanceError('invalid_argument')
                    number = attempt['number']
                else:
                    number = 0  # cached/skipped advice has no external attempt
                value = packed(publication['payload'])
                previous = db.execute('SELECT payload FROM advisories WHERE job=? AND step=? AND number=?',
                    (job_id, publication['step'], number)).fetchone()
                if previous and previous['payload'] != value:
                    raise MaintenanceError('invalid_state', 'Immutable advisory collision')
                db.execute('INSERT OR IGNORE INTO advisories VALUES(?,?,?,?,?,?)',
                    (job_id, publication['step'], number, attempt_id, publication['finding_id'], value))
                db.execute("UPDATE steps SET state='committed' WHERE job=? AND id=?", (job_id, publication['step']))
            retained_advice = sum(len(row[0].encode()) for row in db.execute('SELECT payload FROM advisories WHERE job=?', (job_id,)))
            if retained_advice + retained_bytes > budgets['evidence_bytes']:
                raise MaintenanceError('evidence_budget')
            composed_bytes = sum(len(packed(value).encode()) for value in self._findings(job_id))
            if composed_bytes > budgets['report_bytes']:
                raise MaintenanceError('report_budget')
            for attempt_id, actual in (settlements or {}).items():
                attempt = db.execute('SELECT a.*,s.kind AS step_kind FROM attempts a JOIN steps s ON s.job=a.job AND s.id=a.step WHERE a.id=? AND a.job=?',
                                     (attempt_id, job_id)).fetchone()
                if attempt is not None and attempt['step'] != step_id and attempt['step_kind'] not in {'wire:' + step_id, 'advisor:' + step_id}:
                    raise MaintenanceError('invalid_argument', 'Settlement outside checkpoint ownership')
                if attempt is None:
                    raise MaintenanceError('invalid_argument')
                if actual is None:
                    db.execute("UPDATE attempts SET state='unknown' WHERE id=?", (attempt_id,))
                    continue
                bound = json.loads(attempt['reserved'])
                if any(k not in bound or type(v) is not int or v < 0 for k, v in actual.items()):
                    raise MaintenanceError('budget_violation')
                overrun = any(v > bound[k] for k, v in actual.items())
                if overrun and (attempt_id not in violations or attempt['step_kind'] != 'advisor:' + step_id):
                    raise MaintenanceError('budget_violation')
                # Omitted dimensions retain reservation, never implicitly become free.
                settled = dict(bound, **actual)
                db.execute('UPDATE attempts SET state=?,usage=? WHERE id=?',
                           ('violation' if overrun else 'settled', packed(settled), attempt_id))
            for attempt_id in (settlements or {}):
                db.execute("UPDATE steps SET state='committed' WHERE job=? AND id=(SELECT step FROM attempts WHERE id=?) AND kind IN (?,?)",
                           (job_id, attempt_id, 'wire:' + step_id, 'advisor:' + step_id))
            db.execute("UPDATE steps SET state='committed',result=? WHERE job=? AND id=?", (result_json, job_id, step_id))

    def fail_attempt(self, attempt_id, code, *, known=True, retry_at=None):
        with self._transaction() as db:
            attempt = db.execute('SELECT * FROM attempts WHERE id=?', (attempt_id,)).fetchone()
            if attempt is None:
                raise MaintenanceError('not_found')
            db.execute('UPDATE attempts SET state=?,error=?,usage=?,retry_at=? WHERE id=?',
                ('failed' if known else 'unknown', code, attempt['reserved'] if known else None,
                 retry_at.isoformat() if retry_at is not None else None, attempt_id))

    def report(self, job_id: str, *, offset: int = 0, limit: int = 100) -> dict:
        if type(offset) is not int or type(limit) is not int or offset < 0 or not 1 <= limit <= 1000:
            raise MaintenanceError('invalid_argument')
        job = self._job(job_id)
        findings = self._findings(job_id)[offset:offset+limit]
        return {'schema_version': '1.0', 'job_id': job_id, 'state': job['state'],
            'stop_reason': job['stop_reason'], 'findings': findings, 'usage': self.usage(job_id),
            'coverage': json.loads(job['coverage']),
            'pending_steps': [row['id'] for row in self.steps(job_id) if row['state'] != 'committed']}

    def evidence(self, job_id: str, evidence_id: str) -> dict:
        self._job(job_id)
        row = self._connect().execute('SELECT payload FROM evidence WHERE job=? AND id=?', (job_id, evidence_id)).fetchone()
        if row is None:
            raise MaintenanceError('not_found')
        return json.loads(row[0])


    def attempts(self, job_id, step_id):
        self._job(job_id)
        return [dict(row) for row in self._connect().execute(
            'SELECT a.* FROM attempts a JOIN steps s ON a.job=s.job AND a.step=s.id '
            'WHERE a.job=? AND (a.step=? OR s.kind=?) ORDER BY a.rowid',
            (job_id, step_id, 'wire:' + step_id))]

    def cache_get(self, key, *, now):
        row = self._connect().execute('SELECT * FROM cache WHERE key=?', (key,)).fetchone()
        if row is None:
            return None
        try:
            if now >= datetime.fromisoformat(row['expires']) or len(row['payload'].encode()) > 16 * 1024 * 1024:
                return None
            value = json.loads(row['payload'])
            return value if isinstance(value, dict) and value.get('complete') is True else None
        except (ValueError, TypeError):
            return None

    def cache_put(self, key, payload, *, expires, byte_limit=16 * 1024 * 1024):
        value = packed(payload)
        size = len(value.encode())
        if payload.get('complete') is not True or size > byte_limit:
            return
        with self._transaction() as db:
            db.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?,?)', (key, value, expires.isoformat(), size))
            while db.execute('SELECT COALESCE(SUM(bytes),0) FROM cache').fetchone()[0] > byte_limit:
                db.execute('DELETE FROM cache WHERE key=(SELECT key FROM cache ORDER BY expires,key LIMIT 1)')


    def prepare_step(self, job_id, step_id, details):
        """Freeze a pending boundary's accepted model/payload policy before send."""
        encoded = packed(details)
        with self._transaction() as db:
            self.check_cancel(job_id)
            row = db.execute('SELECT * FROM steps WHERE job=? AND id=?', (job_id, step_id)).fetchone()
            if row is None or (row['state'] != 'pending' and not row['kind'].startswith('advisor:')):
                raise MaintenanceError('invalid_state')
            if row['result'] is not None and row['result'] != encoded:
                raise MaintenanceError('invalid_state', 'Boundary intent is immutable')
            db.execute('UPDATE steps SET result=? WHERE job=? AND id=?', (encoded, job_id, step_id))


    def _findings(self, job_id):
        values = [json.loads(row[0]) for row in self._connect().execute(
            'SELECT payload FROM findings WHERE job=? ORDER BY ordinal,id', (job_id,))]
        latest = {}
        for row in self._connect().execute('SELECT * FROM advisories WHERE job=? ORDER BY number', (job_id,)):
            latest[row['finding']] = json.loads(row['payload'])
        for value in values:
            if value['finding_id'] in latest:
                value['advisory'] = latest[value['finding_id']]
        return values

    def advisory_history(self, job_id, step_id):
        self._job(job_id)
        return [dict(row, payload=json.loads(row['payload'])) for row in self._connect().execute(
            'SELECT * FROM advisories WHERE job=? AND step=? ORDER BY number', (job_id, step_id))]

    def model_stop(self, job_id):
        rows = list(self._connect().execute(
            "SELECT a.* FROM attempts a JOIN steps s ON a.job=s.job AND a.step=s.id WHERE a.job=? AND s.kind LIKE 'advisor:%' ORDER BY a.number", (job_id,)))
        if any(row['state'] == 'violation' for row in rows):
            return 'budget_violation'
        latest = {row['step']: row for row in rows}
        for step, row in latest.items():
            if row['state'] in {'intent', 'unknown'}:
                history = self.advisory_history(job_id, step)
                advisory = history[-1]['payload'] if history else {}
                return 'model_usage_unknown' if advisory.get('status') == 'available' else 'model_outcome_unknown'
        return None


    def completion(self, job_id, *, source_reason=None, coverage=None, model_reason=None):
        """Evaluate all durable outcomes; an advisory success cannot finish a crawl."""
        row = self._job(job_id)
        retained = json.loads(row['coverage']) if coverage is None else coverage
        steps = self.steps(job_id)
        sources = [step for step in steps if step['kind'] in {'extract', 'discover'}]
        partial_source = any(step['state'] == 'committed' and isinstance(step['result'], dict)
                             and step['result'].get('complete') is False for step in sources)
        pending_sources = [step for step in sources if step['state'] != 'committed']
        pending_compares = any(step['kind'] == 'compare' and step['state'] != 'committed' for step in steps)
        if source_reason is None:
            if partial_source or retained.get('source_complete') is False:
                source_reason = 'source_partial'
            elif pending_sources:
                unknown = any(attempt['state'] in {'intent', 'unknown'}
                    for step in pending_sources for attempt in self.attempts(job_id, step['id']))
                source_reason = 'outcome_unknown' if unknown else 'pending_work'
            elif pending_compares:
                source_reason = 'pending_work'
            elif retained.get('processed_products', 0) < retained.get('baseline_count', 0):
                source_reason = 'product_budget'
        reason = source_reason or self.model_stop(job_id) or model_reason
        return ('partial' if reason else 'completed'), reason, retained
