"""Finite controlled CLI stress and scoped real-parser fault proof (no network)."""
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch
from click.testing import CliRunner
import shopextract
from shopextract import cli, _cli_core
from shopextract._models import Platform

OUT = Path(__file__).parent
START = time.monotonic()
SEED = 11025
URL = 'https://synthetic.invalid/item'
async def detect(url, **kwargs):
    return SimpleNamespace(platform=Platform.SHOPIFY, confidence=0.9, signals=['synthetic'])
BASE = b'{"schema_version":1}'
# Exact expected codes/modes predeclared in reviewed G01-G10 and original SC04.
CASES = [
 ('boolean-version', b'{"schema_version":true}', {}, 2, 'E_CONFIG'),
 ('duplicate-key', b'{"schema_version":1,"schema_version":1}', {}, 2, 'E_CONFIG'),
 ('unknown-key', b'{"schema_version":1,"unknown":0}', {}, 2, 'E_CONFIG'),
 ('nonfinite', b'{"schema_version":1,"diagnostics":NaN}', {}, 2, 'E_CONFIG'),
 ('invalid-utf8', b'\xff', {}, 2, 'E_CONFIG'),
 ('cap-below', BASE + b' ' * (65535-len(BASE)), {}, 0, None),
 ('cap-at', BASE + b' ' * (65536-len(BASE)), {}, 0, None),
 ('cap-above', BASE + b' ' * (65537-len(BASE)), {}, 2, 'E_CONFIG'),
 ('file-over-env', b'{"schema_version":1,"output_format":"json"}', {'SHOPEXTRACT_OUTPUT_FORMAT':'legacy'}, 0, None),
 ('invalid-overridden-env', BASE, {'SHOPEXTRACT_DIAGNOSTICS':'invalid'}, 2, 'E_CONFIG'),
 ('invalid-format-env-json', BASE, {'SHOPEXTRACT_OUTPUT_FORMAT':'json'}, 2, 'E_USAGE'),
 ('bootstrap-no-config', b'{broken', {'SHOPEXTRACT_OUTPUT_FORMAT':'invalid'}, 0, 'text-help'),
]
results=[]
with tempfile.TemporaryDirectory(prefix='cli-p0-') as directory, patch.object(shopextract, 'detect', detect):
    selected = Path(directory) / 'cli.json'
    clean = {k:v for k,v in os.environ.items() if not k.startswith('SHOPEXTRACT_')}
    with patch.dict(os.environ, clean, clear=True):
        for name,content,environment,exit_code,code in CASES:
            assert time.monotonic()-START < 120
            selected.write_bytes(content)
            argv=['--output-format','json','--config',str(selected),'detect',URL]
            if name=='file-over-env':argv=['--config',str(selected),'detect',URL]
            if name=='invalid-format-env-json':argv=['--output-format','invalid','--config',str(selected),'detect',URL]
            if name=='bootstrap-no-config':argv=['--config',str(selected),'detect','--help']
            start=time.monotonic();result=CliRunner().invoke(cli.main,argv,env=environment)
            assert time.monotonic()-start < 30
            assert result.exit_code==exit_code,(name,result.output)
            if code=='text-help':assert 'Usage:' in result.stdout
            else:
                payload=json.loads(result.stdout)
                assert (payload['error']['code'] if payload['error'] else None)==code,(name,payload)
            results.append({'case':name,'input_bytes':len(content),'exit':result.exit_code,'passed':True})
            (OUT/'core-stress.json').write_text(json.dumps({'seed':SEED,'limits':{'cases':12,'max_input_bytes':65537,'per_run_seconds':30,'total_seconds':120,'workers':1},'cases':results,'complete':len(results)==12,'provenance':'synthetic controlled CLI/native boundary; actual production config/bootstrap/emitter'},indent=2)+'\n')
        selected.write_bytes(b'{"schema_version":1,"schema_version":1}')
        argv=['--output-format','json','--config',str(selected),'detect',URL]
        def execute():return CliRunner().invoke(cli.main,argv)
        before=execute();assert before.exit_code==2
        # Only the duplicate-key rejection hook is disabled, not the parser/emitter.
        with patch.object(_cli_core,'_reject_pairs',dict):
            mutated=execute()
            caught=False
            try:assert mutated.exit_code==2
            except AssertionError:caught=True
            assert caught and mutated.exit_code==0
        restored=execute();assert restored.exit_code==2
        (OUT/'core-fault-proof.json').write_text(json.dumps({'mechanism':'actual JSON object_pairs_hook duplicate rejection','mutation':'scoped _reject_pairs=dict; restored by patch context','baseline_exit':before.exit_code,'mutated_exit':mutated.exit_code,'critical_assertion_detected_fault':caught,'restored_exit':restored.exit_code,'invocations':3,'network_models':False},indent=2)+'\n')
print(json.dumps({'stress_cases':len(results),'fault_invocations':3,'passed':True,'elapsed_seconds':round(time.monotonic()-START,3)}))
