"""Verify and assemble preprepared taxonomy bytes; no app import/network/build algorithm."""
import importlib.util,json
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def prepared_resource(root):
    root=Path(root);package=root/'src/shopextract/taxonomies/shopify'
    try:
        spec=importlib.util.spec_from_file_location('shopify_resource_verifier',package/'resource.py')
        verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
        pin=json.loads((package/'pin.json').read_text())
        embedded=package/'data'
        directory=embedded if (embedded/'manifest.json').is_file() else root/'build/shopify-taxonomy/catalogs'/pin['release']/pin['fingerprint']
        verifier.verify_resource_files(directory,expected=pin)
        return directory
    except (ValueError,OSError,ImportError,AttributeError) as error:
        raise ValueError('Pinned taxonomy missing or invalid; prepare explicitly with python -m shopextract.taxonomies.shopify.prepare --source-cache PATH (taxonomy-build extra required)') from error


class CustomBuildHook(BuildHookInterface):
    def initialize(self,version,build_data):
        directory=prepared_resource(self.root)
        prefix='shopextract/taxonomies/shopify/data' if self.target_name=='wheel' else 'src/shopextract/taxonomies/shopify/data'
        for name in ('manifest.json','catalog.json.gz','LICENSE'):
            build_data.setdefault('force_include',{})[str(directory/name)]=prefix+'/'+name
