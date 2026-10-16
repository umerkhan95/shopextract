# Live evidence persistence and portability verification

2026-10-16. Sequential bounded public-source sampling; no model or paid inference.

| Live case | Products | Variants | Retrieved captures | Result |
|---|---:|---:|---:|---|
| shopify | 2 | 2 | 105 | passed |
| woocommerce | 2 | 0 | 27 | passed |
| magento | 2 | 30 | 440 | passed |
| shopware | 2 | 0 | 19 | passed |
| public-snapshot | 2 | — | 105 | passed |

Five cases across four platform families passed: 10 product observations and 696 scoped capture records retrieved. Counts include standalone variant scopes and repeat Shopify observations in the public snapshot test; they are not unique products or independent accuracy samples.

The four adapter cases each verified live capture/normalization and resolution, typed SQLite save/load, a genuinely separate process reopening/retrieving, portable bundle load, CSV/Google Shopping/Idealo companion integrity and actual row mapping, modified-file rejection, reference-protected pruning, explicit expiry, expired bundle load/resave and SQLite integrity/foreign keys. Public `shopextract.snapshot()` additionally retained its product-count return, two-product budget and incomplete catalog metadata, with retrievable contracts after process restart.

Final offline CI-equivalent command: `PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q` — **631 passed in 8.29s**.

Commands: `PYTHONPATH=src .venv/bin/python artifacts/live-evidence-trust/run.py shopify` (small saved smoke first), then `... run.py woocommerce magento shopware`, then `... public_snapshot.py`. Adapter workers have 85-second async and 100-second subprocess limits; request timeout is 15 seconds, one page and two retained products. WooCommerce may fetch its normal single page before selecting two products. Public snapshot has a 65-second async cap. All operations are sequential in the network driver.

Sources: [Shopify](https://www.boardgamebliss.com), [WooCommerce](https://demo.athemes.com/botiga), [Magento](https://magento2-demo.magebit.com), [Shopware](https://frontends-demo.vercel.app).

Saved `summary.json` and per-case JSON record actual outcomes. Raw live bundles, sidecars, SQLite files and restart logs remain local under this directory; only compact reports, summaries, driver scripts and the offline result log are committed. Repeated driver runs reuse passed summaries. To deliberately repeat, use a fresh case directory; the harness refuses to overwrite its existing database.

These are bounded live persistence/export checks, not broad extraction quality, full catalog completeness, load, source authenticity or calibrated confidence claims. BigCommerce, browser/CSS and optional LLM were not newly live-tested here; their affected offline compatibility remains in the full suite. Retention establishes support unavailability, not secure deletion of all raw copies/backups. The installed requests stack emitted an existing dependency warning; these live checks completed without a transport or assertion failure.
