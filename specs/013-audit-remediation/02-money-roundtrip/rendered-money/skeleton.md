# Rendered money G2 skeleton — no code

extract(markdown,url='',*,currency=None,locale=None)->dict and
extract_price(text,*,currency=None,locale=None)->tuple[str,str|None]|None retain
positional interfaces. Candidate recognition returns original amount text,explicit
code/symbol; actual interpretation calls existing Normalizer.money/ISO membership,
never float or duplicate separators. Rejections don't become zero. Unknown symbol
has amount without invented currency. Diagnostic currency_conflict retained.
Browser passes captured metadata/structured context,uses presence for price0,and
records original text+transformation/source capture. Generic policy admission unchanged.
