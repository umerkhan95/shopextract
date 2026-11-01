"""Allocation-light lexical budgets before catalog JSON object decoding."""
from dataclasses import dataclass
import re

_STRING_SPECIAL=re.compile(r'["\\\x00-\x1f]')
_NUMBER=re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')
@dataclass(frozen=True)
class JSONShape:
    nodes:int
    keys:int
    tokens:int
    depth:int


def preflight_catalog_json(payload,*,max_bytes=33554432,max_nodes=1000000,max_tokens=2000000,max_depth=64):
    if not isinstance(payload,bytes) or len(payload)>max_bytes:raise ValueError('Catalog byte budget')
    for value,ceiling in ((max_bytes,33554432),(max_nodes,1000000),(max_tokens,2000000),(max_depth,64)):
        if type(value) is not int or not 0<value<=ceiling:raise ValueError('Invalid catalog limit')
    text=payload.decode('utf-8');stack=[];nodes=keys=depth=0;i=0
    def value():
        nonlocal nodes,depth
        nodes+=1;depth=max(depth,len(stack))
        if nodes>max_nodes or nodes+keys>max_tokens or depth>max_depth:raise ValueError('Catalog lexical budget')
        if stack and stack[-1][0]=='{':stack[-1][1]='separator'
    while i<len(text):
        c=text[i]
        if c.isspace():i+=1;continue
        if c=='"':
            is_key=bool(stack and stack[-1][0]=='{' and stack[-1][1]=='key')
            if is_key:
                keys+=1
                if nodes+keys>max_tokens:raise ValueError('Catalog token budget')
                stack[-1][1]='colon'
            else:value()
            i+=1
            while True:
                special=_STRING_SPECIAL.search(text,i)
                if special is None:raise ValueError('Unterminated JSON string')
                j=special.start()
                if text[j]=='\\':i=j+2;continue
                if text[j]!='"':raise ValueError('Invalid JSON string')
                i=j+1;break
            continue
        if c in '{[':
            value();stack.append([c,'key' if c=='{' else 'value']);i+=1;continue
        if c in '}]':
            if not stack or stack[-1][0]!=('{' if c=='}' else '['):raise ValueError('JSON structure mismatch')
            stack.pop();i+=1;continue
        if c==':':
            if not stack or stack[-1][0]!='{':raise ValueError('Unexpected colon')
            stack[-1][1]='value';i+=1;continue
        if c==',':
            if not stack:raise ValueError('Unexpected comma')
            stack[-1][1]='key' if stack[-1][0]=='{' else 'value';i+=1;continue
        match=_NUMBER.match(text,i)
        if match:value();i=match.end();continue
        for literal in ('true','false','null'):
            if text.startswith(literal,i):value();i+=len(literal);break
        else:raise ValueError('Invalid JSON token')
    if stack or not nodes:raise ValueError('Incomplete JSON')
    return JSONShape(nodes,keys,nodes+keys,depth)
