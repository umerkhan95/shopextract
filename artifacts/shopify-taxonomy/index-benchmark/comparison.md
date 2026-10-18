| Metadata storage | Open+first schema s | Resident MiB | Hot p50 ms | Unique128 ms |
| --- | ---: | ---: | ---: | ---: |
| dict | 3.3543 | 415.5 | 0.2927 | 17.32 |
| sqlite | 0.3443 | 91.1 | 0.2503 | 37.87 |

SQLite timing has weaker runtime integrity (file hash vs complete logical validation); preparation costs separate. This is not a production replacement or equivalent end-to-end pipeline benchmark.
