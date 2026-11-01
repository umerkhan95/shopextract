"""Rendered money interfaces/real browser consumer; designed before repair."""
from decimal import Decimal
import httpx
import pytest
from shopextract.extractors import _markdown_price as md
from shopextract.extractors.unified import UnifiedCrawlExtractor
from shopextract._normalize import normalize
from shopextract._models import Platform
from tests.test_truthful_outcomes import crawl_boundary,crawl_result
from tests.test_html_coverage import URL,ld

@pytest.mark.parametrize('text,amount,currency',[
 ('Price: KWD 1.234','1.234','KWD'),('Price: PKR 3,720','3720','PKR'),
 ('Price: USD 9007199254740993.10','9007199254740993.10','USD'),
 ('Price: EUR 0','0','EUR'),('Price: $12.50','12.50',None),('Price: ¥1200','1200',None)])
def test_exact_rendered_money(text,amount,currency):
    result=md.extract(text)
    assert Decimal(result['price'])==Decimal(amount)
    assert result.get('currency')==currency

@pytest.mark.parametrize('currency',['EUR','USD','GBP'])
def test_explicit_currency_positive(currency):
    assert md.extract('Price: '+currency+' 12.50')['currency']==currency

@pytest.mark.parametrize('text',['Price: EUR 1,23,4','Price: EUR NaN','Price: EUR -1'])
def test_rejected_rendered_not_observed_zero(text):
    assert 'price' not in md.extract(text)

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['context','conflict','metadata_zero','policy'])
async def test_actual_browser_money_context_presence_and_admission(crawl_boundary,kind):
    from shopextract._execution import execution_policy,ExecutionPolicy
    html=ld({'@type':'Product','name':'Widget','sku':'W1'}) if kind!='policy' else '<meta property="og:title" content="Returns"><meta property="og:type" content="website">'
    r=crawl_result(html=html);r.metadata={};r.markdown='Price: $12.50'
    if kind in ('context','conflict'):r.metadata={'og:price:currency':'CAD'}
    if kind=='conflict':r.markdown='Price: USD 12.50'
    if kind=='metadata_zero':r.metadata={'og:price:amount':0,'og:price:currency':'EUR'};r.markdown='Price: EUR 12.50'
    crawl_boundary.append(r)
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda q:httpx.Response(404))) as client:
        with execution_policy(ExecutionPolicy(browser=True),10):result=await UnifiedCrawlExtractor(http_client=client).extract(URL)
    if kind=='policy':assert result.products==[];return
    p=normalize(result.products[0],Platform.GENERIC,URL)
    assert p.price==Decimal('0' if kind=='metadata_zero' else '12.50')
    assert p.currency==('CAD' if kind=='context' else '' if kind=='conflict' else 'EUR')
    if kind=='conflict':assert result.complete is False and 'currency_conflict' in result.error

@pytest.mark.asyncio
async def test_actual_browser_kwd_precision_and_source(crawl_boundary):
 from shopextract._execution import execution_policy,ExecutionPolicy
 r=crawl_result(html=ld({'@type':'Product','name':'Kuwait widget','sku':'KWD1'}));r.markdown='Price: KWD 1.234';r.metadata={};r.url=URL
 crawl_boundary.append(r)
 async with httpx.AsyncClient(transport=httpx.MockTransport(lambda q:httpx.Response(404))) as c:
  with execution_policy(ExecutionPolicy(browser=True),10):result=await UnifiedCrawlExtractor(http_client=c).extract(URL)
 p=normalize(result.products[0],Platform.GENERIC,URL)
 assert p.price==Decimal('1.234') and p.currency=='KWD'
 for field in ('/price','/currency'):
  obs=next(o for o in p.evidence_contract.observations if o.field_path==field)
  assert obs.state.value=='observed'
  evidence=[e for e in p.evidence_contract.evidence if e.evidence_id in obs.evidence_ids]
  assert evidence and all(e.source_url==URL for e in evidence)
  assert any('KWD 1.234' in ((e.retained_data or {}).get('source_excerpt','')) for e in evidence)

@pytest.mark.parametrize('text,context,expected',[('Price: £12.50',None,None),('Price: £12.50','FKP','FKP'),('Price: ₩1200',None,None),('Price: ₩1200','KPW','KPW')])
def test_additional_ambiguous_symbols(text,context,expected):
 assert md.extract(text,currency=context).get('currency')==expected

@pytest.mark.parametrize('locale,expected',[(None,None),('fr-FR','1234.50')])
def test_space_grouping_whole_token(locale,expected):
 result=md.extract('Price: EUR 1 234,50',locale=locale)
 assert result.get('price')==expected

@pytest.mark.asyncio
async def test_existing_structured_currency_conflicts_metadata(crawl_boundary):
 from shopextract._execution import execution_policy,ExecutionPolicy
 r=crawl_result(html=ld({'@type':'Product','name':'Widget','sku':'W1','offers':{'price':'12.50','priceCurrency':'CAD'}}));r.url=URL;r.metadata={'og:price:currency':'USD'}
 crawl_boundary.append(r)
 async with httpx.AsyncClient(transport=httpx.MockTransport(lambda q:httpx.Response(404))) as c:
  with execution_policy(ExecutionPolicy(browser=True),10):result=await UnifiedCrawlExtractor(http_client=c).extract(URL)
 p=normalize(result.products[0],Platform.GENERIC,URL)
 assert p.price==Decimal('12.50') and p.currency=='' and not result.complete and 'currency_conflict' in result.error
 assert all(o.state.value!='observed' for o in p.evidence_contract.observations if o.field_path=='/currency')
 assert any(v=='CAD' for v in result.products[0]['_capture']['values'].values())

@pytest.mark.asyncio
@pytest.mark.parametrize('mode',['og_conflict','lowercase_agreement'])
async def test_browser_og_conflict_or_canonical_agreement(crawl_boundary,mode):
 from shopextract._execution import execution_policy,ExecutionPolicy
 html='<meta property="og:type" content="product"><meta property="og:title" content="Widget"><meta property="product:price:amount" content="12.50"><meta property="product:price:currency" content="CAD">' if mode=='og_conflict' else ld({'@type':'Product','name':'Widget','sku':'W1','offers':{'price':'12.50','priceCurrency':'usd'}})
 r=crawl_result(html=html);r.url=URL;r.metadata={'og:price:currency':'USD'}
 crawl_boundary.append(r)
 async with httpx.AsyncClient(transport=httpx.MockTransport(lambda q:httpx.Response(404))) as c:
  with execution_policy(ExecutionPolicy(browser=True),10):result=await UnifiedCrawlExtractor(http_client=c).extract(URL)
 p=normalize(result.products[0],Platform.GENERIC,URL)
 if mode=='og_conflict':
  assert p.currency=='' and not result.complete and 'currency_conflict' in result.error
  assert all(o.state.value!='observed' for o in p.evidence_contract.observations if o.field_path=='/currency')
  assert 'CAD' in result.products[0]['_capture']['values'].values()
 else:assert p.currency=='USD' and 'currency_conflict' not in (result.error or '')
