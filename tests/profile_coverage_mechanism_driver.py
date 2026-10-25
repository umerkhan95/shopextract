"""Fixed48-case pilot mechanism driver; prepare/review before --smoke/--execute."""
import argparse,asyncio,hashlib,json,os,resource,runpy,sys,tempfile,time
from dataclasses import asdict,replace
from datetime import timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
OUT=ROOT/'specs/012-analysis-profile-coverage/evidence'
MANIFEST=OUT/'pilot-case-manifest.json'
NATIVE=None
INPUT_BYTES=0


def peak():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform=='darwin' else value*1024


def measured(value,registry=False):
    global INPUT_BYTES
    size=len(json.dumps(value,default=str,ensure_ascii=False,allow_nan=False).encode())
    assert size<=(2097152 if registry else 65536)
    INPUT_BYTES+=size;assert INPUT_BYTES<=16777216
    return value


def raw(**changes):
    from tests.profile_coverage_helpers import raw_product
    return measured(raw_product(**changes))


def quantity(value,semantic='total_volume'):
    return measured({'value':value,'semantic':semantic})


def compare(left,right,policy='volume_total_l_v1',semantic='total_volume'):
    from shopextract.maintenance.profiles import FieldRule,compare_field
    return compare_field(FieldRule('volume' if policy.startswith('volume') else 'length','identity_variant',policy),quantity(left,semantic),quantity(right,semantic))


async def complete_smoke(path):
    import httpx
    from tests.profile_coverage_helpers import ORIGIN,NOW,policy,configured_goal
    from shopextract.maintenance import MaintenanceStore,MaintenanceEngine
    from shopextract.tools import ToolConfig
    config=policy();store=MaintenanceStore(path/'job.db',category_config=config);calls=[]
    async def resolver(host,context):return ['93.184.216.34']
    payload={k:v for k,v in raw().items() if not k.startswith('_')}
    def wire(request):
        calls.append(str(request.url));assert len(calls)<=6
        return httpx.Response(200,text='<script type="application/ld+json">'+json.dumps(payload)+'</script>',headers={'content-type':'text/html'})
    engine=MaintenanceEngine(store,tool_config=ToolConfig(allowed_origins=(ORIGIN,)),category_config=config,resolver=resolver,wire_transport=httpx.MockTransport(wire),utc_now=lambda:NOW)
    try:
        job=store.create(configured_goal());result=await engine.run(job)
        finding,=result['findings'];assert finding['comparison']=='equal' and finding['supplier_support']['state']=='observed'
        report=store.report(job,include_profile_coverage=True)
        assert report['profile_coverage']['products'][0]['checked_fields']==['attributes/capacity']
        count=len(calls);assert (await engine.resume(job))['findings']==result['findings'] and len(calls)==count
        (OUT/'pilot-engine-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
        return {'requests':count,'checked_fields':['attributes/capacity'],'replay_requests':0}
    finally:await engine.close();store.close()


async def native_case(name,path):
    global NATIVE
    from tests.profile_coverage_helpers import NOW
    from shopextract._capture import capture
    from shopextract._normalize import normalize
    from shopextract._models import Platform
    from shopextract._portable import product_to_record
    from shopextract.maintenance import Goal,MaintenanceStore,MaintenanceEngine
    from shopextract.tools import ToolConfig
    if name=='generic':
        from tests.profile_coverage_helpers import reconcile,policy
        report=await reconcile(path/'j.db',raw=raw(),config=policy())
        assert report['profile_coverage']['products'][0]['checked_fields']==['attributes/capacity'];return
    if NATIVE is None:
        audit=runpy.run_path(str(OUT/'pilot_extraction_audit.py'))
        rows,requests=await audit['native'](retain_raw=True)
        assert len(requests)==6
        NATIVE={r['platform']:measured(r['_raw']) for r in rows}
    source=json.loads(json.dumps(NATIVE[name]));context=source['_capture']
    capture(source,context['url'],context['method'],observed_at=NOW)
    origin='https://synthetic-audit.invalid'
    product=normalize(source,Platform(name),origin,include_refrigerator_attributes=True)
    record=product_to_record(product);store=MaintenanceStore(path/'j.db')
    job=store.create(Goal(baseline=(record,),baseline_mode='captured',supplier_origin=origin,product_urls=(origin+'/product',),fields=('title','attributes/capacity'),profiles={product.external_id:'refrigerator-v1'},deadline=(NOW+timedelta(minutes=2)).isoformat()))
    engine=MaintenanceEngine(store,tool_config=ToolConfig(),utc_now=lambda:NOW)
    try:
        store.acquire();store.begin(job,now=NOW);await engine._reconcile(job,store.goal(job),[record])
        report=store.report(job,include_profile_coverage=True);row=report['profile_coverage']['products'][0]
        assert len(row['configured_fields'])==9 and row['unavailable_fields']==['attributes/capacity']
        assert 'title' in row['checked_fields']
        assert all(f['status']!='proposed_correction' for f in report['findings'])
    finally:await engine.close();store.close()


async def case_run(case,path):
    from tests.profile_coverage_helpers import policy,configured_goal,reconcile,NOW,ORIGIN
    from shopextract.maintenance.profiles import FieldRule,compare_field,profile
    name,group=case['name'],case['group']
    if group=='valid':
        units={'volume_cross_unit':('500 ml','0.5 L','volume_total_l_v1','total_volume'),
               'width_cross_unit':('60 cm','0.6 m','length_width_m_v1','product_width'),
               'height_cross_unit':('1800 mm','1.8 m','length_height_m_v1','product_height'),
               'depth_cross_unit':('650 mm','65 cm','length_depth_m_v1','product_depth'),
               'zero_present':('0 ml','0 L','volume_total_l_v1','total_volume'),
               'fractional_exact':('0.125 ml','0.000125 L','volume_total_l_v1','total_volume'),
               'trailing_zero':('250.000 L','250 L','volume_total_l_v1','total_volume')}
        if name in units:
            result=compare(*units[name]);assert result['comparison']=='equal'
            assert result['normalized_before']==result['normalized_after']
            assert result['input_states']=={'before':'value','after':'value'}
            assert result['trace'][0]['operation']==units[name][2]
            assert result['trace'][0]['unit']==('L' if units[name][2].startswith('volume') else 'm')
            if name=='trailing_zero':assert result['normalized_before']=='250'
        elif name=='long_coefficient':
            from decimal import localcontext
            digits='1234567890'*9+'1234567891'
            with localcontext() as context:
                context.prec=6;result=compare(digits+' ml',digits[:-3]+'.'+digits[-3:]+' L')
            assert result['comparison']=='equal' and result['normalized_before']==digits[:-3]+'.'+digits[-3:]
        elif name=='independent_axes':
            for axis,value,expected in [('width','60 cm','0.6'),('height','1800 mm','1.8'),('depth','65 cm','0.65')]:
                result=compare(value,expected+' m','length_'+axis+'_m_v1','product_'+axis)
                assert result['comparison']=='equal' and result['normalized_before']==expected
        elif name=='common_rule_reuse':
            from tests.test_profile_quantities import test_old_profiles_keep_exact_definition_and_comparison
            test_old_profiles_keep_exact_definition_and_comparison()
            assert all(profile('refrigerator-v1').fields[k]==v for k,v in profile('generic-v1').fields.items())
            result=await reconcile(path/'currency.db',raw=raw(additionalProperty=[{'name':'Total capacity','value':'250 L'}]),config=policy(),goal=configured_goal(fields=('price',),baseline={'price':'200','currency':'USD'}))
            finding,=result['findings']
            assert finding['reason']=='currency_mismatch', {'case':case['id'],'expected':'currency_mismatch','actual':finding['reason'],'match_reason':finding['match_reason']}
        else:
            model=name=='model_variant';field='attributes/model' if model else 'attributes/capacity'
            source=raw(model='FX300') if model else raw(additionalProperty=[{'name':'Total capacity','value':'300 L'}])
            result=await reconcile(path/'j.db',raw=source,config=policy(),goal=configured_goal(fields=(field,)))
            finding,=result['findings'];assert finding['comparison']=='different' and finding['status']=='needs_review'
    elif group=='invalid':
        if name=='missing_null':
            for value,state in [(None,'null')]:
                result=await reconcile(path/'null.db',raw=raw(additionalProperty=[{'name':'Total capacity','value':value}]),config=policy())
                assert result['findings'][0]['input_states']['after']==state
            result=await reconcile(path/'missing.db',raw=raw(additionalProperty=[]),config=policy())
            assert result['findings'][0]['input_states']['after']=='missing'
        elif name=='axis_swap':
            result=compare_field(FieldRule('length','identity_variant','length_width_m_v1'),quantity('60 cm','product_height'),quantity('0.6 m','product_width'))
            assert result['comparison']=='unknown' and result['input_reasons']['before']=='semantic_mismatch'
        elif name=='wrapper_shape':
            for item,state in [({'value':None,'semantic':'total_volume','extra':True},'null'),({'value':'','semantic':7},'empty')]:
                result=compare_field(FieldRule('volume','identity_variant','volume_total_l_v1'),measured(item),quantity('250 L'))
                assert result['input_reasons']['before']=='invalid_type' and result['input_states']['before']==state
        elif name=='length_boundary':
            assert compare('1'*126+' L','1'*126+' L')['comparison']=='equal'
            result=compare('1'*127+' L','1 L');assert result['input_reasons']['before']=='input_too_long'
        else:
            inputs={'empty':[('', 'total_volume','empty'),('\v\f','total_volume','empty')],
                'bool':[(False,'total_volume','invalid_type')], 'negative':[('-1 L','total_volume','negative')],
                'nonfinite':[('NaN','total_volume','non_finite'),('Infinity','total_volume','non_finite')],
                'range':[('1-2 L','total_volume','range')], 'unitless':[(0,'total_volume','unit_missing')],
                'wrong_unit':[('250 kg','total_volume','unit_incompatible'),('250 gallons','total_volume','unit_unsupported')],
                'semantic_context':[('250 L','net_volume','semantic_mismatch'),('250 L','gross_volume','semantic_mismatch'),('60 cm','package_width','semantic_mismatch')]}
            for index,(value,semantic,reason) in enumerate(inputs[name]):
                source=raw(additionalProperty=[],attributes={'capacity':quantity(value,semantic)})
                result=await reconcile(path/f'{index}.db',raw=source,config=policy());finding,=result['findings']
                assert finding['comparison']=='unknown' and finding['status']=='needs_review'
                assert finding['input_reasons']['after']==reason
                assert result['profile_coverage']['products'][0]['checked_fields']==[]
    elif group=='adapters':await native_case(name,path)
    elif group=='interactions':
        changes={};config=policy();goal=configured_goal();clock=NOW
        if name=='config_absent':config=None
        elif name=='selection_absent':goal=configured_goal(profiles={})
        elif name=='binding_conflict':config=policy(bound_profile='footwear-v1')
        elif name=='partial_category':changes['category']=['Refrigerators',None]
        elif name=='wrong_boots':goal=configured_goal(baseline={'product_type':'Boots'})
        elif name=='gtin_conflict':changes['gtin13']='9780140328721'
        elif name=='mpn_variant_conflict':changes.update(mpn='FX-other',model='FX300');goal=configured_goal(baseline={'mpn':'FX-base'})
        elif name=='partial_expiry':
            changes['category']=['Refrigerators',None];goal=replace(goal,freshness_seconds=1);clock=NOW+timedelta(seconds=2)
        result=await reconcile(path/'j.db',raw=raw(**changes),config=config,goal=goal,clock=clock)
        assert all(f['status']=='needs_review' for f in result['findings'])
        finding,=result['findings']
        reasons={'config_absent':'category_policy_missing','selection_absent':'category_profile_missing','binding_conflict':'category_profile_conflict','partial_category':'category_incomplete','wrong_boots':'category_mismatch'}
        if name in reasons:assert finding['reason']==reasons[name]
        if name=='gtin_conflict':assert 'GTIN differs' in finding['match_reason']['conflicts']
        if name=='mpn_variant_conflict':assert 'MPN differs' in finding['match_reason']['conflicts']
        if name=='partial_expiry':
            assert finding['supplier_support']['state']=='expired'
            assert 'category_incomplete' in finding['category_review_reasons']
            assert result['profile_coverage']['products'][0]['checked_fields']==[]
    elif group=='replay':await replay_case(name,path)
    elif group=='registry':await registry_case(name,path)
    else:raise AssertionError('Unknown reviewed case')


async def replay_case(name,path):
    import pytest
    from tests.profile_coverage_helpers import configured_goal,policy,NOW
    from shopextract.maintenance import MaintenanceStore,MaintenanceError,MaintenanceEngine
    from shopextract.tools import ToolConfig
    if name=='unit_policy_change':
        from tests.test_profile_coverage_integration import test_unit_policy_snapshot_mismatch_and_unrelated_registry_addition
        test_unit_policy_snapshot_mismatch_and_unrelated_registry_addition(path)
        from tests.test_profile_coverage_integration import test_completed_resume_rejects_changed_selected_policy_before_source
        completed=path/'completed';completed.mkdir()
        await test_completed_resume_rejects_changed_selected_policy_before_source(completed)
        store=MaintenanceStore(path/'replay.db');job=store.create(configured_goal())
        store.acquire();store.begin(job,now=NOW);store.add_step(job,'pending','extract')
        store.reserve(job,'pending',{'requests':1},now=NOW);store.finish(job,'paused');store.release()
        before=store.status(job);steps=store.steps(job);attempts=store.attempts(job,'pending')
        store.registry['refrigerator-v1']['fields']['attributes/capacity']['normalization']='length_width_m_v1'
        engine=MaintenanceEngine(store,tool_config=ToolConfig(),utc_now=lambda:NOW)
        try:
            for action in (lambda:engine.run(job),lambda:engine.resume(job),lambda:engine.retry_unknown(job,'pending')):
                with pytest.raises(MaintenanceError,match='profile_mismatch'):await action()
                assert store.status(job)==before and store.steps(job)==steps and store.attempts(job,'pending')==attempts
        finally:await engine.close();store.close()
        return
    if name=='unrelated_registry_add':
        import shopextract.maintenance.store as module
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(module,'SHIPPED',('hardware-v1','footwear-v1','generic-v1'))
            store=MaintenanceStore(path/'j.db');job=store.create(configured_goal(fields=('title',),profiles={'S1':'generic-v1'}));before=store.status(job);store.close()
        store=MaintenanceStore(path/'j.db')
        try:store.validate_profiles(job);assert store.status(job)==before and 'refrigerator-v1' in store.registry
        finally:store.close()
    elif name=='category_policy_change':
        config=policy();store=MaintenanceStore(path/'j.db',category_config=config);job=store.create(configured_goal());original=store.category_policy(job);store.close()
        changed=replace(config,profile_bindings=());store=MaintenanceStore(path/'j.db',category_config=changed)
        engine=MaintenanceEngine(store,tool_config=ToolConfig(),category_config=changed,utc_now=lambda:NOW)
        try:
            assert store.category_policy(job)==original
            with pytest.raises(MaintenanceError,match='category_policy_mismatch'):await engine.run(job)
            assert store.category_policy(job)==original and store.status(job)['state']=='queued'
        finally:await engine.close();store.close()
    else:
        import sqlite3
        store=MaintenanceStore(path/'j.db');job=store.create(configured_goal(fields=('title','description'),profiles={'S1':'generic-v1'}));store.acquire();store.begin(job,now=NOW);store.add_steps(job,[('fault','compare')])
        values=[{'finding_id':key,'ordinal':index,'product_key':'S1','field':field,'status':'needs_review','reason':'synthetic_fault','comparison':'unknown'} for index,(key,field) in enumerate([('f1','title'),('f2','description')])]
        try:
            store._connect().execute("CREATE TEMP TRIGGER fail_second BEFORE INSERT ON findings WHEN NEW.id='f2' BEGIN SELECT RAISE(ABORT,'synthetic fault'); END")
            with pytest.raises(MaintenanceError,match='storage_error'):store.checkpoint(job,'fault',{'synthetic':True},findings=values)
            assert store.report(job)['findings']==[] and store.steps(job)[0]['state']!='committed'
            store._connect().execute('DROP TRIGGER fail_second')
            store.checkpoint(job,'fault',{'synthetic':True},findings=values);store.checkpoint(job,'fault',{'synthetic':True},findings=values)
            findings=store.report(job)['findings'];assert len(findings)==2 and {f['finding_id'] for f in findings}=={'f1','f2'}
        finally:store.close()


async def registry_case(name,path):
    import pytest
    from shopextract._models import Platform
    from shopextract.categories import CategoryOptions,CategoryScope,TargetRegistry,validate_options,CategoryError
    from tests.profile_coverage_helpers import policy,configured_goal,reconcile,ORIGIN
    if name in {'below_cap','at_cap','above_cap','duplicate_targets'}:
        count={'below_cap':999,'at_cap':1000,'above_cap':1001,'duplicate_targets':2}[name]
        ids=tuple('t-'+str(i) for i in range(count)) if name!='duplicate_targets' else ('same','same')
        measured(ids,registry=True);options=CategoryOptions(CategoryScope(Platform.GENERIC,ORIGIN),TargetRegistry('synthetic:registry','1',ids))
        if name in {'above_cap','duplicate_targets'}:
            with pytest.raises(CategoryError):validate_options(options)
        else:validate_options(options)
    elif name=='scope_conflict':
        config=policy();rule=config.options.rules[0];selector=replace(rule.selector,scope=replace(config.options.scope,store_url='https://other.invalid'))
        config=replace(config,options=replace(config.options,rules=(replace(rule,selector=selector),)))
        result=await reconcile(path/'j.db',raw=raw(),config=config)
        assert result['findings'][0]['status']=='needs_review'
    else:
        from tests.test_profile_coverage_cli import test_page_diagnostics_preserve_legacy_defaults_and_do_not_read_all_findings
        with pytest.MonkeyPatch.context() as patch:test_page_diagnostics_preserve_legacy_defaults_and_do_not_read_all_findings(path,patch)


def child(mode):
    cases=json.loads(MANIFEST.read_text())['cases'];assert len(cases)==48
    progress=OUT/(mode+'-progress.json');status={'phase':'collection','phase_started':time.monotonic(),'cases':[],'seed':26,'status':'running'};start=time.monotonic()
    def save():
        status.update(peak_rss_bytes=peak(),input_bytes=INPUT_BYTES,elapsed_seconds=round(time.monotonic()-start,3))
        data=json.dumps(status,indent=2);assert len(data.encode())<=65536
        temporary=progress.with_suffix('.tmp');temporary.write_text(data+'\n');temporary.replace(progress)
    save()
    with tempfile.TemporaryDirectory(prefix='profile-mechanism-') as temp:
        root=Path(temp)
        selected=[{'id':'smoke','name':'complete_job'}] if mode=='smoke' else cases
        for case in selected:
            directory=root/case['id'];directory.mkdir();status.update(phase='invocation',phase_started=time.monotonic(),active=case['id']);save();started=time.monotonic()
            try:
                if mode=='smoke':result=asyncio.run(asyncio.wait_for(complete_smoke(directory),10))
                else:result=asyncio.run(asyncio.wait_for(case_run(case,directory),10))
                assert time.monotonic()-started<10 and peak()<=536870912
                status['cases'].append({'id':case['id'],'status':'passed','seconds':round(time.monotonic()-started,3),'result':result})
            except BaseException as error:
                status.update(status='failed',error_type=type(error).__name__,error=str(error)[:2048]);save();raise
            status.update(phase='idle',phase_started=time.monotonic());save()
    status.update(phase='finished',status='passed',active=None);save();print(json.dumps({'status':status['status'],'cases':len(status['cases']),'seconds':status['elapsed_seconds']}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true');parser.add_argument('--execute',action='store_true');parser.add_argument('--child',choices=['smoke','mechanism']);args=parser.parse_args()
    if args.child:child(args.child);return
    if not (args.smoke or args.execute):
        print(json.dumps({'state':'prepared_not_executed','cases':48,'manifest':str(MANIFEST)}));return
    mode='smoke' if args.smoke else 'mechanism'
    if mode=='mechanism':assert json.loads((OUT/'smoke-progress.json').read_text())['status']=='passed','Save smoke first'
    # Reset this invocation's watchdog state before the child starts.
    progress = OUT / (mode + '-progress.json')
    if progress.exists():
        progress.replace(OUT / (mode + '-previous-progress.json'))
    from tests.category_mechanism_driver import run_bounded
    from scripts.run_tests import _subreaper
    previous=_subreaper(True)
    env={**os.environ,'PYTHONPATH':str(ROOT/'src')+os.pathsep+str(ROOT),'PYTHONHASHSEED':'26','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false','HF_HUB_OFFLINE':'1'}
    try:
        result=run_bounded([sys.executable,__file__,'--child',mode],seconds=115,log_path=OUT/(mode+'-driver.log'),env=env,log_bytes=262144,progress_path=OUT/(mode+'-progress.json'),invocation_seconds=10,collection_seconds=10)
    finally:
        if previous is not None:_subreaper(previous)
    result['cleanup_reservation_seconds']=5;result['total_ceiling_seconds']=120
    (OUT/(mode+'-driver-result.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));raise SystemExit(0 if result['returncode']==0 and not result['timed_out'] and not result['log_truncated'] else 1)


if __name__=='__main__':main()
