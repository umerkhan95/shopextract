"""Bounded fresh live checks; preserve original live-e2e artifacts."""
import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path
import httpx
import shopextract as s
from shopextract.compare.catalog import _diff_catalogs

parser = argparse.ArgumentParser(description="Bounded live identity checks for the reviewed Catan sample")
parser.add_argument("--output-dir", default="artifacts/live-identity")
OUT = Path(parser.parse_args().output_dir)
OUT.mkdir(parents=True, exist_ok=True)
PAIRS = [('catan-fifth-edition','catan-base-game'),('catan-5-6-player-extension-fifth-edition','catan-base-game-5-6-player-extension'),('catan-seafarers-fifth-edition','catan-seafarers'),('catan-cities-knights-5-6-player-extension-fifth-edition','catan-cities-knights-5-6-player-extension')]
HOSTS = ['https://www.boardgamebliss.com','https://store.401games.ca']

async def main():
    cats = [[], []]
    strict_cats = [[], []]
    pairs = []
    aliases = {gtin: ["Mayfair Games", "Catan Studio"] for gtin in (
        "029877030712", "029877030729", "029877030736", "029877030781")}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for handles in PAIRS:
            observations = []
            for i, host in enumerate(HOSTS):
                response = await client.get(f'{host}/products/{handles[i]}.json')
                response.raise_for_status()
                raw = response.json()['product']
                p = s.normalize(raw, s.Platform.SHOPIFY, host, restore_short_gtin=True)
                cats[i].append(p)
                strict_cats[i].append(s.normalize(raw, s.Platform.SHOPIFY, host))
                v = raw['variants'][0]
                observations.append({'title': p.title, 'source_barcode': v.get('barcode'), 'gtin': p.gtin,
                                     'source_currency': v.get('price_currency'), 'currency': p.currency,
                                     'vendor': p.vendor, 'url': str(response.url)})
            pairs.append(observations)
    strict = [asdict(s.classify_match(a,b)) for a,b in zip(*strict_cats)]
    restoration_only = [asdict(s.classify_match(a,b)) for a,b in zip(*cats)]
    configured = [asdict(s.classify_match(a,b,publisher_aliases=aliases)) for a,b in zip(*cats)]
    diff = _diff_catalogs(*HOSTS, *cats, .8, publisher_aliases=aliases)
    labeled = [{"id": f"{i}:{j}", "a": asdict(a), "b": asdict(b), "label": "exact" if i == j else "unmatched"}
               for i, a in enumerate(cats[0]) for j, b in enumerate(cats[1])]
    evaluation = s.evaluate_matching(labeled, publisher_aliases=aliases)
    result = {'evaluation': evaluation, 'selected_pairs': pairs, 'strict_policy': strict, 'restoration_only_policy': restoration_only, 'configured_policy': configured,
              'selected_exact_coverage': len(diff.in_both)/4, 'accepted_indices': [(d.index_a,d.index_b) for d in diff.match_report if d.relation == 'exact']}
    for name, url, budget in [('collection',HOSTS[0]+'/collections/catan-series',5), ('demo','https://hydrogen-preview.myshopify.com',3)]:
        r = await s.extract(url, platform=s.Platform.SHOPIFY, max_urls=budget, enrich_identifiers=True, restore_short_gtin=True)
        result[name] = {'budget':budget,'count':len(r.products),'tier':r.tier,'errors':r.errors,
                        'products':[{'title':p.title,'currency':p.currency,'gtin':p.gtin,'in_stock':p.in_stock,
                                     'raw_available':[v.get('available') for v in p.raw_data.get('variants',[])],
                                     'enrichment_sources':p.raw_data.get('_identifier_sources',[]),
                                     'enrichment_errors':p.raw_data.get('_identifier_enrichment_errors',[])} for p in r.products]}
        assert len(r.products) <= budget
        for p in r.products:
            flags=[v.get('available') for v in p.raw_data.get('variants',[])]
            if flags and all(isinstance(x,bool) for x in flags):
                assert p.in_stock == any(flags)
    s.to_csv([asdict(p) for p in cats[0]], str(OUT / "selected.csv"))
    s.to_json([asdict(p) for p in cats[0]], str(OUT / "selected.json"))
    result["exports"] = {"csv_exists": (OUT / "selected.csv").exists(), "json_count": len(json.loads((OUT / "selected.json").read_text()))}
    assert result["exports"]["csv_exists"] and result["exports"]["json_count"] == 4
    assert len(diff.in_both) == 4
    assert all(d.index_a == d.index_b for d in diff.match_report if d.relation == 'exact')
    assert all(p.currency == 'CAD' for cat in cats for p in cat)
    (OUT/'results.json').write_text(json.dumps(result,default=str,indent=2))
    print(json.dumps(result,default=str,indent=2),flush=True)

asyncio.run(main())
