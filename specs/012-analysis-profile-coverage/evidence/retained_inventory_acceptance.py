"""Explicit retained-corpus acceptance; not the fresh-checkout pytest suite.

Run after implementation: PYTHONPATH=src python PATH --source-dir DIR.
Never skips missing inputs; missing/changed pinned corpus is a failure.
"""
import argparse
import hashlib
import json
from pathlib import Path
from shopextract.maintenance.inventory import build_inventory, REFERENCE_IDS

EXPECTED_FILES = {
    'el_electronics.yml': (555297, '08f92912aac14164afbd7704067c586499da9f5591df96def1a25adda908469f'),
    'aa_apparel_accessories.yml': (285314, '3746bf9fab3920b9f529caef076f91225b4f954e6f7e238668aaf49ed90419a6'),
    'hg_home_garden.yml': (877783, '355d32fbc787812c83ff5446dbe7d964d798f8508ec95ee5306f07da8e907a35'),
    'attributes.yml': (4769315, '91ef3829a6621fbc98b46c6447c9702e394fd7c55bfbd56fd2df0545ea9e16b6'),
    'LICENSE': (1046, '6a2261660cc6cb406ed6ef788347d8cb35e939f4537def9e699abf88ed025273'),
}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-dir',required=True,type=Path)
    parser.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args()
    for name,(size,digest) in EXPECTED_FILES.items():
        data=(args.source_dir/name).read_bytes()
        assert len(data)==size and hashlib.sha256(data).hexdigest()==digest
    print('Pinned source identity: 5 files verified',flush=True)
    smoke=build_inventory(args.source_dir,selected_ids=REFERENCE_IDS)
    rows={r['category_id']:r for r in smoke['rows']}
    assert [len(rows[key]['declared_attributes']) for key in REFERENCE_IDS]==[19,16,10]
    assert smoke['denominator']['category_nodes']==4125
    assert smoke['denominator']['branch_nodes']=={'aa_apparel_accessories.yml':663,'el_electronics.yml':1176,'hg_home_garden.yml':2286}
    assert smoke['summary']['reviewed_policy_family_count']==0
    assert smoke['summary']['remaining_profile_count'] is None
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'inventory-smoke.json').write_text(json.dumps(smoke,sort_keys=True,indent=2)+'\n')
    print('Three-reference smoke passed and saved',flush=True)
    full=build_inventory(args.source_dir)
    assert len(full['rows'])==4125
    assert full['summary']['backlog_counts']=={'binding_only':0,'existing_extension':2,'new_profile':1,'review_pending':4122}
    assert full==build_inventory(args.source_dir,branch_files=reversed(tuple(full['denominator']['branch_nodes'])))
    (args.output_dir/'coverage-matrix.json').write_text(json.dumps(full,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'passed','source_files':5,'category_nodes':4125,'network_requests':0,'model_calls':0}))


if __name__=='__main__':main()
