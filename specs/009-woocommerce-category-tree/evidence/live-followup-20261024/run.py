import asyncio,json,sys,time,hashlib
from pathlib import Path
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tests'))
from woo_tree_live_driver import coverage_check
from shopextract import Platform
from shopextract.categories import CategoryScope
from shopextract.categories.woo_tree import WooTreeLimits,fetch_woocommerce_category_tree,woo_tree_to_record,woo_tree_from_record
OUT=Path(__file__).resolve().parent
PLAN={'provenance':'planned_actual_public_read_only','targets':[{'name':'botiga-pagination','url':'https://demo.athemes.com/botiga','per_page':1,'requests':3,'categories':3},{'name':'b2b-smoke','url':'https://demo.woocommerce-b2b.com/sales-agents','per_page':3,'requests':4,'categories':12}], 'seconds_per_run':15,'outer_seconds_per_run':19,'response_bytes':262144,'retained_bytes':1048576,'workers':1,'retries':0,'stop_on_access_denial':True,'no_product_membership_or_shopify_mapping_claim':True,'expected':'Counts agree with receipts; actual parent edges only; strict codec round trip. Expansion only after saved passing small observation.'}
async def main():
 (OUT/'plan.json').write_text(json.dumps(PLAN,indent=2)+'\n')
 summaries=[]
 for target in PLAN['targets']:
  start=time.monotonic(); row={'name':target['name'],'url':target['url']}
  limits=WooTreeLimits(requests=target['requests'],per_page=target['per_page'],categories=target['categories'],seconds=15,response_bytes=262144,retained_bytes=1048576)
  try:
   tree=await asyncio.wait_for(fetch_woocommerce_category_tree(CategoryScope(Platform.WOOCOMMERCE,target['url']),limits=limits),19)
   record=woo_tree_to_record(tree)
   assertions={'coverage':coverage_check(tree),'roundtrip':woo_tree_to_record(woo_tree_from_record(record))==record,'parents_in_receipts':all(f.raw_value==json.loads(tree.pages[d.page-1].body)[d.index][f.facet] for n in tree.nodes for d in n.declarations for f in d.facts if f.state=='observed')}
   row.update(outcome=tree.outcome,reasons=tree.reasons,nodes=len(tree.nodes),pages=len(tree.pages),attempts=len(tree.attempts),parent_edges=len(tree.parent_edges),issues=[i.code for i in tree.issues],assertions=assertions,categories=[{'id':n.native_id,'facts':{f.facet:f.raw_value for f in n.declarations[0].facts if f.state=='observed'}} for n in tree.nodes])
   (OUT/(target['name']+'-record.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
  except Exception as e:row.update(error=type(e).__name__,detail=str(e)[:200])
  row['elapsed_seconds']=round(time.monotonic()-start,3)
  (OUT/(target['name']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
  summaries.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
  (OUT/'summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')
if __name__ == "__main__":
 asyncio.run(main())
