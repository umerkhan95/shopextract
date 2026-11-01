"""Private one-request discovery worker. stdout is protocol only."""
import asyncio
import contextlib
import json
import sys


def main():
    payload=json.loads(sys.stdin.read(65537))
    with contextlib.redirect_stdout(sys.stderr):
        from ._discover import _discover_local
        from ._models import Platform
        result=asyncio.run(_discover_local(payload['url'],
            platform=Platform(payload['platform']) if payload.get('platform') else None,
            max_urls=payload.get('max_urls',100),timeout=payload.get('timeout',30)))
    print(json.dumps({'urls':list(result),'reasons':result.reasons,'request_count':result.request_count},allow_nan=False))


if __name__=='__main__':main()
