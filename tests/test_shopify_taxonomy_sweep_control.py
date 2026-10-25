"""Tiny bounded runner proofs; never import/load the full catalog."""
import os,sys
from pathlib import Path
import pytest
from tests.shopify_taxonomy_sweep import monitor,validate_progress


def test_aggregate_timeout_kills_and_waits_child(tmp_path):
    record=monitor([sys.executable,'-c',"import os,time;open('"+str(tmp_path/'pid')+"','w').write(str(os.getpid()));time.sleep(10)"],tmp_path,{'attempt':'fixture'},seconds=.2,batch_seconds=2)
    assert record['state']=='failed' and record['reason']=='aggregate_timeout' and record['seconds']<3
    pid=int((tmp_path/'pid').read_text())
    with pytest.raises(ProcessLookupError):os.kill(pid,0)


def test_independent_rss_limit_stops_child(tmp_path):
    record=monitor([sys.executable,'-c','import time;x=bytearray(16000000);time.sleep(10)'],tmp_path,{'attempt':'fixture'},seconds=3,rss_bytes=1024*1024,batch_seconds=2)
    assert record['reason']=='rss_limit' and record['peak_sampled_group_rss_bytes']>1024*1024


def test_batch_watchdog_is_separate_from_aggregate(tmp_path):
    record=monitor([sys.executable,'-c','import time;time.sleep(10)'],tmp_path,{},seconds=3,batch_seconds=.2)
    assert record['reason']=='batch_timeout' and record['seconds']<3


def test_stale_attempt_refuses_start_and_bound_progress_refuses_other_source(tmp_path):
    (tmp_path/'progress.json').write_text('{}')
    with pytest.raises(ValueError,match='automatic resume forbidden'):
        monitor([sys.executable,'-c','raise AssertionError("must not launch")'],tmp_path,{'fingerprint':'new'})
    with pytest.raises(ValueError,match='stale_progress_binding'):
        validate_progress({'binding':{'fingerprint':'old'},'processed_ids':[],'categories':0},{'fingerprint':'new'},[])
    with pytest.raises(ValueError,match='invalid_processed_ids'):
        validate_progress({'binding':{},'processed_ids':['b'],'categories':1},{},['a'])
