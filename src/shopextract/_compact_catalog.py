"""Bounded, lossless catalog transport with deduplicated capture bodies."""
from dataclasses import dataclass
import copy
import hashlib
import json


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()


@dataclass(frozen=True)
class CompactLimits:
    max_wire_bytes:int=33554432
    max_expanded_bytes:int=33554432
    max_nodes:int=1000000
    max_depth:int=64
    max_records:int=1000

    def __post_init__(self):
        for name,ceiling in [('max_wire_bytes',33554432),('max_expanded_bytes',33554432),
                             ('max_nodes',1000000),('max_depth',64),('max_records',1000)]:
            value=getattr(self,name)
            if type(value) is not int or not 0<value<=ceiling:raise ValueError('Invalid compact limit')


@dataclass(frozen=True)
class _Reference:
    digest:str


def _capture_slot(path):
    if len(path)>=3 and path[0]=='raw_products' and path[1].isdigit():tail=path[2:]
    elif len(path)>=5 and path[0]=='products' and path[1].isdigit() and path[2:4]==('product','raw_data'):tail=path[4:]
    else:return False
    return tail==('_capture',) or (len(tail)==3 and tail[0]=='_field_sources' and tail[-1]=='_capture') or (len(tail)==3 and tail[0]=='_identifier_sources' and tail[1].isdigit() and tail[-1]=='_capture')


def _pairs(pairs):
    out={}
    for key,value in pairs:
        if key in out:raise ValueError('Duplicate compact key')
        out[key]=value
    return out


def _cost(value,limits,bodies=None):
    cache={}
    def visit(item,depth):
        if depth>limits.max_depth:raise ValueError('Compact depth limit')
        if isinstance(item,_Reference):
            if bodies is None or item.digest not in bodies:raise ValueError('Dangling capture reference')
            if item.digest not in cache:cache[item.digest]=visit(bodies[item.digest],0)
            size,nodes,height=cache[item.digest]
            if depth+height>limits.max_depth:raise ValueError('Expanded depth limit')
            return size,nodes,height
        size,nodes,height=0,1,0
        if isinstance(item,dict):
            size=2+max(0,len(item)-1)
            children=[(len(canonical(k))+1,v) for k,v in item.items()]
        elif isinstance(item,list):
            size=2+max(0,len(item)-1);children=[(0,v) for v in item]
        else:return len(canonical(item)),1,0
        for overhead,child in children:
            count,child_nodes,child_height=visit(child,depth+1)
            size+=overhead+count;nodes+=child_nodes;height=max(height,child_height+1)
            if size>limits.max_expanded_bytes or nodes>limits.max_nodes:raise ValueError('Expanded catalog budget')
        return size,nodes,height
    cost=visit(value,0)
    if cost[0]>limits.max_expanded_bytes or cost[1]>limits.max_nodes:raise ValueError('Catalog budget')
    return cost


def encode_compact_catalog(data,*,limits=CompactLimits()):
    _cost(data,limits)
    if not isinstance(data,dict) or not isinstance(data.get('products'),list) or len(data['products'])>limits.max_records:raise ValueError('Invalid catalog records')
    captures={}
    def escape(value,dedup,path=()):
        if isinstance(value,list):return [escape(v,dedup,path+(str(i),)) for i,v in enumerate(value)]
        if not isinstance(value,dict):return value
        if set(value) in ({'$capture_ref'},{'$literal'}):
            return {'$literal':[[k,escape(v,False)] for k,v in value.items()]}
        out={}
        for key,item in value.items():
            if dedup and _capture_slot(path+(key,)) and isinstance(item,dict):
                digest=hashlib.sha256(canonical(item)).hexdigest()
                captures.setdefault(digest,escape(item,False));out[key]={'$capture_ref':digest}
            else:out[key]=escape(item,dedup,path+(key,))
        return out
    encoded=escape(data,True)
    result={'schema_version':'catalog-1','data':encoded,'captures':captures}
    wire=canonical(result)
    if len(wire)>limits.max_wire_bytes:raise ValueError('Compact wire byte budget')
    _cost(result,CompactLimits(max_expanded_bytes=limits.max_wire_bytes,max_nodes=limits.max_nodes,max_depth=limits.max_depth,max_records=limits.max_records))
    return wire


def decode_compact_catalog(payload,*,limits=CompactLimits()):
    try:
        if not isinstance(payload,bytes) or len(payload)>limits.max_wire_bytes:raise ValueError('Compact wire byte budget')
        from ._bounded_json import preflight_catalog_json
        preflight_catalog_json(payload,max_bytes=limits.max_wire_bytes,max_nodes=limits.max_nodes,max_depth=limits.max_depth)
        envelope=json.loads(payload,object_pairs_hook=_pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))
        _cost(envelope,CompactLimits(max_expanded_bytes=limits.max_wire_bytes,max_nodes=limits.max_nodes,max_depth=limits.max_depth,max_records=limits.max_records))
        if set(envelope)!={'schema_version','data','captures'} or envelope['schema_version']!='catalog-1' or not isinstance(envelope['captures'],dict):raise ValueError('Invalid compact envelope')
        def unescape(value,allow_refs,path=()):
            if isinstance(value,list):return [unescape(v,allow_refs,path+(str(i),)) for i,v in enumerate(value)]
            if not isinstance(value,dict):return value
            if set(value)=={'$literal'}:
                pairs=value['$literal']
                if not isinstance(pairs,list) or any(not isinstance(p,list) or len(p)!=2 or not isinstance(p[0],str) for p in pairs):raise ValueError('Invalid literal escape')
                return _pairs([(k,unescape(v,False)) for k,v in pairs])
            if set(value)=={'$capture_ref'}:
                if not allow_refs or not _capture_slot(path) or not isinstance(value['$capture_ref'],str):raise ValueError('Nested/cyclic capture reference')
                return _Reference(value['$capture_ref'])
            return {k:unescape(v,allow_refs,path+(k,)) for k,v in value.items()}
        bodies={}
        for digest,body in envelope['captures'].items():
            plain=unescape(body,False)
            if hashlib.sha256(canonical(plain)).hexdigest()!=digest:raise ValueError('Capture hash mismatch')
            bodies[digest]=plain
        data=unescape(envelope['data'],True)
        if not isinstance(data,dict) or not isinstance(data.get('products'),list) or len(data['products'])>limits.max_records:raise ValueError('Invalid compact records')
        _cost(data,limits,bodies)
        def hydrate(value):
            if isinstance(value,_Reference):
                if value.digest not in bodies:raise ValueError('Dangling capture reference')
                return copy.deepcopy(bodies[value.digest])
            if isinstance(value,dict):return {k:hydrate(v) for k,v in value.items()}
            if isinstance(value,list):return [hydrate(v) for v in value]
            return value
        return hydrate(data)
    except (TypeError,KeyError,RecursionError,UnicodeError) as error:raise ValueError('Invalid compact catalog') from error
