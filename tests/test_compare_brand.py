"""A compare query that names a brand rejects other brands.

Observed 2026-11-07: ``compare "Haier refrigerator"`` over Shophive, mega.pk,
Powerhouse and Telemart returned "Dawlance 9101 Single Door Refrigerator"
(0.607) and "PEL PRLP 2200 Life Pro Refrigerator" (0.604), which cleared the
0.6 threshold on the word "refrigerator" alone. Shophive states no vendor;
mega.pk states one on every product.
"""

from decimal import Decimal

import pytest

from shopextract._models import ExtractionResult, Product
from shopextract.compare import price
from shopextract.compare.price import _collect_matches, brand_conflict, known_brands


def product(title, vendor="", amount="1000"):
    return Product(title=title, vendor=vendor, price=Decimal(amount), currency="PKR",
                   product_url="https://store.invalid/" + title.lower().replace(" ", "-"))


SHOPHIVE = ExtractionResult(products=[product("Dawlance 9101 Single Door Refrigerator"),
                                      product("PEL PRLP 2200 Life Pro Refrigerator"),
                                      product("Haier HRF-678TGG Double Door Refrigerator")])
MEGA = ExtractionResult(products=[product("Haier HRF 438IFGA Two Door Refrigerator", "Haier"),
                                  product("Dawlance 91999 Avante Refrigerator", "Dawlance"),
                                  product("PEL Life Pro Refrigerator", "PEL")])


def titles(matches):
    return sorted(match.title for match in matches)


def test_vendors_from_one_store_reject_other_brands_in_another():
    matches = _collect_matches("Haier refrigerator", ["shophive", "mega"], [SHOPHIVE, MEGA], 0.6)
    assert all(match.title.lower().startswith("haier") for match in matches)
    assert "Haier HRF-678TGG Double Door Refrigerator" in titles(matches)


def test_stated_vendor_decides_over_title_words():
    brands = {"haier", "dawlance"}
    # A Dawlance listing mentioning Haier in its title is still Dawlance.
    assert brand_conflict("Haier fridge", product("Dawlance fridge like Haier", "Dawlance"), brands)
    assert not brand_conflict("haier fridge", product("HRF-438 fridge", "HAIER"), brands)


def test_brand_names_match_whole_words_only():
    assert brand_conflict("pel refrigerator", product("Pelican cooler"), {"pel"})
    assert not brand_conflict("PEL refrigerator", product("PEL Life Pro Refrigerator"), {"pel"})


def test_a_query_without_a_known_brand_constrains_nothing():
    assert not brand_conflict("double door refrigerator", product("Dawlance double door", "Dawlance"),
                              {"dawlance", "haier"})


def test_without_any_stated_vendor_brand_cannot_be_checked():
    # Known limitation: a store that states no vendor gives no brand vocabulary.
    assert known_brands([SHOPHIVE]) == set()
    matches = _collect_matches("Haier refrigerator", ["shophive"], [SHOPHIVE], 0.6)
    assert "Dawlance 9101 Single Door Refrigerator" in titles(matches)


def test_failed_store_does_not_break_the_vocabulary():
    assert known_brands([RuntimeError("down"), MEGA]) == {"haier", "dawlance", "pel"}


@pytest.mark.asyncio
async def test_currency_safe_compare_uses_every_store_vendors(monkeypatch):
    async def fake_extract(store, max_urls):
        return {"shophive": SHOPHIVE, "mega": MEGA}[store]
    monkeypatch.setattr(price, "extract", fake_extract)
    report = await price.compare("Haier refrigerator", ["shophive", "mega"], currency_safe=True)
    matched = [m.title for group in report.currency_groups.values() for m in group.matches] + [
        m.title for m in report.unranked]
    assert matched and all(title.lower().startswith("haier") for title in matched)
