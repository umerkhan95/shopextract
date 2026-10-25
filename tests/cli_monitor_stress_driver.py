"""Sequential bounded P3 mechanism stress, seed11025, no models/public network."""
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'specs/011-cli-feature-parity/p3/evidence/stress'
OUT.mkdir(exist_ok=True)
CASES=[
 ('bindings','binding_family'),
 ('snapshots','snapshot_roundtrip or snapshot_explicit or snapshot_save_rollback or metadata_invalid'),
 ('history','history_exact or legacy_identity or sqlite_connections'),
 ('reliable','reliable_replay or suspicious_recheck or partial_replay'),
 ('atomic','invalid_selection or transaction_fault'),
 ('retention','prune or lookup_missing'),
 ('resolution','resolve or policy_rejects'),
 ('artifacts','bundle_sidecar_runtime or sidecar_independent or bundle_duplicate'),
 ('aliases','alias or same_input'),
 ('corruption','malformed_artifacts or output_growth'),
 ('boundaries','boundaries or missing_db'),
 ('watch','watch or nonempty_source_errors'),
]
start=time.monotonic();results=[]
env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',HF_HUB_DOWNLOAD_WORKERS='1')
for name,selection in CASES:
    command=[sys.executable,'-m','pytest','-q','tests/test_cli_monitor.py','tests/test_cli_monitor_mechanisms.py','-k',selection]
    begin=time.monotonic()
    with (OUT/f'{name}.log').open('w') as log:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        peak=0;failure=None
        try:
            while process.poll() is None:
                elapsed=time.monotonic()-begin
                try:
                    inventory=subprocess.check_output(['ps','-axo','pid=,pgid=,rss='],text=True)
                    rss=sum(int(row.split()[2]) for row in inventory.splitlines() if len(row.split())==3 and int(row.split()[1])==process.pid)
                    peak=max(peak,rss)
                except (subprocess.CalledProcessError,ValueError):pass
                if elapsed>30 or time.monotonic()-start>300 or peak>512*1024:
                    failure='resource bound exceeded';os.killpg(process.pid,signal.SIGKILL);break
                time.sleep(.05)
            code=process.wait()
        finally:
            # All descendants inherit this isolated process group, including SIGINT transport.
            try:
                os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
        inventory=subprocess.check_output(['ps','-axo','pid=,pgid=,rss='],text=True)
        orphans=[int(row.split()[0]) for row in inventory.splitlines() if len(row.split())==3 and int(row.split()[1])==process.pid]
        if orphans:failure='process group remained after cleanup'
    results.append(dict(case=name,command=command,exit_code=code,seconds=round(time.monotonic()-begin,3),peak_rss_kib=peak,failure=failure,orphans_after_cleanup=orphans))
    (OUT/'status.json').write_text(json.dumps(dict(seed=11025,limits=dict(case_seconds=30,total_seconds=300,rss_mib=512,workers=1,max_input_bytes=1048576,max_records=1000),cases=results,seconds=round(time.monotonic()-start,3)),indent=2))
    if code or failure:sys.exit(1)
print(f'{len(results)} groups PASS in {time.monotonic()-start:.3f}s')
