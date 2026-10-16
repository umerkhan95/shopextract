"""Runtime fixture-byte ledger, separate from RSS and retained verification logs."""
from collections import Counter
import json
import pytest

ACTIVE = None


def charge(category, amount):
    if ACTIVE is not None:
        assert type(amount) is int and amount >= 0
        ACTIVE[category] += amount


class FixtureBytesPlugin:
    """Measure actual boundary bytes; count repeated representations conservatively."""
    def __init__(self):
        self.counts=Counter();self.originals=[]

    def pytest_sessionstart(self,session):
        global ACTIVE
        ACTIVE=self.counts
        import httpx
        from shopextract.tools.state import RetainedGraph,SessionStore
        response_init=httpx.Response.__init__
        graph_init=RetainedGraph.__init__
        publish=SessionStore.publish
        def measured_response(obj,*args,**kwargs):
            data=kwargs.get('content')
            if kwargs.get('json') is not None:
                data=json.dumps(kwargs['json'],ensure_ascii=False,separators=(',',':')).encode()
            elif kwargs.get('text') is not None:
                data=kwargs['text'].encode('utf-8')
            if isinstance(data,str):data=data.encode('utf-8')
            if isinstance(data,(bytes,bytearray)):
                charge('http_response_representation',len(data))
            return response_init(obj,*args,**kwargs)
        def measured_graph(obj,*args,**kwargs):
            graph_init(obj,*args,**kwargs)
            charge('constructed_graph_representation',obj.size)
        def measured_publish(obj,job,graph):
            charge('publication_graph_representation',graph.size)
            return publish(obj,job,graph)
        self.originals=[(httpx.Response,'__init__',response_init),(RetainedGraph,'__init__',graph_init),(SessionStore,'publish',publish)]
        httpx.Response.__init__=measured_response
        RetainedGraph.__init__=measured_graph
        SessionStore.publish=measured_publish

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self,item,call):
        result=yield
        if call.when=='call':
            path=item.funcargs.get('tmp_path')
            if path:
                charge('generated_fixture_files',sum(f.stat().st_size for f in path.rglob('*') if f.is_file()))

    def pytest_sessionfinish(self,session,exitstatus):
        global ACTIVE
        for owner,name,value in reversed(self.originals):setattr(owner,name,value)
        ACTIVE=None
