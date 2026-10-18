"""One deterministic logical catalog identity independent of source paths/time."""
import hashlib
import json

NAMESPACE = 'shopify:standard_product_taxonomy'


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def fingerprint(payload):
    return hashlib.sha256(canonical(payload)).hexdigest()


def registry_version(release, content_fingerprint):
    return release+'@sha256:'+content_fingerprint
