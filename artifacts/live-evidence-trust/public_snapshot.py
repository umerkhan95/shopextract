"""Bounded live proof of the existing public async snapshot entry point."""
import asyncio,json,sqlite3,subprocess,sys
from pathlib import Path
from run import ROOT,audit
from shopextract import snapshot,load_snapshot
async def main():
    db=ROOT/'public-snapshot.db'
    assert not db.exists()
    count=await asyncio.wait_for(snapshot('https://www.boardgamebliss.com',db_path=str(db),max_urls=2),65)
    assert count==2
    with sqlite3.connect(db) as c:
        sid,complete,budget=c.execute('SELECT id,catalog_complete,max_urls FROM snapshots ORDER BY id DESC LIMIT 1').fetchone()
    assert complete==0 and budget==2
    report=audit(load_snapshot(sid,db_path=str(db)),db,sid)
    assert report['field_states'].get('observed',0)>0
    child=subprocess.run([sys.executable,str(ROOT/'run.py'),'--reopen',str(db),str(sid)],capture_output=True,text=True,timeout=30)
    assert child.returncode==0,child.stderr[-500:]
    report.update(status='passed',products=count,catalog_complete=False,max_urls=budget,entry_point='shopextract.snapshot',separate_process_reopen=True)
    (ROOT/'public-snapshot.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
asyncio.run(main())
