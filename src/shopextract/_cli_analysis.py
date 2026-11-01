"""Bounded analysis/export bindings; native algorithms own all domain decisions."""
from __future__ import annotations

import json
import math
import os
import shutil
import tempfile
from dataclasses import asdict
from decimal import Decimal
from enum import Enum
from pathlib import Path

import click

from ._cli_core import CliFailure, CoreCommand, emit_response, make_response
from ._cli_data import (CatalogInput, catalog_from_value, load_catalog, flat_to_products,
                        read_json_file, MAX_RECORDS)
from ._cli_extract import run_operation, validate_timeout, validate_url, validate_max
from ._execution import ExecutionPolicy
from ._evidence import encode_value
from ._models import Product
from ._portable import product_to_record

# Concrete report model schema, deliberately no generic dataclass/default=str dump.
_REPORT_FIELDS = {
    'CatalogStats': ('total_products','price_range','avg_price','median_price','currencies','brands','categories','in_stock','out_of_stock','unknown_stock','has_gtin','has_images','completeness_score'),
    'MatchDecision': ('relation','confidence','evidence','conflicts','needs_review','index_a','index_b','candidate_method','field_support'),
    'Match': ('title','price','currency','store','product_url','similarity'),
    'ComparisonResult': ('query','matches','cheapest','most_expensive','avg_price','price_spread'),
    'SafeComparison': ('query','currency_groups','unranked','sources'),
    'CatalogDiff': ('store_a','store_b','only_in_a','only_in_b','in_both','cheaper_in_a','cheaper_in_b','match_report','sources'),
    'SourceStatus': ('store','usable','catalog_complete','errors'),
    'PricePosition': ('product_title','my_price','rank','total_competitors','percentile','market_avg','cheapest','most_expensive','competitor_prices'),
    'SafePosition': ('position','currency','excluded','sources'),
    'AssortmentGaps': ('missing_categories','missing_brands','competitor_category_counts','competitor_brand_counts','my_categories','my_brands','sources'),
    'ValidationReport': ('marketplace','total','valid','invalid','issues','warnings','pass_rate','subset_status','rules_version','unassessed_checks'),
    'ValidationIssue': ('product_index','product_title','field','error','severity','rule_id'),
    'ImageIssue': ('product_index','product_title','image_url','status_code','content_type','error'),
}


def report(value):
    if isinstance(value, Product):
        return product_to_record(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return encode_value(value)
    if type(value).__name__ in _REPORT_FIELDS:
        return {name:report(getattr(value,name)) for name in _REPORT_FIELDS[type(value).__name__]}
    if isinstance(value,dict):
        return {str(k):report(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [report(v) for v in value]
    if value is None or type(value) in (str,bool,int,float):
        if isinstance(value,float) and not math.isfinite(value):
            raise CliFailure('E_OPERATION','Native report contains a nonfinite aggregate.')
        return value
    # Native raw product values may contain timestamps supported by evidence codec.
    return encode_value(value)


def output(data, *, partial=False, validation=False, warnings=()):
    failure = CliFailure('E_PARTIAL','Some sources returned incomplete results; inspect sources.') if partial else None
    if validation:
        response = make_response(report(data))
        response['ok'] = False
        response['error'] = dict(code='E_VALIDATION',message='Marketplace validation rejected products.',retryable=False)
        emit_response(response)
        raise SystemExit(4)
    emit_response(make_response(report(data),failure=failure,warnings=warnings))
    if partial:
        raise SystemExit(3)


def number(value, *, low=0, high=None, strict=False, name='Value'):
    if not math.isfinite(value) or (value <= low if strict else value < low) or high is not None and value > high:
        raise CliFailure('E_USAGE', f'{name} is outside its finite supported range.')
    return value


def stores(values):
    if not 1 <= len(values) <= 10:
        raise CliFailure('E_USAGE','Supply from1 to10 store URLs.')
    return [validate_url(v) for v in values]


def single(catalog):
    if len(catalog.records) != 1:
        raise CliFailure('E_USAGE','Expected exactly one product record.')
    return catalog.products[0] if catalog.products is not None else catalog.records[0]


def pair_files(left,right):
    if left == right == '-':
        raise CliFailure('E_USAGE','Only one input may read stdin.')
    return load_catalog(left),load_catalog(right)


def matching_files(aliases, candidates, left_count=None, right_count=None):
    result = {}
    if aliases == candidates == '-':raise CliFailure('E_USAGE','Only one input may read stdin.')
    if aliases:
        data = read_json_file(aliases)
        if not isinstance(data,dict) or set(data) != {'schema_version','publisher_aliases'} or type(data['schema_version']) is not int or data['schema_version'] != 1:
            raise CliFailure('E_USAGE','Publisher aliases require schema_version1 and publisher_aliases mapping.')
        mapping = data['publisher_aliases']
        if not isinstance(mapping,dict) or len(mapping)>MAX_RECORDS or any(not isinstance(k,str) or not k or not isinstance(v,list) or not v or len(v)>100 or any(not isinstance(x,str) or not x.strip() for x in v) for k,v in mapping.items()):
            raise CliFailure('E_USAGE','Invalid publisher alias mapping.')
        from .compare.identity_match import _gtin
        if any(not _gtin(key) for key in mapping):
            raise CliFailure('E_USAGE','Publisher aliases require valid GTIN keys.')
        result['publisher_aliases'] = mapping
    if candidates:
        data = read_json_file(candidates)
        if not isinstance(data,dict) or set(data) != {'schema_version','semantic_candidates'} or type(data['schema_version']) is not int or data['schema_version'] != 1:
            raise CliFailure('E_USAGE','Semantic candidates require schema_version1 and semantic_candidates rows.')
        rows = data['semantic_candidates']
        if not isinstance(rows,list) or len(rows)>MAX_RECORDS or left_count is not None and len(rows)!=left_count or any(not isinstance(row,list) or len(row)>MAX_RECORDS or any(type(j) is not int or not 0<=j<(right_count if right_count is not None else MAX_RECORDS) for j in row) for row in rows):
            raise CliFailure('E_USAGE','Invalid semantic candidate dimensions/indices.')
        result['semantic_candidate_indices'] = rows
    return result


def native_inputs(catalog):
    return catalog.products if catalog.products is not None else catalog.records


def network(operation, timeout):
    data,warnings = run_operation(operation,ExecutionPolicy(),validate_timeout(timeout))
    sources = getattr(data,'sources',[])
    if sources and not any(source.usable for source in sources):
        raise CliFailure('E_OPERATION','No usable source catalogs; inspect configured URLs and source availability.')
    partial = any(not s.usable or s.catalog_complete is False or s.errors for s in sources)
    output(data,partial=partial,warnings=warnings)


def compare_command(query,urls,max_per_store,threshold,timeout):
    from .compare import compare
    urls=stores(urls); validate_max(max_per_store); number(threshold,high=1,name='Threshold')
    network(lambda:compare(query,urls,max_per_store=max_per_store,threshold=threshold,currency_safe=True),timeout)


def analyze_command(url,maximum,timeout):
    from . import extract
    from .analyze import analyze_products
    from ._analysis_safe import source_status
    validate_url(url); validate_max(maximum)
    result,warnings=run_operation(lambda:extract(url,max_urls=maximum),ExecutionPolicy(),validate_timeout(timeout))
    source=source_status(url,result)
    if not source.usable:
        raise CliFailure('E_OPERATION','No usable source catalog.')
    records=result.raw_products or asdict(result)['products']
    output({'statistics':analyze_products(records),'aggregate_precision':'native_float_approximate','sources':[source]},
           partial=result.catalog_complete is False or bool(result.errors),warnings=warnings)


def validate_command(file,marketplace):
    from .validate import validate
    catalog=load_catalog(file)
    result=validate(catalog.products if catalog.products is not None else catalog.records,marketplace=marketplace)
    output(result,validation=result.invalid>0)


def _path_alias(a,b):
    aa,bb=Path(a),Path(b)
    return aa.resolve()==bb.resolve() or aa.exists() and bb.exists() and os.path.samefile(aa,bb)


def export_artifact(catalog,fmt,target,companion=None,source=None,categories=None):
    from .export import to_json,to_csv,to_feed,to_parquet
    if companion and (target=='-' or companion=='-' or fmt not in ('csv','google_shopping','idealo') or catalog.products is None):
        raise CliFailure('E_USAGE','Evidence companions require portable input and CSV/feed file outputs.')
    if catalog.categorized_records is not None and not categories:
        raise CliFailure('E_USAGE','Categorized input requires --categories-output to retain scoped companions.')
    if categories and (catalog.categorized_records is None or target=='-' or categories=='-'):
        raise CliFailure('E_USAGE','Category companions require categorized input and file outputs.')
    paths=[p for p in (target,companion,categories) if p and p!='-']
    if any(_path_alias(a,b) for i,a in enumerate(paths) for b in paths[i+1:]) or source and source!='-' and any(_path_alias(source,p) for p in paths):
        raise CliFailure('E_USAGE','Input, output and evidence paths must differ, including aliases.')
    # Sidecar native validation happens before any artifact replacement.
    products=catalog.products if companion else catalog.records
    if categories:
        from ._cli_categories import MAX_BYTES
        category_value=dict(schema_version='1.0',data=dict(products=[product_to_record(p) for p in catalog.products],categorized_products=catalog.categorized_records,**catalog.category_policy)) if catalog.category_policy else catalog.categorized_records
        category_bytes=json.dumps(category_value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
        if len(category_bytes)>MAX_BYTES:
            raise CliFailure('E_USAGE','Category companion exceeds CLI1MiB output cap.')
    structured_columns=[]
    if categories and fmt=='parquet':
        structured_columns=sorted({k for row in products for k,v in row.items() if isinstance(v,(dict,list))})
        products=[{k:json.dumps(encode_value(v),ensure_ascii=False,allow_nan=False,separators=(',',':')) if k in structured_columns else v
                   for k,v in row.items()} for row in products]
    stages=[]; backups=[]; installed=[]; retain=False
    def stage(path,suffix=''):
        parent=Path(path).parent if path!='-' else Path(tempfile.gettempdir())
        prefix=f'.{Path(path).name}.' if path!='-' else '.shopextract-export.'
        fd,name=tempfile.mkstemp(dir=parent,prefix=prefix,suffix=suffix);os.close(fd)
        stages.append(name);return name
    try:
        payload=stage(target,Path(target).suffix)
        side=stage(companion) if companion else None
        category_stage=stage(categories) if categories else None
        if category_stage:Path(category_stage).write_bytes(category_bytes)
        if fmt=='json':to_json(products,payload)
        elif fmt=='csv':to_csv(products,payload,evidence_path=side)
        elif fmt in ('google_shopping','idealo'):
            feed_result=to_feed(catalog.products if catalog.products is not None else products,payload,format=fmt,evidence_path=side)
        else:
            try:to_parquet(products,payload)
            except ImportError:
                raise CliFailure('E_DEPENDENCY','Parquet requires pandas and a parquet engine; install shopextract[data] and pyarrow yourself.') from None
            except NotImplementedError:
                raise CliFailure('E_OPERATION','Native Parquet cannot encode this field shape; use JSON/CSV or categorized structured JSON columns.') from None
        if target=='-':
            click.get_binary_stream('stdout').write(Path(payload).read_bytes())
            return
        pairs=[(payload,target)]+([(side,companion)] if companion else [])+([(category_stage,categories)] if categories else [])
        if categories:
            from ._cli_categories import MAX_BYTES
            if any(Path(temporary).stat().st_size>MAX_BYTES for temporary,_ in pairs):
                raise CliFailure('E_USAGE','Categorized export payload or companion exceeds CLI1MiB; reduce input.')
        for _,destination in pairs:
            if Path(destination).exists():
                backup=stage(destination,'.backup');shutil.copy2(destination,backup)
            else:backup=None
            backups.append((destination,backup))
        try:
            for temporary,destination in pairs:
                os.replace(temporary,destination);installed.append(destination)
        except OSError:
            recovery=[]
            for destination,backup in reversed(backups):
                if destination not in installed:continue
                try:
                    if backup:os.replace(backup,destination)
                    else:Path(destination).unlink(missing_ok=True)
                except OSError:
                    recovery.append(f'{destination} backup={backup or "initially absent"}')
            if recovery:
                retain=True
                raise CliFailure('E_OPERATION','Export replacement/recovery failed; retained recovery files: '+ '; '.join(recovery)+'; retained stages='+','.join(stages)) from None
            raise CliFailure('E_OPERATION','Export replacement failed; previous outputs restored.') from None
        output({'format':fmt,'output':target,'evidence_output':companion,**({'categories_output':categories} if categories else {}),**({'structured_json_columns':structured_columns,'structured_json_encoding':'evidence-json-v1'} if structured_columns else {}),'product_count':len(catalog.records),'bytes':Path(target).stat().st_size,**(feed_result if fmt in ('google_shopping','idealo') else {})})
    except CliFailure:raise
    except (OSError,ValueError,TypeError):
        raise CliFailure('E_OPERATION','Cannot stage export; previous outputs preserved.') from None
    finally:
        if not retain:
            for name in stages:
                try:Path(name).unlink(missing_ok=True)
                except OSError:pass


def register(main):
    @main.command('compare-catalogs')
    @click.argument('store_a')
    @click.argument('store_b')
    @click.option('--max-products',type=click.IntRange(1,1000),default=200)
    @click.option('--threshold',type=float,default=.8)
    @click.option('--publisher-aliases',type=click.Path())
    @click.option('--semantic-candidates',type=click.Path())
    @click.option('--enrich-identifiers',is_flag=True)
    @click.option('--restore-short-gtin',is_flag=True)
    @click.option('--timeout',type=float,default=None)
    def catalogs(store_a,store_b,max_products,threshold,publisher_aliases,semantic_candidates,enrich_identifiers,restore_short_gtin,timeout):
        """Compare two native store URLs (not offline catalog files)."""
        from .compare import compare_catalogs
        stores((store_a,store_b));number(threshold,high=1,name='Threshold')
        options=matching_files(publisher_aliases,semantic_candidates)
        network(lambda:compare_catalogs(store_a,store_b,max_products=max_products,threshold=threshold,source_report=True,
                enrich_identifiers=enrich_identifiers,restore_short_gtin=restore_short_gtin,**options),timeout)

    @main.command('match')
    @click.argument('left')
    @click.argument('right')
    @click.option('--method',type=click.Choice(['identity','fuzzy']),default='identity')
    @click.option('--threshold',type=float,default=.8)
    @click.option('--publisher-aliases',type=click.Path())
    @click.option('--semantic-candidates',type=click.Path())
    def match(left,right,method,threshold,publisher_aliases,semantic_candidates):
        """Match flat or portable catalogs; - reads stdin once."""
        from .compare import match_products,fuzzy_match
        if [left,right,publisher_aliases,semantic_candidates].count('-')>1:raise CliFailure('E_USAGE','Only one input may read stdin.')
        a,b=pair_files(left,right);number(threshold,high=1,name='Threshold')
        options=matching_files(publisher_aliases,semantic_candidates,len(a.records),len(b.records))
        if method=='fuzzy' and options:raise CliFailure('E_USAGE','Declarative matching files require identity method.')
        result=match_products(native_inputs(a),native_inputs(b),threshold=threshold,**options) if method=='identity' else fuzzy_match(a.records,b.records,threshold=threshold)
        output({'method':method,'results':result})

    @main.command('match-pair')
    @click.argument('left')
    @click.argument('right')
    @click.option('--threshold',type=float,default=.8)
    @click.option('--publisher-aliases',type=click.Path())
    def pair(left,right,threshold,publisher_aliases):
        from .compare import classify_match
        if [left,right,publisher_aliases].count('-')>1:raise CliFailure('E_USAGE','Only one input may read stdin.')
        a,b=pair_files(left,right);number(threshold,high=1,name='Threshold')
        output(classify_match(single(a),single(b),threshold=threshold,**matching_files(publisher_aliases,None)))

    @main.command('match-gtin')
    @click.argument('gtin')
    @click.argument('file')
    def gtin(gtin,file):
        """Legacy GTIN/SKU lookup candidates, not identity authorization."""
        from .compare import match_gtin
        output({'candidates':match_gtin(gtin,load_catalog(file).records),'identity_authorization':False})

    @main.command('match-evaluate')
    @click.argument('file')
    @click.option('--threshold',type=float,default=.8)
    @click.option('--publisher-aliases',type=click.Path())
    def evaluate(file,threshold,publisher_aliases):
        from .compare import evaluate_matching,MatchRelation
        if [file,publisher_aliases].count('-')>1:raise CliFailure('E_USAGE','Only one input may read stdin.')
        data=read_json_file(file);number(threshold,high=1,name='Threshold')
        if not isinstance(data,list) or len(data)>MAX_RECORDS:raise CliFailure('E_USAGE','Expected bounded evaluation rows.')
        for row in data:
            if not isinstance(row,dict) or set(row)!={'id','a','b','label'} or not isinstance(row['id'],str) or row['label'] not in [r.value for r in MatchRelation]:
                raise CliFailure('E_USAGE','Evaluation rows require id,a,b,label with native relation label.')
            for side in ('a','b'):
                catalog=catalog_from_value([row[side]])
                row[side]=native_inputs(catalog)[0]
        output(evaluate_matching(data,threshold=threshold,**matching_files(publisher_aliases,None)))

    @main.group('identity',cls=click.Group)
    def identity():
        """Assign stable identities or inspect native normalized attributes."""
    for action in ('assign','inspect'):
        def identity_command(file,supplier_id,action=action):
            from .identity import assign_identity
            from .compare import normalized_attributes
            catalog=load_catalog(file)
            products=catalog.products if catalog.products is not None else flat_to_products(catalog.records)
            if action=='assign':
                try:
                    assigned=[assign_identity(p,supplier_id) for p in products]
                except ValueError:
                    raise CliFailure('E_USAGE','Identity assignment requires a consistent supplier ID or absolute product URL.') from None
                output({'products':assigned})
            else:output({'products':products,'normalized_attributes':[normalized_attributes(p) for p in products]})
        identity.command(action,cls=CoreCommand)(click.argument('file')(click.option('--supplier-id',default='')(identity_command)))

    @main.command('analyze-file')
    @click.argument('file')
    def analyze_file(file):
        from .analyze import analyze_products
        catalog=load_catalog(file)
        output({'statistics':analyze_products(catalog.products if catalog.products is not None else catalog.records),'aggregate_precision':'native_float_approximate'})

    @main.group('stats',cls=click.Group)
    def stats():
        """Native approximate float statistics on flat or portable catalogs."""
    @stats.command('distribution',cls=CoreCommand)
    @click.argument('file')
    @click.option('--buckets',help='Comma-separated ascending finite nonnegative boundaries.')
    def distribution(file,buckets):
        from .analyze import price_distribution
        values=None
        if buckets is not None:
            try:values=[float(v) for v in buckets.split(',')]
            except ValueError:raise CliFailure('E_USAGE','Invalid bucket boundaries.') from None
            if not values or len(values)>100 or values!=sorted(set(values)) or any(not math.isfinite(v) or v<0 for v in values):raise CliFailure('E_USAGE','Buckets must be ascending unique finite nonnegative numbers.')
        output({'distribution':price_distribution(load_catalog(file).records,values),'aggregate_precision':'native_float_approximate'})
    @stats.command('outliers',cls=CoreCommand)
    @click.argument('file')
    @click.option('--std-multiplier',type=float,default=2.)
    def outlier(file,std_multiplier):
        from .analyze import outliers
        number(std_multiplier,strict=True,name='Multiplier')
        output({'products':outliers(load_catalog(file).records,std_multiplier),'aggregate_precision':'native_float_approximate'})
    @stats.command('brands',cls=CoreCommand)
    @click.argument('file')
    def brands(file):
        from .analyze import brand_breakdown
        output({'brands':brand_breakdown(load_catalog(file).records)})

    @main.group('competitive',cls=click.Group)
    def competitive():
        """Native competitor store analysis; brands consumes a catalog mapping."""
    @competitive.command('brands',cls=CoreCommand)
    @click.argument('file')
    def coverage(file):
        from .analyze import brand_coverage
        data=read_json_file(file)
        if not isinstance(data,dict) or len(data)>10:raise CliFailure('E_USAGE','Expected mapping of at most10 store names to catalogs.')
        catalogs={name:catalog_from_value(value).records for name,value in data.items()}
        if sum(map(len,catalogs.values()))>MAX_RECORDS:raise CliFailure('E_USAGE','Catalog mapping exceeds1000 total records.')
        output(brand_coverage(catalogs))
    @competitive.command('position',cls=CoreCommand)
    @click.argument('file')
    @click.option('--competitor',multiple=True,required=True)
    @click.option('--max-products',type=click.IntRange(1,1000),default=200)
    @click.option('--timeout',type=float,default=None)
    def position(file,competitor,max_products,timeout):
        from .analyze import price_position
        catalog=load_catalog(file);single(catalog);urls=stores(competitor)
        product=catalog.records[0];currency=product.get('currency')
        if catalog.products is not None:
            from ._analysis_safe import observed_currency
            currency=observed_currency(catalog.products[0],catalog.products[0].raw_data)
        if not isinstance(currency,str) or not currency.strip() or not product.get('title') or product.get('price') is None:raise CliFailure('E_USAGE','Position requires title,price and explicit currency.')
        network(lambda:price_position(product,urls,max_products=max_products,currency=currency.strip().upper()),timeout)
    @competitive.command('gaps',cls=CoreCommand)
    @click.argument('store')
    @click.option('--competitor',multiple=True,required=True)
    @click.option('--max-products',type=click.IntRange(1,1000),default=200)
    @click.option('--timeout',type=float,default=None)
    def gaps(store,competitor,max_products,timeout):
        from .analyze import assortment_gaps
        urls=stores((store,*competitor))
        network(lambda:assortment_gaps(urls[0],urls[1:],max_products=max_products,source_report=True),timeout)

    @main.command('duplicates')
    @click.argument('file')
    @click.option('--method',type=click.Choice(['title','gtin','sku']),default='title')
    @click.option('--threshold',type=float,default=.9)
    def duplicates(file,method,threshold):
        from .validate import find_duplicates
        number(threshold,high=1,name='Threshold')
        output({'duplicates':find_duplicates(load_catalog(file).records,method,threshold)})

    @main.group('images',cls=click.Group)
    def images():
        """Check product image URLs using native HEAD validation."""
    @images.command('check',cls=CoreCommand)
    @click.argument('file')
    @click.option('--timeout',type=float,default=None)
    @click.option('--concurrency',type=click.IntRange(1,20),default=20)
    def image_check(file,timeout,concurrency):
        from .validate import check_images
        records=load_catalog(file).records;deadline=validate_timeout(timeout)
        for p in records:
            if p.get('image_url'):validate_url(p['image_url'])
        data,warnings=run_operation(lambda:check_images(records,timeout=deadline,concurrency=concurrency),ExecutionPolicy(),deadline)
        output({'issues':data},warnings=warnings)

    @main.command('export')
    @click.argument('file')
    @click.option('--format','fmt',type=click.Choice(['json','csv','google_shopping','idealo','parquet']),required=True)
    @click.option('--output','-o',required=True,help='Artifact path, or - for raw stdout without response JSON.')
    @click.option('--evidence-output',type=click.Path())
    @click.option('--categories-output',type=click.Path(),help='Required scoped companion file for categorized input.')
    def export(file,fmt,output,evidence_output,categories_output):
        """Stage native artifact exports; companions require portable CSV/feed input."""
        export_artifact(load_catalog(file),fmt,output,evidence_output,source=file,categories=categories_output)
