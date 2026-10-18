"""Cold checkout delivery sequence; no actual dependency/source download."""
import importlib.util,json,subprocess,sys
from pathlib import Path
import pytest
from tests.test_shopify_taxonomy_data import build

ROOT=Path(__file__).resolve().parents[1]

def bootstrap():
    path=ROOT/'scripts/bootstrap_taxonomy.py'
    if not path.exists():pytest.fail('Standalone taxonomy delivery bootstrap is missing',pytrace=False)
    spec=importlib.util.spec_from_file_location('taxonomy_bootstrap_test',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def test_metadata_build_requirements_and_real_310_toml_fallback():
    module=bootstrap();metadata=module.read_project(ROOT/'pyproject.toml')
    requirements=module.build_requirements(metadata)
    assert next(v for v in metadata['project']['dependencies'] if v.startswith('httpx')) in requirements
    assert tuple(v for v in requirements if not v.startswith('httpx'))==tuple(metadata['project']['optional-dependencies']['taxonomy-build'])
    assert not any(v.startswith(('crawl4ai','pandas','litellm')) for v in requirements)
    assert module.TOML_SOURCE==('tomli (Hatch backend dependency)' if sys.version_info<(3,11) else 'stdlib.tomllib')


def test_standalone_namespace_uses_checkout_builders_without_application_import(tmp_path):
    module=bootstrap()
    # Actual fresh process, so an installed shopextract package cannot mask eager imports.
    command=[sys.executable,'-c',"import importlib.util,sys;from pathlib import Path;s=importlib.util.spec_from_file_location('bootstrap',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);p=m.load_preparer(Path(sys.argv[2]));assert 'shopextract' not in sys.modules;assert not any(x in sys.modules for x in ['crawl4ai','pandas','litellm']);print(p.__file__)",str(ROOT/'scripts/bootstrap_taxonomy.py'),str(ROOT)]
    result=subprocess.run(command,capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stderr
    assert str(ROOT/'src/shopextract/taxonomies/shopify/prepare.py') in result.stdout


def test_workflows_prepare_before_project_install_and_publish():
    module=bootstrap()
    import yaml
    action=yaml.safe_load((ROOT/'.github/actions/prepare-taxonomy/action.yml').read_text())
    assert 'scripts/bootstrap_taxonomy.py' in str(action)
    for name,following in [('test.yml','pip install -e'),('publish.yml','python -m build')]:
        text=(ROOT/'.github/workflows'/name).read_text()
        assert text.index('uses: ./.github/actions/prepare-taxonomy')<text.index(following)
        assert 'allow-download: "true"' in text


def cold_tree(tmp_path,pin):
    import shutil
    root=tmp_path/'checkout';root.mkdir()
    shutil.copytree(ROOT/'src',root/'src',ignore=shutil.ignore_patterns('__pycache__','data'))
    for name in ('pyproject.toml','hatch_build.py','README.md','LICENSE'):shutil.copyfile(ROOT/name,root/name)
    (root/'scripts').mkdir();shutil.copyfile(ROOT/'scripts/bootstrap_taxonomy.py',root/'scripts/bootstrap_taxonomy.py')
    # If bootstrap executes this checkout's application __init__, preparation
    # fails. Unique fixture pin also prevents resolving installed worktree data.
    (root/'src/shopextract/__init__.py').write_text('raise RuntimeError("Application import forbidden during standalone build")\n')
    (root/'src/shopextract/taxonomies/shopify/pin.json').write_text(json.dumps(pin))
    return root


def test_actual_cold_fixture_bootstrap_then_hook_and_missing_input(tmp_path):
    import os
    module=bootstrap();source=tmp_path/'source';source.mkdir()
    _,staged=build(source);pin=json.loads((staged.path/'manifest.json').read_text())
    root=cold_tree(tmp_path,pin)
    spec=importlib.util.spec_from_file_location('cold_hook_test',root/'hatch_build.py')
    hook=importlib.util.module_from_spec(spec);spec.loader.exec_module(hook)
    with pytest.raises(ValueError,match='prepare'):hook.prepared_resource(root)
    env=dict(os.environ);env['PYTHONPATH']=str(root/'src')
    command=[sys.executable,str(root/'scripts/bootstrap_taxonomy.py'),'--offline','--source-cache',str(source)]
    result=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=45)
    assert result.returncode==0,result.stdout+result.stderr
    directory=hook.prepared_resource(root)
    assert json.loads((directory/'manifest.json').read_text())==pin
    assert directory.is_relative_to(root/'build')
    bad=subprocess.run([*command[:-1],str(root/'missing')],cwd=root,env=env,capture_output=True,text=True,timeout=20)
    assert bad.returncode!=0 and 'Pinned sources unavailable' in bad.stderr
    original=(source/'taxonomy.en.json.gz').read_bytes()
    try:
        (source/'taxonomy.en.json.gz').write_bytes(b'corrupted local source')
        corrupted=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=20)
        assert corrupted.returncode!=0 and 'Pinned source hash mismatch' in corrupted.stderr
    finally:(source/'taxonomy.en.json.gz').write_bytes(original)
    # Data and source pin remain unchanged after either failure.
    assert json.loads((directory/'manifest.json').read_text())==pin
    assert json.loads((root/'src/shopextract/taxonomies/shopify/pin.json').read_text())==pin
