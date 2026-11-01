"""Bounded local catalog profiles; no merchant approval or protocol certification."""
from dataclasses import fields
from decimal import Decimal,InvalidOperation
import json
from urllib.parse import urlsplit
from ._models import Product,Variant
from .validate._destination import assess_google,source_record,RULES_VERSION
from ._currencies import is_pricing_currency

_SOURCE_DATE='2026-11-01'
_LIMITS={'records':1000,'source_variants':1000,'source_depth':64,'assessed_variants':100,'assessed_depth':8,'field_bytes':8192,'report_bytes':8*1024*1024}
_REGISTRY={
 'google_shopping':('limited_google_catalog_subset',RULES_VERSION,'https://support.google.com/merchants/answer/7052112','catalog_subset'),
 'schema_org':('schema_model_coverage','shopextract.schema-coverage.v1','https://schema.org/Product','vocabulary'),
 'openai_discovery':('openai_basic_product_fields','shopextract.openai-basic.v1','https://developers.openai.com/commerce/specs/file-upload/products?fields=required&version=currently-stable&view=table','stable_basic_fields'),
 'acp':('unsupported_protocol_assessment','shopextract.protocol-unassessed.v1','https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/rfcs/rfc.product_feeds.md','RFCProposal')}
_TEXT_FIELDS=('item_id','external_id','canonical_product_id','sku','gtin','mpn','name','title','description','body_html','url','product_url','image','image_url','brand','vendor','seller_name','price','currency','condition','productGroupID','productID','item_group_id','availability')


def _plain(value):
    if isinstance(value,dict):return value
    if isinstance(value,(Product,Variant)):return {f.name:getattr(value,f.name) for f in fields(value)}
    raise ValueError('Profile items must be product objects')


def _children(value):
    p=_plain(value)
    children=p.get('hasVariant') if 'hasVariant' in p else p.get('variants')
    if not children and isinstance(value,Product):
        raw=p.get('raw_data') or {}
        if isinstance(raw,dict) and raw.get('@type')=='ProductGroup':children=raw.get('hasVariant')
    if children is None:return []
    if isinstance(children,(dict,Product,Variant)):return [children]
    if not isinstance(children,list):raise ValueError('Variant references require captured product objects')
    return children


def _issue(code,field='',state='needs_context',message=''):
    return dict(code=code,field=field,state=state,message=message or code.replace('_',' '))


_IDENTIFIER_FIELDS=('item_id','external_id','canonical_product_id','sku','productGroupID','productID','item_group_id')


def _label_part(record,names):
    for name in names:
        value=record.get(name)
        if isinstance(value,(str,int,float,Decimal)) and not isinstance(value,bool) and str(value).strip():return str(value)
    return ''


def _label_parts(value):
    p=_plain(value)
    return (_label_part(p,_IDENTIFIER_FIELDS),_label_part(p,('product_url','url')),_label_part(p,('name','title')))


def _item_label(value):
    return next((v for v in _label_parts(value) if v),'')


def _key_shape(value):
    p=_plain(value)
    known={k:str(p[k]) for k in _TEXT_FIELDS if k in p and isinstance(p[k],(str,int,float,Decimal,bool))}
    return {'fields':known,'variants':[_key_shape(v) for v in _children(value)]}


def _key(value):
    return (*_label_parts(value),json.dumps(_key_shape(value),sort_keys=True,ensure_ascii=True,separators=(',',':')))


def _subtree_nodes(value):
    return 1+sum(_subtree_nodes(v) for v in _children(value))


def _preflight(products,seller):
    if len(products)>_LIMITS['records']:return 'record_budget_exceeded'
    active=set();variant_count=0;projected_bytes=4096
    def visit(value,depth=0):
        nonlocal variant_count,projected_bytes
        if depth>_LIMITS['source_depth']:return 'source_variant_depth_exceeded'
        if depth and not isinstance(value,(dict,Product,Variant)):
            return 'uncaptured_variant_reference' if isinstance(value,str) else 'invalid_variant_shape'
        if id(value) in active:return 'cyclic_variant_graph'
        active.add(id(value))
        try:
            p=_plain(value)
            for key in _TEXT_FIELDS:
                val=p.get(key)
                if key in _IDENTIFIER_FIELDS and val is not None and (not isinstance(val,(str,int,float,Decimal)) or isinstance(val,bool)):
                    return 'unsupported_identifier_shape'
                if isinstance(val,str):
                    if len(val)>_LIMITS['field_bytes'] or len(val.encode('utf-8'))>_LIMITS['field_bytes']:return 'field_byte_budget_exceeded'
                    projected_bytes+=len(json.dumps(val,ensure_ascii=True).encode())+len(key)+8
            if depth==0 and seller:
                if not isinstance(seller,str):return 'invalid_seller_context'
                if len(seller)>8192 or len(seller.encode())>8192:return 'field_byte_budget_exceeded'
                projected_bytes+=len(json.dumps(seller,ensure_ascii=True).encode())
            if projected_bytes>_LIMITS['report_bytes']-4096:return 'projection_byte_budget_exceeded'
            try:children=_children(value)
            except ValueError:
                raw=p.get('hasVariant',p.get('variants'))
                return 'uncaptured_variant_reference' if isinstance(raw,str) else 'invalid_variant_shape'
            variant_count+=len(children)
            if variant_count>_LIMITS['source_variants']:return 'variant_input_budget_exceeded'
            for child in children:
                failure=visit(child,depth+1)
                if failure:return failure
        finally:active.remove(id(value))
    for product in products:
        failure=visit(product)
        if failure:return failure
    return None


def _supported(p,support,key):
    if support is None:return p.get(key)
    entry=support.get('/'+key,{})
    return p.get(key) if entry.get('state')=='observed' and entry.get('value')==p.get(key) else None


def _text(value):return isinstance(value,str) and bool(value.strip())


def _basic(value,seller):
    p,support=source_record(value);checks=[]
    def val(key):return _supported(p,support,key)
    projection={'item_id':val('item_id') or val('external_id') or p.get('canonical_product_id'),
        'title':val('title') or val('name'),'description':val('description'),
        'url':val('product_url') or val('url'),'brand':val('brand') or val('vendor'),
        'seller_name':seller,'image_url':val('image_url') or val('image')}
    for key in ('item_id','title','description','url','brand','seller_name','image_url'):
        if not _text(projection.get(key)):
            checks.append(_issue('missing_'+key,key,'missing'));projection.pop(key,None)
    for key in ('url','image_url'):
        if key in projection:
            parsed=urlsplit(projection[key])
            if parsed.scheme not in ('http','https') or not parsed.netloc:checks.append(_issue('invalid_'+key,key,'invalid'))
    stock=val('in_stock');availability=val('availability')
    if availability and availability not in ('in_stock','out_of_stock','unknown'):
        checks.append(_issue('availability_value_unassessed','availability'))
    else:projection['availability']=availability or ('in_stock' if stock is True else 'out_of_stock' if stock is False else 'unknown')
    currency=val('currency')
    if not isinstance(currency,str) or not is_pricing_currency(currency.strip()):checks.append(_issue('missing_or_invalid_currency','currency','invalid'))
    try:
        amount=Decimal(str(val('price')))
        if not amount.is_finite() or amount<0:raise ValueError()
        if isinstance(currency,str) and is_pricing_currency(currency.strip()):projection['price']=str(amount)+' '+currency.strip().upper()
    except (ValueError,TypeError,InvalidOperation):checks.append(_issue('missing_or_invalid_price','price','invalid'))
    if _children(value):checks.append(_issue('variant_grouping_unassessed','variants'))
    return projection,checks


def readiness_report(products,target,*,context=None,seller_name=None):
    """Assess only the named profile; ready never means listing/checkout approval."""
    if target not in _REGISTRY:raise ValueError('Unknown readiness target')
    if not isinstance(products,list):raise ValueError('Expected a bounded product list')
    if context is not None and not isinstance(context,dict):raise ValueError('Context must be an object')
    context=context or {};seller=seller_name if seller_name is not None else context.get('seller_name')
    scope,rules,link,maturity=_REGISTRY[target]
    result=dict(schema_version='1.0',rule_set=rules,source_date=_SOURCE_DATE,source_links=[link],
        provenance=dict(maturity=maturity,source_date_kind='retrieved',source_support='Retained observations or supplied unverified fields; no external verification'),
        assessment_scope=scope,ready=False,summary=dict(input_records=len(products),assessed_records=0,omitted_records=0,omitted_variants=0),items=[],diagnostics=[],
        unassessed_checks=['merchant_verification','ads','checkout','full_destination_requirements'],limits=dict(_LIMITS))
    failure=_preflight(products,seller)
    if failure:
        result['diagnostics'].append(_issue(failure));result['summary']['omitted_records']=len(products);return result
    ordered=sorted(products,key=_key);assessed=0;omitted=0;used=4096
    def schema_node(value,depth=0):
        nonlocal assessed,omitted
        p,support=source_record(value) if isinstance(value,Product) else (_plain(value),None)
        raw=p.get('raw_data') or {}
        if isinstance(value,Product) and isinstance(raw,dict) and raw.get('@type')=='ProductGroup':p=raw;support=None
        types=p.get('@type','Product');types=types[:8] if isinstance(types,list) else [types]
        kind='ProductGroup' if any(str(t).rsplit('/',1)[-1].rsplit('#',1)[-1]=='ProductGroup' for t in types) else 'Product'
        def val(key):return _supported(p,support,key)
        offer=bool(p.get('offers')) if 'offers' in p else val('price') is not None and bool(val('currency'))
        coverage=dict(name=bool(val('name') or val('title')),url=bool(val('url') or val('product_url')),image=bool(val('image') or val('image_url')),identifier=bool(val('sku') or val('gtin') or val('productID') or val('productGroupID') or val('external_id')),offer=offer)
        node=dict(kind=kind,coverage=coverage,checks=[_issue('missing_'+k,k,'missing') for k,v in coverage.items() if not v],variants=[])
        for child in sorted(_children(value),key=_key):
            if depth>=_LIMITS['assessed_depth'] or assessed>=_LIMITS['assessed_variants']:
                omitted+=_subtree_nodes(child)
                code='variant_depth_exceeded' if depth>=_LIMITS['assessed_depth'] else 'variant_budget_exceeded'
                if not any(i['code']==code for i in result['diagnostics']):result['diagnostics'].append(_issue(code,'variants'))
                continue
            assessed+=1;node['variants'].append(schema_node(child,depth+1))
        return node
    for value in ordered:
        item_id=_item_label(value)
        if target=='google_shopping':
            assessment=assess_google(value,context=context)
            item=dict(item_id=item_id,checks=[_issue(i['rule_id'],i['field'],'needs_context' if i['severity']=='warning' else 'invalid',i['message']) for i in assessment['issues']],subset_status=assessment['subset_status'])
        elif target=='schema_org':item=dict(item_id=item_id,**schema_node(value))
        elif target=='openai_discovery':
            projection,checks=_basic(value,seller);item=dict(item_id=item_id,projection=projection,checks=checks)
        else:item=dict(item_id=item_id,checks=[_issue('unsupported_protocol_assessment','protocol')])
        size=len(json.dumps(item,ensure_ascii=True,allow_nan=False).encode())+2
        if used+size>_LIMITS['report_bytes']-4096:
            result['diagnostics'].append(_issue('projection_byte_budget_exceeded'));break
        used+=size;result['items'].append(item)
    result['summary'].update(assessed_records=len(result['items']),omitted_records=len(products)-len(result['items']),omitted_variants=omitted)
    def passed(item):return not item['checks'] and all(passed(v) for v in item.get('variants',[]))
    result['ready']=bool(result['items']) and not result['diagnostics'] and all(passed(i) for i in result['items'])
    return result


def register(main):
    import click
    from ._cli_core import CoreCommand,CliFailure
    from ._cli_data import load_catalog,read_json_file
    from ._cli_analysis import output
    @main.command('readiness',cls=CoreCommand)
    @click.argument('file')
    @click.option('--target',type=click.Choice(list(_REGISTRY)),required=True)
    @click.option('--country')
    @click.option('--category')
    @click.option('--seller-name')
    @click.option('--context','context_path',type=click.Path())
    @click.option('--strict',is_flag=True,help='Exit3 on profile blockers; retain the informational report.')
    def readiness(file,target,country,category,seller_name,context_path,strict):
        """Report local profile coverage; merchant approval/checkout remain unassessed.

        At most1000 records/source variants; schema coverage100 variants/depth8.
        Reports cap8MiB and retain explicit resource/context diagnostics.
        """
        context=read_json_file(context_path) if context_path else {}
        allowed={'destination','country','condition','category','variant','identifier_status','seller_name'}
        if not isinstance(context,dict) or context.keys()-allowed or any(type(v) is not bool if k=='variant' else not isinstance(v,str) for k,v in context.items()):
            raise CliFailure('E_USAGE','Context requires documented string fields and a boolean variant flag.')
        if country:context['country']=country
        if category:context['category']=category
        catalog=load_catalog(file)
        result=readiness_report(catalog.products if catalog.products is not None else catalog.records,target,context=context,seller_name=seller_name)
        output(result,partial=strict and not result['ready'])
