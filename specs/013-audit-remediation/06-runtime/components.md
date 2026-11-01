# R1 component model — G3 ready

G2 PASS prerequisite. Author /root/audit_research; independent reviewer next.
R1 only: no production code,proxy functions,new worker or plugin framework.

| Owner/component | Reuse and consumers | Contract |
| --- | --- | --- |
| Root __init__ | Existing83 public objects and __version__; stdlib importlib | Frozen ordered __all__/intentional names; __getattr__ resolves original module attribute,not wrapper; __dir__ exposes all names without loading optional modules |
| Extractor __init__ | Existing10 actual extractor classes; same stdlib import mechanism | Plain namespace import has no crawl4ai/playwright dependency; explicit browser-class access imports actual class |
| Module export registry | Small private per-module name->module/attribute declarations | Ownership stays with defining package; no shared mutable cross-package registry or runtime test-fixture dependency |
| Python import cache | importlib/sys.modules plus successful per-module globals binding | Cache actual objects once; public function/class identities and signatures preserved; repeat lookup returns identical object |
| Frozen compatibility oracle | Original eager initializer source + inventory fixtures | Independent tests compare every original exported object; expectation is not inferred from production lazy mapping |

Lifecycle is ordinary per-process module import. No threads/processes/network,
background cleanup or persistent state introduced. A plain package/model/native
Domain import must not load browser modules. Explicit export resolution may load
its actual dependencies. Unknown names raise AttributeError; defining-module
ImportError propagates and no placeholder/success cache entry is fabricated.

Naming/submodule collisions must preserve reviewed public callable resolution;
actual module objects are not proxies for functions. Frozen all-export identity
controls challenge unintended omissions/collisions. __all__/dir/version and exact
constructor signatures remain compatible. No fixed import-time SLA or claim of
proving prior100-poll failure cause.

R2 Woo limits/retry,R3 checkpoints,R4 worker/robots and R5 ordering/stdout are future
independent component/skeleton/red reviews. This R1 G3 gate does not authorize a
whole-runtime refactor or waive outstanding full-suite/live verification gates.
