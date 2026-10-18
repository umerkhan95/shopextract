"""Explicit updater HTTP byte/hash/source limits, no actual network."""
import hashlib
import httpx,pytest
from shopextract.taxonomies.shopify.contracts import ShopifyReleaseSource,TaxonomyIntegrityError
from shopextract.taxonomies.shopify.download import download_shopify_taxonomy_release

@pytest.mark.parametrize('fault',['none','hash','redirect','redirect_budget','bytes'])
async def test_bounded_official_download(tmp_path,monkeypatch,fault):
    blobs={'taxonomy.en.json.gz':b'gzip-fixture','attributes.yml':b'yaml-fixture','LICENSE':b'MIT fixture'}
    source=ShopifyReleaseSource('fixture','0'*40,*(hashlib.sha256(blobs[n]).hexdigest() for n in blobs))
    sent=[]
    def wire(request):
        sent.append(request)
        if fault=='redirect':return httpx.Response(302,headers={'location':'https://attacker.test/source'})
        if fault=='redirect_budget':return httpx.Response(302,headers={'location':str(request.url)})
        name=request.url.path.rsplit('/',1)[-1];body=blobs[name]
        if fault=='hash':body=b'damaged'
        if fault=='bytes':body=b'x'*(8*1024*1024+1)
        return httpx.Response(200,content=body)
    original=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(wire),**kw))
    if fault=='none':
        result=await download_shopify_taxonomy_release(source,staging_root=tmp_path)
        assert result.taxonomy_path.read_bytes()==blobs['taxonomy.en.json.gz'] and len(sent)==3
    else:
        with pytest.raises(TaxonomyIntegrityError):await download_shopify_taxonomy_release(source,staging_root=tmp_path)
        assert not list(tmp_path.glob('*.partial')) and len(sent)<=4
