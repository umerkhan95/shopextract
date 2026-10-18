"""Explicit checkout preparation, without importing the application package."""
import argparse
import importlib
import importlib.machinery
import subprocess
import sys
import types
from pathlib import Path

try:
    import tomllib
    TOML_SOURCE='stdlib.tomllib'
except ModuleNotFoundError:
    # Hatch declares tomli for Python<3.11; installed build tooling supplies it.
    import tomli as tomllib
    TOML_SOURCE='tomli (Hatch backend dependency)'


def read_project(path):
    with Path(path).open('rb') as source:return tomllib.load(source)


def build_requirements(metadata):
    from packaging.requirements import Requirement
    project=metadata['project']
    # Reuse the exact declared HTTP client constraint; do not copy it into CI or
    # install the application's unrelated runtime dependency set for a build.
    http=[value for value in project['dependencies'] if Requirement(value).name.lower()=='httpx']
    if len(http)!=1:raise ValueError('Exactly one declared httpx build transport required')
    return tuple(dict.fromkeys(http+project['optional-dependencies']['taxonomy-build']))


def load_preparer(root):
    directory=(Path(root)/'src/shopextract/taxonomies/shopify').resolve()
    name='_shopextract_taxonomy_build'
    if name in sys.modules:raise RuntimeError('Build namespace already in use')
    package=types.ModuleType(name)
    package.__path__=[str(directory)];package.__package__=name
    package.__spec__=importlib.machinery.ModuleSpec(name,loader=None,is_package=True)
    sys.modules[name]=package
    # Relative imports execute the SAME source files, without either application
    # __init__. Nothing is registered under the real shopextract namespace.
    prepared=importlib.import_module(name+'.prepare')
    if Path(prepared.__file__).resolve()!=directory/'prepare.py':raise RuntimeError('Unexpected preparation module')
    return prepared


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache',type=Path)
    parser.add_argument('--build-root',type=Path,default=Path('build/shopify-taxonomy'))
    parser.add_argument('--allow-download',action='store_true')
    parser.add_argument('--offline',action='store_true',help='No pip index or taxonomy network; use local verified source files')
    args=parser.parse_args(argv)
    if args.offline and args.allow_download:parser.error('--offline cannot allow downloads')
    root=Path(__file__).resolve().parents[1]
    command=[sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input']
    if args.offline:command.append('--no-index')
    command.extend(build_requirements(read_project(root/'pyproject.toml')))
    subprocess.run(command,check=True,timeout=90)
    prepare=load_preparer(root)
    sys.argv=[str(root/'src/shopextract/taxonomies/shopify/prepare.py'),'--build-root',str(args.build_root)]
    if args.source_cache is not None:sys.argv+=['--source-cache',str(args.source_cache)]
    if args.allow_download:sys.argv.append('--allow-download')
    prepare.main()


if __name__=='__main__':main()
