"""A pinned, explicitly incomplete Google catalog subset; never account approval."""
from dataclasses import fields
from decimal import Decimal,InvalidOperation
from .._models import Product
from .._currencies import is_pricing_currency

RULES_VERSION='google-catalog-subset-2026-11-01'
UNASSESSED=['shipping','tax','certification','account','landing_page_access','image_access','specialized_apparel','source_authenticity']

def source_record(product):
    if isinstance(product,Product):
        record={f.name:getattr(product,f.name) for f in fields(Product)}
        contract=getattr(product,'evidence_contract',None)
        view=product.trust_view() if contract is not None else {}
        for path,entry in view.items():
            if path.count('/')==1 and entry.get('state')=='observed' and entry.get('value')!=record.get(path[1:]):
                entry['state']='unsupported';entry['reason']='Current scalar differs from retained resolved value'
        return record,view
    return dict(product),None


def assess_google(product,*,context=None):
    p,support=source_record(product);projection=dict(p);issues=[]
    def issue(rule,field,message,severity='error'):
        if not any(i['rule_id']==rule for i in issues):issues.append(dict(rule_id=rule,field=field,message=message,severity=severity))
    def observed(field):return support is None or support.get('/'+field,{}).get('state')=='observed'
    external=p.get('external_id') if observed('external_id') else None
    item_id=external or p.get('canonical_product_id')
    id_source='external_id' if external else 'derived_canonical' if item_id else None
    projection['external_id']=item_id
    projection['brand']=p.get('brand') or p.get('vendor')
    for field,rule in [('external_id','missing_id'),('title','missing_title'),('description','missing_description'),('product_url','missing_link'),('image_url','missing_image')]:
        value=projection.get(field)
        if not isinstance(value,str) or not value.strip() or field!='external_id' and not observed(field):issue(rule,field,'Required catalog fact missing or unsupported')
    for field,maximum in [('title',150),('description',5000)]:
        if isinstance(p.get(field),str) and len(p[field])>maximum:issue(field+'_length',field,f'Exceeds max length ({len(p[field])} > {maximum})')
    raw=p.get('raw_data') or {}
    if isinstance(raw,dict) and raw.get('og:type') in ('website','article'):
        issue('product_evidence','raw_data','Captured page does not identify a product')
    image=str(p.get('image_url') or '').lower()
    if '/placeholder/' in image or image.startswith('data:'):issue('placeholder_image','image_url','Placeholder image is not product imagery')
    try:
        amount=Decimal(str(p.get('price')))
        if not amount.is_finite() or amount<0 or not observed('price'):raise ValueError()
    except (ValueError,InvalidOperation,TypeError):issue('invalid_price','price','Amount must be finite and nonnegative with observed support')
    if 'amount' in locals() and amount.is_finite() and amount==0 and observed('price'):
        issue('zero_price_needs_context','price','Explicit zero amount needs destination-specific eligibility context','warning')
    code=p.get('currency')
    if not isinstance(code,str) or not is_pricing_currency(code.strip()) or not observed('currency'):
        issue('invalid_currency','currency','Missing, invalid or unsupported pricing currency');projection.pop('currency',None)
    else:projection['currency']=code.strip().upper()
    stock=p.get('in_stock')
    if type(stock) is not bool or not observed('in_stock'):
        projection.pop('in_stock',None);issue('missing_availability','in_stock','Availability is unknown or unsupported')
    c=context or {}
    required={'destination','country','condition','category','variant','identifier_status'}
    category=c.get('category');destination=c.get('destination');country=c.get('country')
    supported=required<=c.keys() and type(c.get('variant')) is bool and destination in ('shopping_ads','free_listings') and category in ('general','books','movie','music','1604') and (country=='US' or destination=='free_listings' and country=='PK')
    if not supported:issue('unsupported_rule_branch','context','Missing or unsupported destination context','warning')
    if category=='1604':issue('apparel_profile_not_implemented','context','Apparel profile is not assessed','warning')
    condition=c.get('condition')
    actual_condition=p.get('condition') if observed('condition') else None
    actual_condition=actual_condition.strip().lower() if isinstance(actual_condition,str) else None
    if actual_condition:projection['condition']=actual_condition
    else:projection.pop('condition',None)
    if condition not in ('new','used','refurbished'):issue('condition_need_context','condition','Condition needs captured context','warning')
    elif condition in ('used','refurbished') and not actual_condition:issue('missing_condition','condition','Used/refurbished condition must be supplied')
    if condition in ('new','used','refurbished') and actual_condition and actual_condition!=condition:issue('condition_conflict','condition','Captured condition conflicts with caller context')
    for field in ('gtin','mpn'):
        if p.get(field) and not observed(field):
            projection.pop(field,None);issue('unsupported_'+field,field,'Manufacturer identifier has no observed source support')
    if projection.get('gtin'):
        from ..compare.identity_match import _gtin
        if not _gtin(projection['gtin']):issue('invalid_gtin','gtin','Assigned GTIN has invalid length or check digit')
    brand=projection.get('brand')
    if condition=='new' and category not in ('books','movie','music') and not brand:issue('missing_brand','brand','Brand required for this subset')
    if brand and support is not None and not (observed('vendor') or observed('brand')):issue('unsupported_brand','brand','Brand has no observed source support')
    identifier=c.get('identifier_status')
    if p.get('identifier_exists')=='no' and (projection.get('gtin') or projection.get('mpn')):issue('contradictory_identifiers','identifier_exists','Identifiers contradict no-assignment declaration')
    if identifier=='absent' and not projection.get('gtin') and not projection.get('mpn') and p.get('identifier_exists')=='no':projection['identifier_exists']='no'
    else:
        if projection.get('identifier_exists')=='no':projection.pop('identifier_exists',None)
        if identifier!='present':issue('identifiers_need_context','identifiers','Assignment status needs explicit context','warning')
        elif not projection.get('gtin') and not (brand and projection.get('mpn')):issue('missing_identifiers','identifiers','Assigned GTIN or brand/manufacturer MPN required')
    if c.get('variant') is True and (country=='US' or destination=='free_listings') and not p.get('item_group_id'):issue('missing_item_group_id','item_group_id','Variant grouping identifier required')
    status='blocked' if any(i['severity']=='error' for i in issues) else 'needs_context' if issues else 'subset_pass'
    return dict(projection=projection,issues=issues,subset_status=status,id_source=id_source,unassessed_checks=list(UNASSESSED),rules_version=RULES_VERSION)
