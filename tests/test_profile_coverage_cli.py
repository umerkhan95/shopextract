"""Opt-in diagnostic paging/CLI/UTF8 output contracts against durable SQLite."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from click.testing import CliRunner
from shopextract.cli import main
from shopextract.maintenance import MaintenanceStore,MaintenanceError,Goal
from tests.profile_coverage_helpers import NOW,ORIGIN


def report_job(path,count=1):
    store=MaintenanceStore(path)
    goal=Goal(baseline=({'external_id':'S1','title':'Synthetic refrigerator'},),supplier_origin=ORIGIN,product_urls=(ORIGIN+'/product',),fields=('title',),profiles={'S1':'generic-v1'},deadline='2026-10-25T13:00:00+00:00')
    key=store.create(goal);store.acquire();store.begin(key,now=NOW)
    for index in range(count):
        step='fixture:'+str(index);store.add_steps(key,[(step,'compare')])
        # Deliberately legacy/minimal committed outcomes: absent source details
        # must remain not_recorded rather than fabricated captured coverage.
        finding={'finding_id':'fixture-'+str(index),'ordinal':index,'product_key':'S1','profile':'generic-v1','field':'title','status':'needs_review','reason':'supplier_unsupported','before':'Synthetic refrigerator','after':None,'comparison':'unknown','normalized_before':'Synthetic refrigerator','normalized_after':None,'trace':[],'baseline_support':{'kind':'supplied','state':'asserted'},'supplier_support':{'state':'unsupported'},'evidence_ids':[]}
        store.checkpoint(key,step,{'finding_id':finding['finding_id']},findings=[finding])
    store.finish(key,'completed');store.release()
    return store,key


def test_page_diagnostics_preserve_legacy_defaults_and_do_not_read_all_findings(tmp_path,monkeypatch):
    store,key=report_job(tmp_path/'j.db',101)
    try:
        legacy=store.report(key,offset=100,limit=1)
        assert 'profile_coverage' not in legacy
        def prohibited(*args):raise AssertionError('unbounded _findings called by opt-in page')
        monkeypatch.setattr(store,'_findings',prohibited)
        page=store.report(key,offset=100,limit=1,include_profile_coverage=True)
        assert page['findings']==legacy['findings'] and page['findings'][0]['finding_id']=='fixture-100'
        diagnostic=page['profile_coverage']
        assert (diagnostic['scope'],diagnostic['offset'],diagnostic['limit'],diagnostic['finding_count'])==('finding_page',100,1,1)
        row,=diagnostic['products'];assert row['configured_fields']==['currency','description','price','title']
        assert row['requested_fields']==row['page_fields']==['title']
        assert row['checked_fields']==[] and row['unavailable_fields']==['title']
        assert row['unrequested_fields']==['currency','description','price']
        empty=store.report(key,offset=101,limit=1,include_profile_coverage=True)
        assert empty['profile_coverage']['products']==[] and empty['profile_coverage']['finding_count']==0
    finally:store.close()


@pytest.mark.parametrize('limit,valid',[(0,False),(1,True),(999,True),(1000,True),(1001,False)])
def test_report_limit_contract_is_retained_with_diagnostics(tmp_path,limit,valid):
    store,key=report_job(tmp_path/'j.db')
    try:
        if valid:assert len(store.report(key,limit=limit,include_profile_coverage=True)['findings'])==1
        else:
            with pytest.raises(MaintenanceError,match='invalid_argument'):store.report(key,limit=limit,include_profile_coverage=True)
    finally:store.close()


def test_python_public_operation_root_and_module_cli_agree(tmp_path):
    from shopextract._cli_operations import maintenance_operation
    db=tmp_path/'j.db';store,key=report_job(db)
    try:expected=store.report(key,include_profile_coverage=True)
    finally:store.close()
    scope={'db':str(db),'profiles':None,'category_config':None,'operator_config':None,'allow_origin':()}
    assert maintenance_operation('report',scope,key,offset=0,limit=100,include_profile_coverage=True)==expected
    result=CliRunner().invoke(main,['maintenance','--db',str(db),'report',key,'--coverage'])
    assert result.exit_code==0,result.output
    assert json.loads(result.stdout)['data']==expected
    environment={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1]/'src')}
    child=subprocess.run([sys.executable,'-m','shopextract.maintenance','--db',str(db),'report',key,'--coverage'],capture_output=True,text=True,env=environment,timeout=10)
    assert child.returncode==0,child.stderr+child.stdout
    assert json.loads(child.stdout)['data']==expected


@pytest.mark.parametrize('size,allowed',[(1048575,True),(1048576,True),(1048577,False)])
def test_actual_utf8_envelope_budget_includes_newline(size,allowed):
    # Serializer accepts actual adapter envelope; it has no CLI dependency.
    encode=importlib.import_module('shopextract.maintenance.reporting').encode_coverage_response
    envelope={'schema_version':'1.0','ok':True,'data':{'payload':''},'warnings':[],'error':None,'completeness':'complete'}
    base=len(json.dumps(envelope,ensure_ascii=False,separators=(',',':')).encode())+1
    extra=size-base;envelope['data']['payload']='é'*(extra//2)+'a'*(extra%2)
    assert len(json.dumps(envelope,ensure_ascii=False,separators=(',',':')).encode())+1==size
    if allowed:
        result=encode(envelope);assert isinstance(result,bytes) and len(result)==size and result.endswith(b'\n')
    else:
        with pytest.raises(MaintenanceError,match='resource_limit'):encode(envelope)


def test_coverage_flag_is_explicit_on_both_cli_help_paths(tmp_path):
    root=CliRunner().invoke(main,['maintenance','report','--help'])
    assert root.exit_code==0 and '--coverage' in root.stdout
    child=subprocess.run([sys.executable,'-m','shopextract.maintenance','--db',str(tmp_path/'unused.db'),'report','--help'],capture_output=True,text=True,timeout=10)
    assert child.returncode==0 and '--coverage' in child.stdout
    assert not (tmp_path/'unused.db').exists()


def test_coverage_budget_rejection_keeps_single_error_envelope(tmp_path,monkeypatch,capsys):
    """Inject only resource admission failure, preserving real CLI/Store paths."""
    reporting=importlib.import_module('shopextract.maintenance.reporting')
    db=tmp_path/'j.db';store,key=report_job(db);store.close();calls=[]
    def denied(envelope):
        calls.append(True)
        raise MaintenanceError('resource_limit')
    monkeypatch.setattr(reporting,'encode_coverage_response',denied)
    root=CliRunner().invoke(main,['maintenance','--db',str(db),'report',key,'--coverage'])
    assert root.exit_code==1,root.output
    body=json.loads(root.stdout);assert body['ok'] is False and body['data'] is None
    assert body['error']['code']=='E_OPERATION' and calls
    count=len(calls)
    from shopextract.maintenance import __main__ as module
    monkeypatch.setattr(sys,'argv',['maintenance','--db',str(db),'report',key,'--coverage'])
    with pytest.raises(SystemExit) as stopped:module.main()
    assert stopped.value.code==2 and len(calls)>count
    body=json.loads(capsys.readouterr().out)
    assert body['ok'] is False and body['error']=='resource_limit' and 'data' not in body


def test_legacy_captured_baseline_without_evidence_is_not_checked():
    from shopextract.maintenance.reporting import page_coverage
    from shopextract.maintenance.store import _profile_record
    from shopextract.maintenance.profiles import profile
    goal={'profiles':{'S1':'generic-v1'},'fields':['title'],'baseline_mode':'captured'}
    finding={'product_key':'S1','field':'title','before':'Title','after':'Title','comparison':'equal','baseline_support':{'state':'observed','evidence_ids':[]},'supplier_support':{'state':'observed','evidence_ids':['e_retained']}}
    row=page_coverage(goal,{'generic-v1':_profile_record(profile('generic-v1'))},[finding],0,100)['products'][0]
    assert row['checked_fields']==[] and row['not_recorded_fields']==['title']
