"""Domain payload shapes for the version1 envelopes, not just framing."""
STRING={'type':'string','minLength':1}
NULL_STRING={'type':['string','null']}
CODES=['invalid_argument','unsupported_version','permission_denied','not_found','expired',
       'resource_limit','timeout','cancelled','source_error','internal_error']
ERROR={'type':'object','required':['code','message','retryable'], 'properties':{
    'code':{'enum':CODES},'message':STRING,'retryable':{'type':'boolean'},'details':{'type':'object'}},
    'additionalProperties':False}
SUMMARY_ERROR={'type':'object','required':['code','message'],
               'properties':{'code':{'enum':CODES},'message':STRING},'additionalProperties':False}
ACK={'type':'object','required':['job_id','state'],'properties':{
    'job_id':STRING,'state':{'enum':['queued','running']}},'additionalProperties':False}
STATUS={'type':'object','required':['state','queued_at','started_at','terminal_at'], 'properties':{
    'state':{'enum':['queued','running','succeeded','failed','cancelled','timed_out']},
    'queued_at':STRING,'started_at':NULL_STRING,'terminal_at':NULL_STRING,'error':SUMMARY_ERROR},
    'additionalProperties':False}
EVIDENCE={'type':'object','required':['evidence_id','source_url','observed_at','method','pointer','retained_data','truncated'],
    'properties':{'evidence_id':STRING,'source_url':{'type':'string','format':'uri'},
        'observed_at':{'type':'string','format':'date-time'},'method':STRING,'pointer':NULL_STRING,
        'retained_data':{},'source_role':STRING,'truncated':{'type':'boolean'},'excerpt':NULL_STRING},
    'additionalProperties':False}
PRODUCT={'type':'object','required':['title','price','currency','owner_handle','evidence_ids','field_evidence','support','variants'],
    'properties':{'title':{'type':'string'},'price':{'type':'string','pattern':r'^-?[0-9]+(?:\.[0-9]+)?(?:[Ee][+-]?[0-9]+)?$'},
        'currency':{'type':'string'},'owner_handle':STRING,'evidence_ids':{'type':'array','items':STRING},
        'field_evidence':{'type':'object','additionalProperties':{'type':'array','items':STRING}},
        'support':{'type':'object','additionalProperties':{'type':'object','required':['state'],
            'properties':{'state':{'enum':['observed','unknown','absent','unsupported','expired','conflicting']}}}},
        'variants':{'type':'array','items':{'type':'object','required':['owner_handle','evidence_ids','field_evidence']}}}}
MATCH={'type':'object','required':['relation','confidence','evidence','conflicts','needs_review','index_a','index_b','candidate_method','field_support'],
    'properties':{'relation':{'enum':['exact','variant','bundle','substitute','unmatched','uncertain']},
        'confidence':{'type':'number'},'evidence':{'type':'array'},'conflicts':{'type':'array'},
        'needs_review':{'type':'boolean'},'index_a':{'type':['integer','null']},
        'index_b':{'type':['integer','null']},'candidate_method':STRING,'field_support':{'type':'object'}},
    'additionalProperties':False}
EVENT={'type':'object','required':['candidate_id','event_id','kind','state','reason','supplier','canonical_product_id',
        'canonical_variant_id','field_path','previous_snapshot_id','current_snapshot_id','old','new','recheck'],
    'properties':{**{key:STRING for key in ['candidate_id','event_id','reason','supplier','canonical_product_id']},
        'canonical_variant_id':NULL_STRING,'field_path':{'type':'string'},
        'kind':{'enum':['field_changed','product_added','product_removed']},
        'state':{'enum':['confirmed','pending','rejected']},'previous_snapshot_id':{'type':'integer','minimum':1},
        'current_snapshot_id':{'type':'integer','minimum':1},'old':{'type':'object'},'new':{'type':'object'},
        'recheck':{'type':['object','null']}},'additionalProperties':False}
DIAGNOSTIC={'type':'object','anyOf':[{'required':['code','message']},{'required':['reason','details']}],
    'properties':{'code':STRING,'message':STRING,'source_url':STRING,'canonical_product_id':NULL_STRING,
        'canonical_variant_id':NULL_STRING,'field_path':{'type':'string'},'reason':STRING,'details':{'type':'object'}},
    'additionalProperties':False}
METADATA={'type':'object','properties':{**{key:STRING for key in ['catalog_handle','capture_handle','report_id',
    'policy_version','supplier','status','reason']},'previous_snapshot_id':{'type':'integer'},
    'current_snapshot_id':{'type':'integer'}},'additionalProperties':False}
PAGE={'type':'object','required':['state','collection','items','next_cursor','total','completeness','metadata'],
    'properties':{'state':{'const':'succeeded'},'collection':{'enum':['urls','products','matches','candidates','events','new_events','diagnostics']},
        'items':{'type':'array'},'next_cursor':NULL_STRING,'total':{'type':'integer','minimum':0},
        'completeness':{'enum':['complete','partial']},'metadata':METADATA},'additionalProperties':False,
    'allOf':[{'if':{'properties':{'collection':{'const':name}}},'then':{'properties':{'items':{'items':shape}}}}
        for name,shape in [('urls',STRING),('products',PRODUCT),('matches',MATCH),('candidates',EVENT),
                           ('events',EVENT),('new_events',EVENT),('diagnostics',DIAGNOSTIC)]]}
LOOKUP={'type':'object','required':['status','reason'],'properties':{
    'status':{'enum':['available','expired','missing','unsupported','not_retained']},'reason':STRING,'evidence':EVIDENCE},
    'allOf':[{'if':{'properties':{'status':{'const':'available'}}},'then':{'required':['evidence']}}],
    'additionalProperties':False}


def output_schema(name):
    if name in {'discover','extract','match','changes'}:data=ACK
    elif name in {'job_status','job_cancel'}:data=STATUS
    elif name=='evidence':data=LOOKUP
    else:data={'oneOf':[{'type':'object','required':['state'],'properties':{'state':{'enum':['queued','running']}},'additionalProperties':False},PAGE]}
    return {'type':'object','required':['schema_version','request_id','ok','warnings'],
        'properties':{'schema_version':{'const':'1.0'},'request_id':STRING,'ok':{'type':'boolean'},
            'warnings':{'type':'array','items':DIAGNOSTIC},'data':data,'error':ERROR},
        'oneOf':[{'required':['data'],'not':{'required':['error']},'properties':{'ok':{'const':True}}},
                 {'required':['error'],'not':{'required':['data']},'properties':{'ok':{'const':False}}}],
        'additionalProperties':False}
