"""One saved historical product, measured offline; no extrapolated timing claim."""
import cProfile,pstats,io,json,tempfile,time
from pathlib import Path
from shopextract._cli_data import read_json_file,products_from_value
from shopextract.export import to_csv
base=Path(__file__).parent
source=json.loads((base.parent/'02-money-roundtrip/actual-audit-shape.json').read_text())['source']
products=products_from_value(read_json_file(source))[:1]
prof=cProfile.Profile();start=time.monotonic()
with tempfile.TemporaryDirectory() as t:
 prof.enable();to_csv(products,t+'/p.csv',evidence_path=t+'/e.json');prof.disable()
stream=io.StringIO();pstats.Stats(prof,stream=stream).sort_stats('cumulative').print_stats(18)
(base/'export-profile.txt').write_text('one product; elapsed '+str(time.monotonic()-start)+'\n'+stream.getvalue())
print((base/'export-profile.txt').read_text()[:2400])
