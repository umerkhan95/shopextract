"""Explicit source/release preparation; normal installation and lookup never invoke it."""
import argparse,asyncio,json
from pathlib import Path
from .contracts import DownloadedRelease,ShopifyReleaseSource,StagedTaxonomy,TaxonomyPublicationError
from .resource import verify_resource_files


def pinned_source():
    pin=json.loads(Path(__file__).with_name('pin.json').read_text())
    hashes=dict(pin['source_hashes'])
    return ShopifyReleaseSource(pin['release'],pin['commit'],hashes['taxonomy.en.json.gz'],hashes['attributes.yml'],hashes['LICENSE'])


def prepare_shopify_taxonomy_build(*,source,source_cache=None,build_root,allow_download=False):
    from .build import build_shopify_taxonomy
    from .publish import publish_shopify_taxonomy
    cache=Path(source_cache) if source_cache is not None else None
    if cache is not None and all((cache/n).is_file() for n in ('taxonomy.en.json.gz','attributes.yml','LICENSE')):
        downloaded=DownloadedRelease(source,*(cache/n for n in ('taxonomy.en.json.gz','attributes.yml','LICENSE')))
    elif allow_download:
        from .download import download_shopify_taxonomy_release
        downloaded=asyncio.run(download_shopify_taxonomy_release(source,staging_root=Path(build_root)/'sources'))
    else:raise TaxonomyPublicationError('Pinned sources unavailable; prepare with verified local sources or explicit --allow-download')
    staged=build_shopify_taxonomy(downloaded,staging_root=Path(build_root)/'staging')
    root=Path(build_root)/'catalogs'
    publish_shopify_taxonomy(staged,catalog_root=root)
    path=root/source.version/staged.manifest.fingerprint
    verify_resource_files(path)
    return StagedTaxonomy(path,staged.manifest)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache',type=Path);parser.add_argument('--build-root',type=Path,default=Path('build/shopify-taxonomy'))
    parser.add_argument('--allow-download',action='store_true');args=parser.parse_args()
    staged=prepare_shopify_taxonomy_build(source=pinned_source(),source_cache=args.source_cache,build_root=args.build_root,allow_download=args.allow_download)
    print(json.dumps({'resource':str(staged.path),'fingerprint':staged.manifest.fingerprint}))

if __name__=='__main__':main()
