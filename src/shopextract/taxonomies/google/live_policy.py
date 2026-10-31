"""Read-only managed-network preflight; never grants or changes access."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime, timezone


def policy_denial(url):
    path = Path('/etc/codex/network-policy.json')
    try:
        raw = path.read_bytes()
        if len(raw) > 65536:
            return None
        value = json.loads(raw)
        policy = value['http_network_policy']
        if type(value['version']) is not int or value['version'] != 1 or policy['type'] != 'restricted':
            return None
        rules = policy['egress_rules']
        if not isinstance(rules, list) or any(not isinstance(r, dict) or set(r) != {'host'} or
            not isinstance(r['host'], str) or any(c in r['host'] for c in '*:/') for r in rules):
            return None  # Unsupported rules are not evidence of a denial or grant.
        host = urlsplit(url).hostname
        if host in {rule['host'].lower() for rule in rules}:
            return None  # Presence is not a promise of successful authorization.
        return dict(reason='host_not_allowed', host=host, policy_path=str(path),
                    sha256=hashlib.sha256(raw).hexdigest(), observed_at=datetime.now(timezone.utc).isoformat())
    except (OSError, ValueError, TypeError, KeyError):
        return None
