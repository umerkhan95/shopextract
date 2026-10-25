"""One bounded offline official-source importer smoke; no download or pipeline sweep."""
import json
from pathlib import Path
import resource
import signal
import time
from dataclasses import asdict

from shopextract.taxonomies.shopify import load_shopify_taxonomy
from shopextract.taxonomies.shopify.build import build_shopify_taxonomy
from shopextract.taxonomies.shopify.contracts import DownloadedRelease,ShopifyReleaseSource
from shopextract.taxonomies.shopify.publish import publish_shopify_taxonomy


def main():
    out=Path('artifacts/shopify-taxonomy');started=time.monotonic()
    status={'state':'started','provenance':'offline real importer over actual saved official sources','request_count':0,
        'limits':{'seconds':60,'peak_rss_bytes':768*1024*1024},
        'baseline_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    def save():
        status.update(seconds=round(time.monotonic()-started,3),peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        (out/'full-import-smoke.json').write_text(json.dumps(status,indent=2)+'\n')
    def expired(*args):raise TimeoutError('One-time import60s watchdog')
    signal.signal(signal.SIGALRM,expired);signal.alarm(60);save()
    try:
        source=ShopifyReleaseSource('2026-08','2e9aa2e9b882383952c63d212add13eb80f46cf9',
            'ee77e261eba2f0ab4375a42b95e9d1bec00779e1f3311d0e9eb6d16f05cf4c09',
            '91ef3829a6621fbc98b46c6447c9702e394fd7c55bfbd56fd2df0545ea9e16b6',
            '6a2261660cc6cb406ed6ef788347d8cb35e939f4537def9e699abf88ed025273')
        cache=Path('downloads/shopify-taxonomy/2026-08')
        downloaded=DownloadedRelease(source,cache/'taxonomy.en.json.gz',cache/'attributes.source.yml',out/'LICENSE')
        staged=build_shopify_taxonomy(downloaded,staging_root=Path('build/shopify-taxonomy/staging'))
        status.update(state='imported',fingerprint=staged.manifest.fingerprint,counts=asdict(staged.manifest.counts),
            resource_bytes=(staged.path/'catalog.json.gz').stat().st_size);save()
        manifest=publish_shopify_taxonomy(staged,catalog_root=Path('build/shopify-taxonomy/catalogs'))
        catalog=load_shopify_taxonomy(catalog_root=Path('build/shopify-taxonomy/catalogs'),fingerprint=manifest.fingerprint)
        assert catalog.category('el-6-6').name=='Laptops'
        assert len(catalog.attributes_for('el-6-6'))==19
        assert len(tuple(catalog.iter_categories()))==14606
        assert len(tuple(catalog.iter_attributes()))==8556
        assert len(tuple(catalog.iter_values()))==74820
        assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss<=768*1024*1024
        status.update(state='passed',loaded_manifest=str(Path('build/shopify-taxonomy/catalogs')/manifest.release/manifest.fingerprint/'manifest.json'))
        save();print(json.dumps(status,indent=2))
    except BaseException as error:
        status.update(state='failed',reason=type(error).__name__+': '+str(error));save();raise
    finally:signal.alarm(0)


if __name__=='__main__':main()
