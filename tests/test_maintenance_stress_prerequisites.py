"""Required timeout-amendment prerequisites; deterministic production semantics."""
from copy import deepcopy
from dataclasses import asdict
import json
import os
import subprocess
import sys
import time
import pytest

from shopextract.compare.identity_match import match_products
from shopextract.tools.domain import synchronous
from shopextract._portable import product_from_record
from tests.test_maintenance_acceptance import Harness, goal, supplier_html, NOW, ORIGIN
from tests.maintenance_process_guard import run_group


def parsed(description='new', *, sku='S1', attributes=None):
    product=json.loads(supplier_html(description,attributes).split('>',1)[1].rsplit('<',1)[0])
    product['sku']=sku
    html='<script type="application/ld+json">'+json.dumps(product)+'</script>'
    records=synchronous({'operation':'parse','mode':'html','platform':'generic','html':html,
        'url':ORIGIN+'/products/p1','origin':ORIGIN,'observed_at':NOW.isoformat(),'maximum':2})
    return product_from_record(records[0])


@pytest.mark.asyncio
async def test_full_dictionary_matching_equivalence_and_actual_report_evidence(tmp_path):
    cases=[([parsed('old')],[parsed('new')]),
        ([parsed('old')],[parsed('new',sku='different')]),
        ([parsed('old',attributes={'ram':'8 GB'})],[parsed('new',attributes={'ram':'16 GB'})]),
        ([parsed('old')],[parsed('new'),parsed('competing')])]
    for left,right in cases:
        original=match_products(left,right)
        materialized=match_products([asdict(p) for p in left],[asdict(p) for p in right])
        def semantics(decisions):
            values=[]
            for decision in decisions:
                value=asdict(decision);value.pop('field_support');values.append(value)
            return values
        assert semantics(original)==semantics(materialized)
        assert all(d.field_support for d in original)
        assert all(d.field_support=={} for d in materialized)
    h=Harness(tmp_path/'jobs.db')
    key,report=await h.run(goal())
    finding,=report['findings']
    assert finding['status']=='proposed_correction'
    assert finding['supplier_support']['state']=='observed' and finding['evidence_ids']
    evidence=h.store.evidence(key,finding['evidence_ids'][0])
    assert evidence['source_url'].startswith(ORIGIN) and evidence['pointer']
    assert '0–45°C' in str(evidence['retained_data'])


def test_hung_worker_and_descendant_are_terminated_and_reaped(tmp_path):
    receipt=tmp_path/'descendant.pid'
    code='''import os,signal,subprocess,sys,time
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
open(sys.argv[1],'w').write(str(child.pid))
def stop(signum,frame):
 child.wait(timeout=.4)
 sys.exit(0)
signal.signal(signal.SIGTERM,stop)
time.sleep(60)
'''
    with (tmp_path/'stdout').open('w') as output:
        result=run_group([sys.executable,'-c',code,str(receipt)],timeout=.3,stdout=output,stderr=output)
    assert result['timed_out'] and result['cleanup_seconds']<=1
    child=int(receipt.read_text())
    for pid in (child,result['pid']):
        with pytest.raises(ProcessLookupError):os.kill(pid,0)


@pytest.mark.asyncio
async def test_checkpoint_mutation_fixture_reaches_real_resume(tmp_path):
    from tests.maintenance_stress_driver import checkpoint_reuse
    await checkpoint_reuse(tmp_path/'real')
    with pytest.raises(AssertionError,match='checkpoint detector'):
        await checkpoint_reuse(tmp_path/'mutant',mutant=True)
