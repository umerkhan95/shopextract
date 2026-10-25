"""Explicit bounded acquisition from pinned official Shopify release/source URLs."""
import asyncio,hashlib,time
from pathlib import Path
from urllib.parse import urljoin,urlsplit
import httpx
from .contracts import DownloadedRelease,TaxonomyIntegrityError
from .resource import safe_release,hex_digest


async def download_shopify_taxonomy_release(source, *, staging_root):
    safe_release(source.version);hex_digest(source.commit,length=40)
    for value in (source.taxonomy_sha256,source.extensions_sha256,source.license_sha256):hex_digest(value)
    root=Path(staging_root);root.mkdir(parents=True,exist_ok=True)
    urls=[('taxonomy.en.json.gz',f'https://github.com/Shopify/product-taxonomy/releases/download/v{source.version}/taxonomy.en.json.gz',source.taxonomy_sha256,8*1024*1024),
        ('attributes.yml',f'https://raw.githubusercontent.com/Shopify/product-taxonomy/{source.commit}/data/attributes.yml',source.extensions_sha256,8*1024*1024),
        ('LICENSE',f'https://raw.githubusercontent.com/Shopify/product-taxonomy/{source.commit}/LICENSE',source.license_sha256,8192)]
    count=0;start=time.monotonic();paths=[]
    async def acquire():
        nonlocal count
        async with httpx.AsyncClient(timeout=10,follow_redirects=False,trust_env=False) as client:
            for name,url,expected,cap in urls:
                path=root/name;temp=root/(name+'.partial')
                try:
                    for redirects in range(4):
                        p=urlsplit(url)
                        if p.scheme!='https' or p.hostname not in {'github.com','raw.githubusercontent.com','release-assets.githubusercontent.com','objects.githubusercontent.com'} or p.username or p.password or p.fragment:
                            raise TaxonomyIntegrityError('Taxonomy download source denied')
                        if count>=8 or time.monotonic()-start>=60:raise TaxonomyIntegrityError('Taxonomy download budget reached')
                        count+=1
                        async with client.stream('GET',url,headers={'Accept-Encoding':'identity'}) as response:
                            if response.is_redirect:
                                if redirects==3:raise TaxonomyIntegrityError('Taxonomy redirect limit reached')
                                url=urljoin(url,response.headers['location']);continue
                            response.raise_for_status();size=0;digest=hashlib.sha256()
                            with temp.open('wb') as output:
                                async for chunk in response.aiter_bytes():
                                    size+=len(chunk)
                                    if size>cap:raise TaxonomyIntegrityError('Taxonomy download byte cap reached')
                                    digest.update(chunk);output.write(chunk)
                            if digest.hexdigest()!=expected:raise TaxonomyIntegrityError('Taxonomy source hash mismatch')
                            temp.replace(path);paths.append(path);break
                finally:temp.unlink(missing_ok=True)
    try:await asyncio.wait_for(acquire(),timeout=60)
    except (httpx.HTTPError,asyncio.TimeoutError,OSError) as error:raise TaxonomyIntegrityError('Pinned taxonomy acquisition failed') from error
    return DownloadedRelease(source,*paths)
