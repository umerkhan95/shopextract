"""Schema.org JSON-LD structured data extractor (static methods only)."""

from __future__ import annotations

import json
import logging

from bs4 import BeautifulSoup
from .._capture import capture

logger = logging.getLogger(__name__)

# Fields that may contain PII
_SCHEMA_ORG_PII_FIELDS = frozenset({
    "review", "reviews", "author", "aggregateRating",
    "creator", "contributor", "editor", "publisher",
    "reviewedBy", "commentCount", "comment",
    "interactionStatistic",
})


class SchemaOrgExtractor:
    """Extract JSON-LD structured data from <script type='application/ld+json'> tags."""

    @staticmethod
    def _is_product_type(type_value) -> bool:
        if isinstance(type_value, str):
            return "Product" in type_value
        if isinstance(type_value, list):
            return any("Product" in str(t) for t in type_value)
        return False

    @staticmethod
    def _strip_pii_fields(product: dict) -> dict:
        return {k: v for k, v in product.items() if k not in _SCHEMA_ORG_PII_FIELDS}

    @staticmethod
    def _has_nonzero_price(offers) -> bool:
        if isinstance(offers, dict):
            try:
                return float(offers.get("price", 0)) > 0
            except (ValueError, TypeError):
                return bool(offers.get("price"))
        if isinstance(offers, list):
            for offer in offers:
                if isinstance(offer, dict):
                    try:
                        if float(offer.get("price", 0)) > 0:
                            return True
                    except (ValueError, TypeError):
                        if offer.get("price"):
                            return True
        return False

    @staticmethod
    def _enrich_product_group(product: dict) -> None:
        """Pull first variant's non-zero offers into a ProductGroup with no direct price."""
        offers = product.get("offers")
        if SchemaOrgExtractor._has_nonzero_price(offers):
            return

        variants = product.get("hasVariant", [])
        if not isinstance(variants, list) or not variants:
            return

        for variant in variants:
            if not isinstance(variant, dict):
                continue
            v_offers = variant.get("offers")
            if isinstance(v_offers, dict):
                try:
                    if float(v_offers.get("price", 0)) > 0:
                        product["offers"] = v_offers
                        return
                except (ValueError, TypeError):
                    if v_offers.get("price"):
                        product["offers"] = v_offers
                        return
            if isinstance(v_offers, list):
                for offer in v_offers:
                    if not isinstance(offer, dict):
                        continue
                    try:
                        if float(offer.get("price", 0)) > 0:
                            product["offers"] = [offer]
                            return
                    except (ValueError, TypeError):
                        if offer.get("price"):
                            product["offers"] = [offer]
                            return

    @staticmethod
    def _extract_og_meta(soup: BeautifulSoup) -> dict[str, str]:
        og_data: dict[str, str] = {}
        for meta in soup.find_all("meta", attrs={"property": True}):
            prop = meta.get("property", "")
            content = meta.get("content", "")
            if prop.startswith("og:") and content:
                og_data[prop] = content.strip()
        return og_data

    @staticmethod
    def extract_from_html(html: str, url: str, *, diagnostics=None, max_nodes=256,
                          max_depth=8, _soup=None, collected_nodes=None) -> list[dict]:
        """Walk bounded JSON-LD blocks and resolve only captured local references."""
        from urllib.parse import urljoin
        from .._product_admission import has_product_evidence
        diagnostics = diagnostics if diagnostics is not None else []
        soup = _soup if _soup is not None else BeautifulSoup(html, 'html.parser')
        products=[]; emitted=set()
        for block,script in enumerate(soup.find_all('script',type='application/ld+json')):
            try:data=json.loads(script.string or script.get_text())
            except (ValueError,TypeError):continue
            stack=[(data,0,'',False)]; nodes=[]; count=0; exceeded=False
            while stack:
                node,depth,pointer,variant=stack.pop()
                if not isinstance(node,(dict,list)):continue
                count+=1
                if count>max_nodes or depth>max_depth:exceeded=True;break
                if isinstance(node,dict):
                    nodes.append((node,pointer,variant))
                    group='ProductGroup' in str(node.get('@type',''))
                    for key,value in reversed(list(node.items())):
                        token=key.replace('~','~0').replace('/','~1')
                        stack.append((value,depth+1,pointer+'/'+token,variant or group and key=='hasVariant'))
                else:
                    for i,value in reversed(list(enumerate(node))):stack.append((value,depth+1,pointer+'/'+str(i),variant))
            if exceeded:
                diagnostics.append({'code':'jsonld_budget_exceeded','message':'JSON-LD block exceeds traversal budget'})
                continue
            if collected_nodes is not None:
                for node,pointer,_ in nodes:
                    types=node.get('@type',[])
                    if isinstance(types,str):types=[types]
                    if isinstance(types,list) and any(isinstance(t,str) and t.rstrip('/').rsplit('/',1)[-1].rsplit(':',1)[-1]=='BreadcrumbList' for t in types):
                        collected_nodes.append((node,'/scripts/'+str(block)+pointer))
            index={urljoin(url,n['@id']):n for n,_,_ in nodes if isinstance(n.get('@id'),str) and len(n)>1}
            def resolve(value,prefix,seen,mapping,depth=0):
                if depth>max_depth:
                    diagnostics.append({'code':'jsonld_budget_exceeded','message':'JSON-LD reference depth exceeded'})
                    return None
                if isinstance(value,list):return [resolve(v,prefix+'/'+str(i),seen,mapping,depth+1) for i,v in enumerate(value)]
                if not isinstance(value,dict):return value
                identifier=value.get('@id')
                if isinstance(identifier,str) and len(value)==1:
                    key=urljoin(url,identifier)
                    if key in seen:return {'@id':identifier}
                    if key not in index and prefix.endswith('/inCodeSet'):
                        return {'@id':identifier}  # Opaque captured taxonomy namespace, not a node fetch.
                    if key not in index:
                        diagnostics.append({'code':'external_reference_ignored','message':'Reference not present in captured document'})
                        return None
                    original=index[key]; captured=capture(dict(original),url,'json_ld_reference')['_capture']
                    for path in captured['values']:
                        mapping[prefix+path]={'capture_path':path,'_capture':captured}
                    return resolve(original,prefix,seen|{key},mapping,depth+1)
                return {k:resolve(v,prefix+'/'+k.replace('~','~0').replace('/','~1'),seen,mapping,depth+1) for k,v in value.items()}
            for original,pointer,variant in nodes:
                if variant or not has_product_evidence(original):continue
                identifier=urljoin(url,original['@id']) if isinstance(original.get('@id'),str) else (block,pointer)
                if identifier in emitted:continue
                emitted.add(identifier)
                raw=SchemaOrgExtractor._strip_pii_fields(dict(original))
                context=capture(dict(raw),url,'json_ld')['_capture']
                context['document_pointer']='/scripts/'+str(block)+pointer
                mapping={}; resolved=resolve(raw,'',{identifier},mapping)
                if not isinstance(resolved,dict):continue
                resolved['_capture']=context
                if mapping:resolved['_field_sources']=mapping
                if 'ProductGroup' in str(raw.get('@type','')):
                    SchemaOrgExtractor._enrich_product_group(resolved)
                    for i,variant_node in enumerate(raw.get('hasVariant') or []):
                        if isinstance(variant_node,dict) and resolved.get('offers')==variant_node.get('offers'):
                            prefix='/hasVariant/'+str(i)+'/offers'
                            for path in context['values']:
                                if path.startswith(prefix):resolved.setdefault('_field_sources',{})['/offers'+path[len(prefix):]]={'capture_path':path,'_capture':context}
                            break
                products.append(SchemaOrgExtractor._strip_pii_fields(resolved))
        return products
