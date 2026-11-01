"""Bounded deterministic status classes omitted by representative acceptance rows."""
import pytest
from tests.test_truthful_outcomes import crawl_boundary, crawl_result, URL
from shopextract.extractors.unified import UnifiedCrawlExtractor


@pytest.mark.asyncio
@pytest.mark.parametrize('status',[302,500,0,'bad',True])
@pytest.mark.parametrize('mode',['single','batch'])
async def test_untrusted_status_never_admits_product(crawl_boundary,status,mode):
    crawl_boundary.append(crawl_result(status))
    extractor=UnifiedCrawlExtractor()
    if mode=='single':
        assert await extractor._extract_with_browser(URL)==[]
    else:
        result=await extractor.extract_batch([URL])
        assert result.products==[] and result.complete is False and result.error
