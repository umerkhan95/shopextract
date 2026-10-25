"""Bounded storage-only experiment. No production catalog replacement or dependencies."""
import dataclasses,functools,gzip,hashlib,json,math,os,random,signal,sqlite3,subprocess,sys,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/shopify-taxonomy/index-benchmark'
BUILD=ROOT/'build/shopify-taxonomy/index-comparison'


def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()


def checksum_file(path):
    digest=hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda:source.read(65536),b''):digest.update(chunk)
    return digest.hexdigest()


def prepare_records(data,path):
    if path.exists():raise ValueError('Prototype already exists; no automatic restart')
    connection=sqlite3.connect(path)
    connection.executescript('PRAGMA cache_size=-4096; CREATE TABLE record(kind TEXT,id TEXT,payload TEXT,PRIMARY KEY(kind,id)) WITHOUT ROWID; CREATE TABLE alias(kind TEXT,key TEXT,destkind TEXT,id TEXT,ambiguous INTEGER,PRIMARY KEY(kind,key)) WITHOUT ROWID;')
    expected=hashlib.sha256();rows=0
    groups={'attribute':'attributes','category':'categories','extension':'extensions','return_reason':'return_reasons','value':'values'}
    for kind,key in sorted(groups.items()):
        items=sorted(data.get(key,[]),key=lambda r:r['handle'] if kind=='extension' else r['id'])
        for item in items:
            native=item['handle'] if kind=='extension' else item['id'];payload=canonical(item).decode()
            connection.execute('INSERT INTO record VALUES(?,?,?)',(kind,native,payload))
            expected.update(canonical([kind,native,payload]));rows+=1
            alias_kind='attribute' if kind=='extension' else kind
            aliases={native}
            if kind=='category':aliases.add(item['short_id'])
            elif kind in ('attribute','value'):
                aliases.update([native.rsplit('/',1)[-1],item['handle']])
                if 'friendly_id' in item:aliases.add(item['friendly_id'])
            elif kind=='extension':aliases.add(item['friendly_id'])
            for alias in sorted(aliases):
                connection.execute('INSERT INTO alias VALUES(?,?,?,?,0) ON CONFLICT(kind,key) DO UPDATE SET ambiguous=CASE WHEN alias.destkind!=excluded.destkind OR alias.id!=excluded.id THEN 1 ELSE alias.ambiguous END',(alias_kind,alias,kind,native))
    connection.commit()
    actual=hashlib.sha256()
    for row in connection.execute('SELECT kind,id,payload FROM record ORDER BY kind,id'):actual.update(canonical(list(row)))
    assert actual.hexdigest()==expected.hexdigest()
    connection.close()
    return {'record_rows':rows,'canonical_records_sha256':actual.hexdigest(),'sqlite_bytes':path.stat().st_size}


class SQLitePrototype:
    def __init__(self,path):
        self.connection=sqlite3.connect(path.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
        self.connection.execute('PRAGMA cache_size=-4096')
        self._record=functools.lru_cache(maxsize=128)(self._uncached)
    def _uncached(self,kind,native):
        row=self.connection.execute('SELECT payload FROM record WHERE kind=? AND id=?',(kind,native)).fetchone()
        return None if row is None else json.loads(row[0])
    def schema(self,key):
        if not isinstance(key,str):raise TypeError('text key required')
        if not key:raise ValueError('nonempty key required')
        alias=self.connection.execute('SELECT destkind,id,ambiguous FROM alias WHERE kind=? AND key=?',('category',key)).fetchone()
        if alias is None:return b'null'
        if alias[2]:raise ValueError('ambiguous alias')
        node=self._record(alias[0],alias[1]);bindings=[]
        for base,extension in node['binding_refs']:
            attribute=self._record('attribute',base)
            source=self._record('extension',extension) if extension else attribute
            bindings.append({'category_id':node['id'],'base_attribute_id':base,'handle':source['handle'],'name':source['name'],
                'description':source['description'],'extended':extension is not None,'extension_handle':extension,'value_ids':attribute['value_ids']})
        return canonical({'category':{k:v for k,v in node.items() if k!='binding_refs'},'attributes':bindings})
    def close(self):self._record.cache_clear();self.connection.close()
    def cache_info(self):return self._record.cache_info()


def catalog_schema(catalog,key):
    node=catalog.category(key)
    if node is None:return b'null'
    # Same timed return representation/materialization as SQLite: fresh field
    # dictionaries + canonical UTF8 JSON bytes. No final-result byte cache.
    return canonical({'category':{f.name:getattr(node,f.name) for f in dataclasses.fields(node)},
        'attributes':[{f.name:getattr(b,f.name) for f in dataclasses.fields(b)} for b in catalog.attributes_for(node.id)]})


def rss():
    return int(subprocess.check_output(['ps','-o','rss=','-p',str(os.getpid())],text=True,timeout=2).strip())*1024


def prepare():
    started=time.perf_counter()
    from shopextract.taxonomies.shopify.resource import read_gzip,verify_resource_files
    from shopextract.taxonomies.shopify.validation import validate_resource_data
    pin=json.loads((ROOT/'src/shopextract/taxonomies/shopify/pin.json').read_text())
    directory=ROOT/'build/shopify-taxonomy/catalogs'/pin['release']/pin['fingerprint']
    t=time.perf_counter();manifest=verify_resource_files(directory,expected=pin);bytecheck=time.perf_counter()-t
    t=time.perf_counter();data=json.loads(read_gzip(directory/'catalog.json.gz'));decode=time.perf_counter()-t
    t=time.perf_counter();validate_resource_data(data,manifest);validation=time.perf_counter()-t
    BUILD.mkdir(parents=True,exist_ok=True)
    t=time.perf_counter();facts=prepare_records(data,BUILD/'catalog.sqlite');preparation=time.perf_counter()-t
    backend=SQLitePrototype(BUILD/'catalog.sqlite')
    keys=[c['id'] for c in data['categories']];randomizer=random.Random(8)
    chosen=[keys[0],'gid://shopify/TaxonomyCategory/el-6-6']
    for key in randomizer.sample(keys,130):
        if key not in chosen:chosen.append(key)
        if len(chosen)==128:break
    oracle={key:hashlib.sha256(backend.schema(key)).hexdigest() for key in chosen}
    misses=['gid://shopify/TaxonomyCategory/unknown-benchmark-'+str(i) for i in range(64)]
    for key in misses:assert backend.schema(key)==b'null'
    backend.close()
    result={'state':'passed','fingerprint':pin['fingerprint'],'source_hashes':pin['source_hashes'],'resource_sha256':pin['resource_sha256'],
        'byte_check_seconds':bytecheck,'decode_seconds':decode,'full_logical_validation_seconds':validation,'sqlite_preparation_seconds':preparation,
        'total_worker_seconds':time.perf_counter()-started,'record_counts':{k:len(data[k]) for k in ('categories','attributes','extensions','values','return_reasons')},
        'context_links':sum(len(c['binding_refs']) for c in data['categories']),'fixture_seed':8,'selected_ids':chosen,'valid_nonmembers':misses,
        'expected_schema_sha256':oracle,'sqlite_sha256':checksum_file(BUILD/'catalog.sqlite'),**facts}
    (OUT/'preparation.json').write_text(json.dumps(result,indent=2)+'\n')


def candidate(kind):
    started=time.perf_counter()
    # Equal application/module imports for both candidates; no catalog load here.
    from shopextract.taxonomies.shopify import load_shopify_taxonomy
    imports=time.perf_counter()-started;baseline_rss=rss()
    plan=json.loads((OUT/'preparation.json').read_text());t=time.perf_counter()
    if kind=='dict':
        catalog=load_shopify_taxonomy(catalog_root=ROOT/'build/shopify-taxonomy/catalogs')
        get=lambda key:catalog_schema(catalog,key);hash_seconds=None;parity='production full byte/logical/reference validation'
    else:
        h=time.perf_counter();assert checksum_file(BUILD/'catalog.sqlite')==plan['sqlite_sha256'];hash_seconds=time.perf_counter()-h
        backend=SQLitePrototype(BUILD/'catalog.sqlite');get=backend.schema;parity='prototype DB file hash only; full logical/reference checks done in preparation, not runtime equivalent'
    opened=time.perf_counter()-t;t=time.perf_counter();first=get(plan['selected_ids'][0]);first_seconds=time.perf_counter()-t
    assert hashlib.sha256(first).hexdigest()==plan['expected_schema_sha256'][plan['selected_ids'][0]]
    keys=plan['selected_ids'];mixed=keys[:64]+plan['valid_nonmembers'];random.Random(8).shuffle(mixed)
    workloads={'hot_repeat_100':[keys[1]]*100,'unique_128':keys,'mixed_hits_misses_128':mixed,
        'valid_misses_64':plan['valid_nonmembers']}
    timings={};output_digest=hashlib.sha256()
    for name,requests in workloads.items():
        samples=[]
        for key in requests:
            t=time.perf_counter_ns();payload=get(key);samples.append((time.perf_counter_ns()-t)/1e6)
            expected=plan['expected_schema_sha256'].get(key,hashlib.sha256(b'null').hexdigest())
            assert hashlib.sha256(payload).hexdigest()==expected
            output_digest.update(payload)
        ordered=sorted(samples)
        timings[name]={'items':len(requests),'total_ms':sum(samples),'p50_ms':ordered[len(ordered)//2],'p95_ms':ordered[math.ceil(.95*len(ordered))-1]}
    for size in (1,16,128):
        t=time.perf_counter();digest=hashlib.sha256()
        for offset in range(0,len(keys),size):
            for key in keys[offset:offset+size]:digest.update(get(key))
        timings['batch_'+str(size)]={'items':128,'total_ms':(time.perf_counter()-t)*1000,'sha256':digest.hexdigest()}
    record={'state':'passed','candidate':kind,'scope':'metadata storage prototype comparison; canonical JSON bytes equally materialized inside timing; no new production backend',
        'application_import_seconds':imports,'pre_backend_rss_bytes':baseline_rss,'backend_open_seconds':opened,'first_schema_seconds':first_seconds,
        'backend_plus_first_seconds':opened+first_seconds,'db_file_hash_seconds':hash_seconds,'integrity_parity':parity,'steady_rss_bytes':rss(),
        'rss_delta_from_common_imports_bytes':rss()-baseline_rss,'os_cache':'uncontrolled; expected warm after preparation; fresh process only',
        'python':sys.version,'sqlite':sqlite3.sqlite_version,'semantic_workload_sha256':output_digest.hexdigest(),'timings':timings,
        'total_worker_seconds':time.perf_counter()-started,'fingerprint':plan['fingerprint']}
    if kind=='sqlite':record['source_record_cache']=str(backend.cache_info());backend.close()
    (OUT/(kind+'.json')).write_text(json.dumps(record,indent=2)+'\n')


def run_child(mode,seconds,deadline):
    started=time.monotonic();peak=0;reason=None
    with (OUT/(mode+'.log')).open('wb') as output:
        process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--'+mode],stdout=output,stderr=output,start_new_session=True)
        def stop():
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        timer=threading.Timer(min(seconds,max(0,deadline-time.monotonic())),stop);timer.daemon=True;timer.start()
        try:
            while process.poll() is None:
                if time.monotonic()>=deadline or time.monotonic()-started>=seconds:reason='timeout';break
                listing=subprocess.check_output(['ps','-ax','-o','pgid=,rss='],text=True,timeout=2)
                current=sum(int(r)*1024 for g,r in (line.split() for line in listing.splitlines()) if int(g)==process.pid);peak=max(peak,current)
                if current>512*1024*1024:reason='rss_limit';break
                if (OUT/(mode+'.log')).stat().st_size>65536:reason='log_limit';break
                time.sleep(.05)
        finally:timer.cancel();timer.join(timeout=2);stop();process.wait(timeout=2)
    record={'stage':mode,'state':'passed' if process.returncode==0 and reason is None else 'failed','reason':reason,
        'exit_code':process.returncode,'seconds':time.monotonic()-started,'peak_sampled_group_rss_bytes':peak}
    (OUT/(mode+'-execution.json')).write_text(json.dumps(record,indent=2)+'\n')
    return record


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'attempt.json').open('x') as output:json.dump({'seed':8,'limits':{'aggregate_seconds':180,'prepare_seconds':60,'candidate_seconds':30,'rss_bytes':512*1024*1024},'code_sha256':checksum_file(Path(__file__).resolve())},output)
    started=time.monotonic();deadline=started+180;stages=[]
    for mode,limit in [('prepare',60),('dict',30),('sqlite',30)]:
        result=run_child(mode,limit,deadline);stages.append(result)
        if result['state']!='passed':break
    state='passed' if len(stages)==3 and all(r['state']=='passed' for r in stages) else 'failed'
    result={'state':state,'seconds':time.monotonic()-started,'stages':stages,'new_dependencies':0,'production_backend_changed':False}
    if state=='passed':
        a=json.loads((OUT/'dict.json').read_text());b=json.loads((OUT/'sqlite.json').read_text())
        assert a['semantic_workload_sha256']==b['semantic_workload_sha256']
        result['semantic_workload_sha256']=a['semantic_workload_sha256']
        lines=['| Metadata storage | Open+first schema s | Resident MiB | Hot p50 ms | Unique128 ms |','| --- | ---: | ---: | ---: | ---: |']
        for r in (a,b):lines.append(f"| {r['candidate']} | {r['backend_plus_first_seconds']:.4f} | {r['steady_rss_bytes']/1048576:.1f} | {r['timings']['hot_repeat_100']['p50_ms']:.4f} | {r['timings']['unique_128']['total_ms']:.2f} |")
        lines+=['','SQLite timing has weaker runtime integrity (file hash vs complete logical validation); preparation costs separate. This is not a production replacement or equivalent end-to-end pipeline benchmark.']
        (OUT/'comparison.md').write_text('\n'.join(lines)+'\n')
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':
    if len(sys.argv)==2:
        {'--prepare':prepare,'--dict':lambda:candidate('dict'),'--sqlite':lambda:candidate('sqlite')}[sys.argv[1]]()
    else:main()
