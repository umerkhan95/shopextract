"""Browser-free source-owned structured product parsing shared with native tools."""
from dataclasses import dataclass
import json
import re
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from ._capture import capture
from ._product_admission import has_product_evidence
from .extractors._schema_org import SchemaOrgExtractor
from .extractors._opengraph import OpenGraphExtractor


# Containers that hold only the page product's media; the info column also holds
# payment widgets and share icons, so it is a fallback, not a gallery.
_GALLERY='.product.media,[data-gallery-role="gallery-placeholder"],.MagicToolboxContainer,.woocommerce-product-gallery'
_IMAGE_PATH=re.compile(r'\.(?:jpe?g|png|webp|gif|avif)$',re.I)
_BRAND='[itemprop="brand"],.product-brand,.brand-name'
_BREADCRUMB='.breadcrumbs li,ol.breadcrumb li,nav[aria-label="breadcrumb"] li,nav[aria-label="Breadcrumb"] li'


def _theme_asset(url):
    path=urlsplit(url).path.lower()
    return path.endswith('.svg') or '/static/' in path and '/frontend/' in path


def _image_candidates(node):
    candidates=[]
    for image in node.select('img'):
        candidate=image.get('data-src') or image.get('data-original') or image.get('src')
        if not candidate and image.get('srcset'):candidate=image['srcset'].split(',')[0].strip().split()[0]
        if candidate:candidates.append(candidate)
    return candidates


# Rejecting a placeholder or theme asset is cleanup of a wrong value, not lost
# coverage; other diagnostics mean the parser may have dropped source data.
CLEANUP_CODES=frozenset({'placeholder_image','theme_asset_image'})


def coverage_issues(diagnostics):
    return [d for d in diagnostics if d['code'] not in CLEANUP_CODES]


# SFRA's description tab; themes keep the reference .description/.long-description markup or an id.
_SFRA_DESCRIPTION='.description-and-detail #nav-description .content,.description-and-detail .description .content,.long-description'
_CURRENCY_CODE=re.compile(r'"currencyCode"\s*:\s*"([A-Z]{3})"')


def _sfra_products(soup,url,issues):
    """Salesforce B2C Commerce (SFRA) product view without JSON-LD or product Open Graph.

    The storefront renders the product id on ``.product-detail[data-pid]``, the
    sales price as ``.prices .sales .value[content]`` and the analytics currency
    in its data layer, the description in its detail tabs. Only the page's own
    product is read, and a field the page does not render stays absent: the
    view states no stock, so availability stays unknown.
    """
    details=soup.select('.product-detail[data-pid]')
    if len(details)!=1:return []
    detail=details[0];pid=(detail.get('data-pid') or '').strip()
    if not pid or pid not in urlsplit(url).path:return []
    name=detail.select_one('.product-name')
    name=name.get_text(' ',strip=True) if name else ''
    price=detail.select_one('.prices .sales .value[content]')
    currencies={m.group(1) for script in soup.select('script') for m in _CURRENCY_CODE.finditer(script.get_text())}
    if not name or price is None:
        issues.append({'code':'sfra_product_incomplete','message':'SFRA product view has no name or sales price'})
        return []
    product={'@type':'Product','name':name,'sku':pid,'productID':pid,'url':url,
             'offers':{'@type':'Offer','price':price['content'].strip()}}
    description=soup.select_one(_SFRA_DESCRIPTION)
    description=description.get_text(' ',strip=True) if description else ''
    if description:product['description']=description
    if len(currencies)==1:product['offers']['priceCurrency']=currencies.pop()
    elif currencies:issues.append({'code':'conflicting_currency','message':'Data layer names several currencies'})
    images=[]
    for image in detail.select('.primary-images img'):
        candidate=image.get('data-high-src') or image.get('data-src') or image.get('src') or ''
        if candidate and not candidate.startswith('data:'):
            candidate=urljoin(url,candidate)
            if candidate not in images:images.append(candidate)
    if images:product['image']=images
    return [capture(product,url,'html_sfra')]


@dataclass
class StructuredHTMLResult:
    products:list
    diagnostics:list


def extract_structured_products(html,url,*,include_categories=False,max_nodes=256,max_depth=8,max_images=20):
    if not 0<max_nodes<=256 or not 0<max_depth<=8 or not 0<max_images<=20:raise ValueError('Invalid HTML limits')
    soup=BeautifulSoup(html,'html.parser');issues=[]
    breadcrumbs=[]
    products=SchemaOrgExtractor.extract_from_html(html,url,diagnostics=issues,max_nodes=max_nodes,max_depth=max_depth,_soup=soup,collected_nodes=breadcrumbs)
    og=OpenGraphExtractor.extract_from_html(html,url,include_categories=include_categories)
    if not products:products=[p for p in og if has_product_evidence(p)]
    if not products:products=_sfra_products(soup,url,issues)
    def warn(code,message):
        if not any(i['code']==code for i in issues):issues.append({'code':code,'message':message})
    def bind(product,key,value,source,source_path):
        product[key]=value
        target='/'+key
        product.setdefault('_field_sources',{})[target]={'capture_path':source_path,'_capture':source}
        if isinstance(value,list):
            for i in range(len(value)):product['_field_sources'][target+'/'+str(i)]={'capture_path':source_path+'/'+str(i),'_capture':source}
    section=soup.select_one('main.product,main.product-info-main,.product-info-main')
    form=(section.select_one('#product_addtocart_form') if section else None) or soup.select_one('form#product_addtocart_form')
    sku=section.select_one('span.sku,[itemprop="sku"]') if section else None
    sku=sku.get_text(strip=True) if sku else None
    identity=form.select_one('input[name="product"]') if form else None
    product_id=identity.get('value') if identity else None
    matches=[p for p in products if p.get('url') and urljoin(url,str(p['url']))==url or p.get('@id')==url]
    if len(matches)!=1 and product_id:matches=[p for p in products if str(p.get('productID',''))==product_id or p.get('sku')==product_id]
    owner=matches[0] if len(matches)==1 else products[0] if len(products)==1 else None
    if len(products)>1 and owner is None:warn('ambiguous_dom_owner','DOM fields have no unique captured product owner')
    if og and owner is not None:
        meta=og[0]
        for p in [owner]:
            for field,key in [('image','og:image'),('description','og:description'),('url','og:url')]:
                if not p.get(field) and meta.get(key):bind(p,field,meta[key],meta['_capture'],'/'+key)
    if owner is not None:
        dom={}
        if sku:dom['sku']=sku
        if product_id:dom['productID']=str(product_id)
        # Magento renders the regular price beside the final one, keyed by the
        # form's product id; related-product price boxes carry other ids.
        regular=soup.select_one(f'#old-price-{product_id}[data-price-type="oldPrice"][data-price-amount]') if product_id and str(product_id).isdigit() else None
        if regular is not None:dom['compare_at_price']=regular['data-price-amount']
        containers=soup.select(_GALLERY)
        containers=[c for c in containers if not any(p in containers for p in c.parents)]
        if len(containers)>1:warn('ambiguous_gallery','Several gallery containers; info column used instead')
        if len(containers)==1:
            # Zoom galleries link full-size files and show cached thumbnails; prefer the links.
            links=[a['href'] for a in containers[0].select('a[href]') if _IMAGE_PATH.search(urlsplit(a['href']).path)]
            candidates=links or _image_candidates(containers[0])
        else:candidates=_image_candidates(section) if section else []
        gallery=[]
        for candidate in candidates:
            candidate=urljoin(url,candidate)
            if _theme_asset(candidate):warn('theme_asset_image','Theme or widget asset rejected as product image')
            elif candidate not in gallery:gallery.append(candidate)
        dom['gallery']=gallery
        scope=[n for n in (section,*(containers if len(containers)==1 else [])) if n is not None]
        brands=set()
        for node in (b for n in scope for b in n.select(_BRAND)):
            value=node.get('content') or (node.a or node).get_text(' ',strip=True)
            if value:brands.add(value)
        if len(brands)>1:warn('conflicting_brand','Scoped DOM brand values disagree')
        elif brands:dom['brand']=brands.pop()
        source=capture({'dom':dom},url,'html_dom')['_capture']
        for field in ('sku','productID','brand','compare_at_price'):
            if dom.get(field):
                current=owner.get(field);current=current.get('name') if isinstance(current,dict) else current
                if current and str(current)!=str(dom[field]):
                    warn('conflicting_'+field,'Structured field conflicts with scoped DOM source')
                    owner.setdefault('_html_field_conflicts',{})[field]=[str(current),str(dom[field])]
                elif not owner.get(field):bind(owner,field,dom[field],source,'/dom/'+field)
    def placeholder(value):
        path=urlsplit(value).path.lower()
        return value.startswith('data:') or '/placeholder/' in path or path.rsplit('/',1)[-1] in ('placeholder.jpg','placeholder.png','spacer.gif','transparent.gif')
    for p in products:
        original=p.get('image') or p.get('og:image') or []
        originals=original if isinstance(original,list) else [original]
        images=[];sources=[]
        for i,item in enumerate(originals):
            image=(item.get('url') or item.get('contentUrl')) if isinstance(item,dict) else item
            if not isinstance(image,str) or not image:continue
            image=urljoin(url,image)
            if placeholder(image):warn('placeholder_image','Placeholder image rejected');continue
            if image not in images:
                images.append(image);pointer='/image/'+str(i) if isinstance(original,list) else '/image'
                if isinstance(item,dict):pointer+='/'+('url' if item.get('url') else 'contentUrl')
                mapped=p.get('_field_sources',{}).get(pointer)
                sources.append(mapped or {'capture_path':pointer,'_capture':p.get('_capture',{})})
        if p is owner:
            for i,image in enumerate(gallery):
                if not placeholder(image) and image not in images:
                    images.append(image);sources.append({'capture_path':'/dom/gallery/'+str(i),'_capture':source})
        if len(images)>max_images:warn('image_budget_reached','Image retention budget reached')
        images=images[:max_images];sources=sources[:max_images]
        if images:
            # Retain scalar source shape where unchanged; list projection maps each selected input.
            unchanged=isinstance(original,str) and len(images)==1 and images[0]==original
            if not unchanged:
                p['image']=images
                for i,item in enumerate(sources):p.setdefault('_field_sources',{})['/image/'+str(i)]=item
            if 'og:title' in p:
                p['og:image']=images[0]
                p.setdefault('_field_sources',{})['/og:image']=sources[0]
        else:p['image']='';p.pop('og:image',None)
    if owner is not None:
        for crumb,origin_pointer in breadcrumbs:
            items=crumb.get('itemListElement')
            normalized=[]
            if isinstance(items,list):
                for item in items:
                    if not isinstance(item,dict):break
                    link=item.get('item');link_data=link if isinstance(link,dict) else {}
                    name=item.get('name') or link_data.get('name')
                    address=link if isinstance(link,str) else link_data.get('@id') or link_data.get('url')
                    if type(item.get('position')) is not int or item['position']<1 or not isinstance(name,str):break
                    normalized.append({'position':item['position'],'name':name,'item':address})
            if not isinstance(items,list) or len(normalized)!=len(items) or len({i['position'] for i in normalized})!=len(normalized):
                warn('breadcrumb_invalid','Breadcrumb positions/names invalid');continue
            origin=urlsplit(url).scheme+'://'+urlsplit(url).netloc+'/'
            ordered=sorted(normalized,key=lambda x:x['position'])
            category=[i['name'] for i in ordered if i.get('item') not in (origin,url)]
            if category and not owner.get('category'):
                captured=capture({'dom':{'category':category,'breadcrumbs':ordered}},url,'html_breadcrumb')['_capture']
                bind(owner,'category',category,captured,'/dom/category')
        crumbs=soup.select(_BREADCRUMB)
        if not owner.get('category') and crumbs:
            origin=urlsplit(url).scheme+'://'+urlsplit(url).netloc+'/'
            trail=[(c.get_text(' ',strip=True),urljoin(url,c.a['href']) if c.a and c.a.get('href') else None) for c in crumbs]
            # Drop the home link and the unlinked current page that closes the trail.
            if trail and trail[-1][1] is None:trail=trail[:-1]
            category=[name for name,address in trail if name and address not in (origin,url)]
            if len(category)>16:warn('breadcrumb_invalid','Breadcrumb exceeds retained depth')
            elif category:
                captured=capture({'dom':{'category':category}},url,'html_breadcrumb')['_capture']
                bind(owner,'category',category,captured,'/dom/category')
    from .extractors._product_html import enrich_product_html
    enrich_product_html(products,html,url,include_brand=not any(i['code']=='conflicting_brand' for i in issues))
    return StructuredHTMLResult(products,issues)
