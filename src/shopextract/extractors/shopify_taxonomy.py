"""Explicit versioned category supplement; public product/variant evidence is retained."""
from dataclasses import dataclass,field
from urllib.parse import urlsplit
import httpx
from ._storefront import request,storefront_client,stateless_cookies
from .._capture import capture
from ..categories.native import native_body,localize_category_errors

SHOPIFY_TAXONOMY_QUERY='''query ShopifyTaxonomyProduct($handle: String!) {
  product(handle: $handle) { id title handle productType category { id name } }
}'''


def valid_handle(value):
    return isinstance(value,str) and 0<len(value)<=255 and not any(ord(c)<32 or ord(c)==127 for c in value)


@dataclass(frozen=True)
class ShopifyStorefrontConfig:
    endpoint: str
    access_token: str | None = field(default=None,repr=False)
    api_version: str = '2026-10'
    auth_mode: str = 'token'

    def __post_init__(self):
        p=urlsplit(self.endpoint)
        if (self.api_version!='2026-10' or p.scheme!='https' or not p.hostname or p.username or p.password
            or p.query or p.fragment or p.path!='/api/'+self.api_version+'/graphql.json'):
            raise ValueError('Explicit versioned HTTPS Shopify Storefront endpoint required')
        if self.auth_mode=='token':
            if not isinstance(self.access_token,str) or not self.access_token.strip() or any(ord(c)<32 for c in self.access_token):
                raise ValueError('Token mode requires supplied Storefront token')
        elif self.auth_mode=='tokenless':
            if self.access_token is not None:raise ValueError('Tokenless mode requires no token')
        else:raise ValueError('Unknown Shopify Storefront authentication mode')


def _unavailable(raw,code):
    raw.setdefault('_category_diagnostics',[]).append({'path':['category'],'code':code})


async def supplement_categories(products,config,*,client=None):
    if not isinstance(config,ShopifyStorefrontConfig):raise TypeError('ShopifyStorefrontConfig required')
    # Reject inherited auth, even token mode: supplied runtime config is sole authority.
    if client is not None and (client.auth is not None or any(k.lower() in
        ('authorization','cookie','x-shopify-storefront-access-token','shopify-storefront-private-token') for k in client.headers)
        or client.cookies):raise ValueError('Conflicting inherited Storefront credentials')
    headers={'X-Shopify-Storefront-Access-Token':config.access_token} if config.auth_mode=='token' else {}
    async with storefront_client(client,10,{'User-Agent':'ShopExtract/0.1.2'},cookies=stateless_cookies()) as wire:
        for raw in products:
            # A caller-owned client may accept response cookies. Never replay
            # those on a later product; owned/native clients reject persistence.
            if wire.cookies:
                _unavailable(raw,'category_client_credentials');continue
            handle=raw.get('handle');native=raw.get('id')
            if not valid_handle(handle) or type(native) not in (str,int) or isinstance(native,bool):
                _unavailable(raw,'category_product_identity_unavailable');continue
            try:
                response=await request(wire,'POST',config.endpoint,headers=headers,
                    json={'query':SHOPIFY_TAXONOMY_QUERY,'variables':{'handle':handle}})
                body=native_body(response,include_categories=True)
                node=body['data'].get('product')
                expected=str(native) if str(native).startswith('gid://shopify/Product/') else 'gid://shopify/Product/'+str(native)
                if not isinstance(node,dict) or node.get('id')!=expected or node.get('handle')!=handle:
                    _unavailable(raw,'category_product_identity_mismatch');continue
                localized=localize_category_errors(body['_category_errors'],product_path=('product',))
                if any(e.path is None or not e.path or e.path[0] in ('id','handle') for e in localized):
                    _unavailable(raw,'category_join_source_error');continue
                observed=capture(dict(node),str(response.url),'shopify_storefront_category')
                if 'category' in node:
                    raw['category']=node['category']
                    for path in ('/category','/category/id','/category/name'):
                        raw.setdefault('_field_sources',{})[path]={'capture_path':path,'_capture':observed['_capture']}
                # Only this independently captured projection belongs to the
                # supplement. Public type/collection facts retain their source.
                for error in localized:
                    if error.path and error.path[0]=='category':
                        raw.setdefault('_category_diagnostics',[]).append({'path':list(error.path),'code':error.code})
            except (httpx.HTTPError,ValueError,KeyError,TypeError):
                _unavailable(raw,'category_source_unavailable')
    return products
