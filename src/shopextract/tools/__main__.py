"""Self-hosted stdio launcher. Configuration is trusted operator input."""
import argparse
import asyncio
import json
import sys
from .runtime import ToolConfig, ToolRuntime, Limits, CaptureGrant


def load_config(path):
    with open(path, encoding='utf-8') as source:
        value = json.load(source)
    if not isinstance(value, dict) or value.keys() - {'allowed_origins', 'allowed_tools', 'captures', 'limits'}:
        raise ValueError('Invalid operator config')
    return ToolConfig(allowed_origins=tuple(value.get('allowed_origins', ())),
        allowed_tools=tuple(value.get('allowed_tools', ToolConfig().allowed_tools)),
        captures=tuple(CaptureGrant(**entry) for entry in value.get('captures', ())),
        limits=Limits(**value.get('limits', {})))


def main():
    parser = argparse.ArgumentParser(description='ShopExtract read-only MCP stdio server')
    parser.add_argument('--config', required=True, help='Trusted local JSON operator configuration')
    args = parser.parse_args()
    try:
        from .mcp_server import serve
        import mcp
    except ImportError:
        print('Install shopextract[mcp] to run the MCP server.', file=sys.stderr)
        return 2
    try:
        runtime = ToolRuntime(load_config(args.config))
        asyncio.run(serve(runtime))
    except (ValueError, TypeError, OSError):
        print('Invalid or unavailable operator configuration.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
