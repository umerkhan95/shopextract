"""Sequential bounded P2 mechanism stress, seed11025, no models/public network."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'specs/011-cli-feature-parity/p2/evidence/stress'
OUT.mkdir(exist_ok=True)
CASES=[
 ('grammar','nested or double_dash or new_group'),
 ('matching','matching_identity or semantic_indexed or native_semantic'),
 ('transport','portable_identity or zero_false or malformed_types'),
 ('currency','compare_groups or position_filters or dropped_raw or catalog_urls'),
 ('sources','all_failure or shared_deadline or analyze_machine'),
 ('validation','native_validation'),
 ('images','controlled_http'),
 ('exports','real_export_payload'),
 ('rollback','replace_rollback or restores_two or staging_failure'),
 ('filesystem','export_aliases or optional_engine'),
 ('boundaries','record_and_byte or threshold or store_caps'),
 ('schemas','bad_declarative or malformed_stdin or nonempty_product'),
]
start=time.monotonic();results=[]
env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',HF_HUB_DOWNLOAD_WORKERS='1')
for name,selection in CASES:
    command=[sys.executable,'-m','pytest','-q','tests/test_cli_analysis.py','tests/test_cli_analysis_mechanisms.py','-k',selection]
    begin=time.monotonic()
    with (OUT/f'{name}.log').open('w') as log:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        peak=0;failure=None
        while process.poll() is None:
            elapsed=time.monotonic()-begin
            try:
                rss=subprocess.check_output(['ps','-o','rss=','-p',str(process.pid)],text=True).strip()
                peak=max(peak,int(rss or 0))
            except (subprocess.CalledProcessError,ValueError):pass
            if elapsed>30 or time.monotonic()-start>300 or peak>512*1024:
                failure='resource bound exceeded';process.kill();break
            time.sleep(.05)
        code=process.wait()
    results.append(dict(case=name,command=command,exit_code=code,seconds=round(time.monotonic()-begin,3),peak_rss_kib=peak,failure=failure))
    (OUT/'status.json').write_text(json.dumps(dict(seed=11025,limits=dict(case_seconds=30,total_seconds=300,rss_mib=512,workers=1,max_input_bytes=1048576,max_records=1000),cases=results,seconds=round(time.monotonic()-start,3)),indent=2))
    if code or failure:sys.exit(1)
print(f'{len(results)} groups PASS in {time.monotonic()-start:.3f}s')
