"""ONE declared read-only public Woo tree smoke; real transport counted, no retries."""
import hashlib
import json
from pathlib import Path
import time

import httpx
from click.testing import CliRunner

from shopextract.cli import main
from shopextract.categories import CategoryOptions,CategoryScope,TargetRegistry
from shopextract.categories._codec import wire
from shopextract.categories.woo_tree import WooTreeLimits,woo_tree_from_record
from shopextract._models import Platform
from shopextract.tools.security import GuardedTransport

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'specs/011-cli-feature-parity/p4/evidence/live'
BUDGET=ROOT/'specs/011-cli-feature-parity/evidence/live-budget.json'
TARGET='https://demo.athemes.com/botiga'

def run():
 DEST.mkdir(parents=True,exist_ok=True)
 if (DEST/'report.json').exists():raise RuntimeError('one declared smoke already saved; no rerun')
 budget=json.loads(BUDGET.read_text())
 assert 'P4' not in budget['phases']
 retained=budget.get('retained_item_budget',dict(products=budget['spent']['retained_products'],category_nodes=0,total=budget['spent']['retained_products'],ceiling=12))
 assert retained['total']+2<=retained['ceiling'] and budget['spent']['actual_http_attempts']+5<=30
 assert budget['spent']['live_wall_seconds']+30<=300
 options=CategoryOptions(CategoryScope(Platform.WOOCOMMERCE,TARGET),TargetRegistry('operator-local','v1',()))
 options_path=DEST/'options.json';options_path.write_text(json.dumps(wire(options)))
 limits=wire(WooTreeLimits(requests=5,per_page=2,categories=2,response_bytes=1048576,retained_bytes=1048576,seconds=25.))
 limits_path=DEST/'limits.json';limits_path.write_text(json.dumps(limits))
 sends=[];original=GuardedTransport.raw
 async def counted(transport,request):
  if len(sends)>=5:raise RuntimeError('live send ceiling reached before submission')
  receipt=dict(method=request.method,url=str(request.url),status=None)
  sends.append(receipt)
  try:
   response=await original(transport,request);receipt['status']=response.status_code;return response
  except BaseException as error:
   receipt['error_type']=type(error).__name__;raise
 command=['--output-format','json','categories','tree','fetch','--options',str(options_path),
          '--limits',str(limits_path),'--timeout','30']
 began=time.monotonic()
 GuardedTransport.raw=counted
 try:
  result=CliRunner().invoke(main,command)
 finally:
  GuardedTransport.raw=original
 elapsed=round(time.monotonic()-began,3)
 (DEST/'response.json').write_text(result.output)
 response=json.loads(result.output)
 data=response.get('data') or {};record=data.get('tree');nodes=0;outcome='operation_failure'
 if record:
  tree=woo_tree_from_record(record);nodes=len(tree.nodes);outcome=tree.outcome
  (DEST/'tree.json').write_text(json.dumps(record,ensure_ascii=False,separators=(',',':')))
 assert nodes<=2 and len(sends)<=5 and elapsed<=30
 status='observed_bounded_tree' if outcome in ('complete','partial') else 'observed_source_unavailable_or_malformed'
 report=dict(target=TARGET,command=command,actual_http_attempts=len(sends),http_sends=sends,
  retained_products=0,retained_category_nodes=nodes,retained_items=nodes,live_wall_seconds=elapsed,
  cli_exit=result.exit_code,outcome=outcome,reasons=data.get('reasons',[]),status=status,
  record_sha256=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest() if record else None,
  notes='One saved read-only smoke; no retries/expansion/browser/model. Synthetic mechanism coverage separate; unavailable is not category availability success.')
 (DEST/'report.json').write_text(json.dumps(report,indent=2))
 budget['phases']['P4']={k:report[k] for k in ('target','actual_http_attempts','retained_products','retained_category_nodes','retained_items','live_wall_seconds','status','outcome')}
 budget['phases']['P4']['evidence']='../p4/evidence/live/report.json'
 budget['spent']['actual_http_attempts']+=len(sends)
 budget['spent']['live_wall_seconds']=round(budget['spent']['live_wall_seconds']+elapsed,3)
 budget['spent']['retained_category_nodes']=budget['spent'].get('retained_category_nodes',0)+nodes
 budget['spent']['retained_items']=retained['total']+nodes
 retained['category_nodes']+=nodes;retained['total']+=nodes
 budget['retained_item_budget']=retained
 BUDGET.write_text(json.dumps(budget,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':run()
