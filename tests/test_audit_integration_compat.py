"""Final compatibility contract: source-result reuse never upgrades coverage."""
import json
import pytest
from tests.test_maintenance_acceptance import Harness,goal

@pytest.mark.asyncio
@pytest.mark.parametrize('status',[200,500])
async def test_cache_reuses_only_supported_page_observations(tmp_path,status):
 h=Harness(tmp_path/'cache.db',status=status,category='Shoes')
 try:
  await h.run(goal());sent=len(h.requests)
  h.store.acquire()
  with h.store._transaction() as db:rows=list(db.execute('SELECT payload FROM cache'))
  h.store.release()
  if status==200:
   assert rows
   for row in rows:
    value=json.loads(row['payload']);assert value['complete'] is False and value['products']
    assert {d['code'] for d in value['diagnostics']}=={'catalog_coverage_unverified'}
  else:assert not rows
  await h.run(goal())
  assert (len(h.requests)==sent) is (status==200)
 finally:h.store.close()
