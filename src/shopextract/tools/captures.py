"""Worker-only bounded, read-transaction capture loader; no migration/backfill."""
from dataclasses import fields
import json
from pathlib import Path
import sqlite3
from .contracts import ToolError

TABLES=('evidence_products','evidence_owners','evidence_records','evidence_payloads','evidence_references')


def load_capture(payload):
    from ..monitor.evidence import _iter_snapshot
    from .._portable import product_to_record
    from .domain import catalog_graph
    from .runtime import Limits
    from .state import SessionStore
    limits=Limits(**payload['limits']);grant=payload['grant'];connection=None
    try:
        connection=sqlite3.connect(Path(grant['db_path']).expanduser().resolve().as_uri()+'?mode=ro',uri=True,timeout=limits.max_timeout_seconds)
        connection.execute('PRAGMA query_only=ON');connection.execute('BEGIN')
        known={row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('snapshots','evidence_products','evidence_owners','evidence_records','evidence_payloads','evidence_references')")}
        if 'snapshots' not in known or not connection.execute('SELECT 1 FROM snapshots WHERE id=?',(grant['snapshot_id'],)).fetchone():
            raise ToolError('source_error','Configured capture unavailable')
        modern=bool(known.intersection(TABLES))
        if modern and not set(TABLES)<=known:
            raise ToolError('source_error','Incomplete capture schema')
        total=0
        for table in ['snapshots']+(list(TABLES) if modern else []):
            columns=[row[1] for row in connection.execute(f'PRAGMA table_info({table})')]
            # SQLite computes scalar byte lengths; no stored text/blob is fetched yet.
            size='+'.join('coalesce(length(CAST(t."'+column.replace('"','""')+'" AS BLOB)),0)' for column in columns)
            if table=='evidence_payloads':
                query=f'SELECT coalesce(sum({size}),0),count(*) FROM {table} t JOIN evidence_records r ON r.payload_hash=t.payload_hash WHERE r.snapshot_id=?'
            else:
                key='id' if table=='snapshots' else 'snapshot_id'
                query=f'SELECT coalesce(sum({size}),0),count(*) FROM {table} t WHERE t.{key}=?'
            amount,count=connection.execute(query,(grant['snapshot_id'],)).fetchone();total+=amount
            if total>limits.graph_bytes or (table=='evidence_products' and count>limits.item_count):
                raise ToolError('resource_limit','Configured capture preflight limit reached')
        if not modern or not connection.execute('SELECT 1 FROM evidence_products WHERE snapshot_id=? LIMIT 1',(grant['snapshot_id'],)).fetchone():
            legacy=json.loads(connection.execute('SELECT products_json FROM snapshots WHERE id=?',(grant['snapshot_id'],)).fetchone()[0])
            if not isinstance(legacy,list):raise ToolError('source_error')
            if len(legacy)>limits.item_count:raise ToolError('resource_limit')
            del legacy
        store=SessionStore(limits);graph=catalog_graph([],store,grant=grant)
        for index,product in enumerate(_iter_snapshot(connection,grant['snapshot_id'],legacy_only=not modern)):
            if index>=limits.item_count:raise ToolError('resource_limit')
            part=catalog_graph([product_to_record(product)],store)
            graph.collections['products'].extend(part.collections['products']);graph.products.extend(part.products);graph.owners.update(part.owners)
            if graph.size>limits.graph_bytes:raise ToolError('resource_limit','Configured graph limit reached')
        return {field.name:getattr(graph,field.name) for field in fields(graph)}
    except ToolError:raise
    except (sqlite3.Error,ValueError,KeyError,TypeError,AttributeError):
        raise ToolError('source_error','Configured capture unavailable') from None
    finally:
        if connection is not None:connection.close()
