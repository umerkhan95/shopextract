"""Borrow HTTP in CLI contract fixtures; real worker tested independently."""
def borrow_worker_network(monkeypatch):
 from shopextract import _discovery_runtime
 from shopextract._discover import _discover_local
 from shopextract._models import Platform
 async def bridge(payload,**kwargs):
  return await _discover_local(payload['url'],platform=Platform(payload['platform']) if payload.get('platform') else None,max_urls=payload.get('max_urls',100),timeout=payload.get('timeout',30))
 monkeypatch.setattr(_discovery_runtime,'run_discovery_worker',bridge)
