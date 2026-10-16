"""Controlled generic parser mechanisms C07-C11/C22/C24; no network/models."""
import json

import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract.categories import normalize_with_categories
from shopextract.categories.contracts import (
    AdapterContext, CategoryLimits, CategoryOptions, CategoryScope, CategorySelector,
    MappingRule, TargetRegistry,
)
from shopextract.categories.adapters.generic import observe_categories
from shopextract.extractors.feed import GoogleFeedExtractor
from shopextract.extractors._opengraph import OpenGraphExtractor
from shopextract.extractors._schema_org import SchemaOrgExtractor

URL = 'https://merchant.test/catalog/product'
SCOPE = CategoryScope(Platform.GENERIC, 'https://merchant.test/catalog')
CONTEXT = AdapterContext(SCOPE)


def schema(category=..., **extra):
    raw = {'@type': 'Product', 'name': 'Dress', 'offers': {'price': '10', 'priceCurrency': 'EUR'}, **extra}
    if category is not ...:
        raw['category'] = category
    html = '<script type="application/ld+json">' + json.dumps(raw) + '</script>'
    return SchemaOrgExtractor.extract_from_html(html, URL)[0]


def options(*rules):
    return CategoryOptions(SCOPE, TargetRegistry('test:canonical', 'v1', ('dress',)), rules)


def test_c07_jsonld_memberships_and_opaque_delimiters():
    raw = schema(['Boots', 'Sale', 'Boots'])
    observation = observe_categories(raw, context=CONTEXT)[0]
    assert {t.label for t in observation.terms} == {'Boots', 'Sale'}
    assert len(observation.terms) == 2
    assert observation.relation == 'memberships' and observation.parent_edges == ()
    assert all(f.support == SupportState.OBSERVED for t in observation.terms for f in t.facts)
    for value in ('https://example.test/tax/12', r'A\>B / C'):
        term = observe_categories(schema(value), context=CONTEXT)[0].terms[0]
        assert term.ref.native_id == (value if value.startswith('https:') else None)
        assert term.label == (None if value.startswith('https:') else value)
        assert not any(f.binding.facet == 'raw_path' for f in term.facts)


@pytest.mark.parametrize('parser,body', [
    ('xml', '<rss xmlns:g="http://base.google.com/ns/1.0"><channel><item><g:id>D1</g:id><title>Dress</title><g:google_product_category>2271</g:google_product_category><g:product_type>Merchant &gt; Dresses</g:product_type></item></channel></rss>'),
    ('csv', 'id,title,google_product_category,product_type\nD1,Dress,2271,"Merchant > Dresses"\n'),
])
def test_c08_feed_real_parser_retains_separate_namespaces(parser, body):
    parse = getattr(GoogleFeedExtractor, '_parse_' + parser)
    legacy = parse(body, URL)[0]
    assert 'category_declarations' not in legacy
    assert 'google_product_category' not in legacy
    raw = parse(body, URL, include_categories=True)[0]
    wrapped = normalize_with_categories(raw, Platform.GENERIC, SCOPE.store_url, category_options=options(
        MappingRule('gpc', 'v1', CategorySelector('google:product_category', None, native_id='2271', allow_unknown_version=True), ('dress',)),
    ))
    assert wrapped is not None
    standard = next(o for o in wrapped.observations if o.taxonomy_kind == 'standard')
    custom = next(o for o in wrapped.observations if o.taxonomy_kind == 'custom_type')
    assert standard.terms[0].ref.native_id == '2271'
    assert standard.terms[0].ref.taxonomy_version is None
    assert standard.terms[0].ref.merchant_scope is None
    assert custom.terms[0].label == 'Merchant > Dresses'
    assert custom.terms[0].ref.namespace == 'google:product_type'
    assert all(o.parent_edges == () and o.relation != 'ordered_path' for o in wrapped.observations)
    assert any(m.status == 'mapped' and m.target_ids == ('dress',) for m in wrapped.mappings)
    assert standard.terms[0].facts[0].pointer.startswith('/category_declarations/')


def test_c08_declared_google_path_and_one_xml_decode():
    path = 'Apparel & Accessories > Clothing > Dresses'
    raw = GoogleFeedExtractor._parse_csv('id,title,google_product_category,product_type\nD1,Dress,' + path + ',"Home > Bags, wallets"\n', URL, include_categories=True)[0]
    observation = observe_categories(raw, context=CONTEXT)[0]
    term = observation.terms[0]
    assert term.ref.native_id is None and term.label is None
    assert term.facts[0].binding.facet == 'raw_path' and term.facts[0].raw_value == path
    wrapped = normalize_with_categories(raw, Platform.GENERIC, SCOPE.store_url, category_options=options(
        MappingRule('path', 'v1', CategorySelector('google:product_category', None, raw_path=path, allow_unknown_version=True), ('dress',)),
    ))
    assert any(m.status == 'mapped' for m in wrapped.mappings)
    assert raw['category_declarations']['product_type'] == 'Home > Bags, wallets'
    xml = '<rss xmlns:g="http://base.google.com/ns/1.0"><item><title>Dress</title><g:product_type>Home &amp;gt; Bags</g:product_type></item></rss>'
    retained = GoogleFeedExtractor._parse_xml(xml, URL, include_categories=True)[0]
    assert retained['category_declarations']['product_type'] == 'Home &gt; Bags'
    assert observe_categories(retained, context=CONTEXT)[1].terms[0].label == 'Home &gt; Bags'


def test_c09_category_code_context_and_thing():
    refs = []
    for namespace in ('https://tax.test/X', 'https://tax.test/Y'):
        observation = observe_categories(schema({'@type':'CategoryCode', 'codeValue':'12', 'inCodeSet':{'@id':namespace}, 'name':'Stiefel'}), context=CONTEXT)[0]
        term = observation.terms[0]
        refs.append(term.ref)
        assert term.ref.namespace == namespace and term.ref.native_id == '12'
        assert observation.taxonomy_kind == 'structured_code'
        assert {f.binding.facet for f in term.facts} == {'native_id', 'label', 'code_context'}
        assert all(f.support == SupportState.OBSERVED for f in term.facts)
    assert refs[0] != refs[1]
    raw = schema({'@type':'CategoryCode', 'codeValue':'12'})
    term = observe_categories(raw, context=CONTEXT)[0].terms[0]
    assert not any(f.binding.facet == 'code_context' and f.support == SupportState.OBSERVED for f in term.facts)
    wrapped = normalize_with_categories(raw, Platform.GENERIC, SCOPE.store_url, category_options=options(
        MappingRule('missing-set','v1',CategorySelector(term.ref.namespace,None,native_id='12',allow_unknown_version=True),('dress',)),
    ))
    assert all(m.status != 'mapped' for m in wrapped.mappings)
    thing = observe_categories(schema({'@type':'Thing','@id':'https://tax.test/node/12','name':'Boots'}), context=CONTEXT)[0].terms[0]
    assert thing.ref.native_id == 'https://tax.test/node/12' and thing.label == 'Boots'


@pytest.mark.parametrize('value,state', [(..., 'missing'), (None,'null'), ('','empty'), ([], 'empty'), ({'bad':True},'malformed')])
def test_c10_schema_raw_states(value, state):
    observation = observe_categories(schema(value), context=CONTEXT)[0]
    assert observation.source_state == state and observation.terms == ()
    if value is not ...:
        assert observation.facts[0].raw_value == value


@pytest.mark.parametrize('body,state', [
    ('title\nDress\n', 'missing'), ('title,product_type\nDress,\n','empty'),
])
def test_c10_feed_presence_before_defaults(body,state):
    raw = GoogleFeedExtractor._parse_csv(body, URL, include_categories=True)[0]
    assert raw['product_type'] == ''
    assert observe_categories(raw, context=CONTEXT)[1].source_state == state
    absent = GoogleFeedExtractor._parse_xml('<rss><item><title>Dress</title></item></rss>',URL,include_categories=True)[0]
    empty = GoogleFeedExtractor._parse_xml('<rss xmlns:g="http://base.google.com/ns/1.0"><item><title>Dress</title><g:product_type/></item></rss>',URL,include_categories=True)[0]
    assert observe_categories(absent,context=CONTEXT)[1].source_state == 'missing'
    assert observe_categories(empty,context=CONTEXT)[1].source_state == 'empty'


def test_c10_opengraph_repeats_retained_unknown_and_default_unchanged():
    html = '<meta property="og:title" content="Dress"><meta property="product:category" content="Boots"><meta property="product:category" content="Sale"><meta property="product:category" content="">'
    legacy = OpenGraphExtractor.extract_from_html(html, URL)[0]
    assert legacy['product:category'] == 'Sale' and 'category_declarations' not in legacy
    raw = OpenGraphExtractor.extract_from_html(html,URL,include_categories=True)[0]
    observation = observe_categories(raw,context=CONTEXT)[0]
    assert {t.label for t in observation.terms} == {'Boots','Sale'}
    assert observation.completeness == 'unknown' and observation.parent_edges == ()
    assert raw['category_declarations']['product:category'] == ['Boots','Sale','']


def test_c11_mutation_retention_and_llm_do_not_gain_support():
    raw = schema({'@type':'Thing','@id':'https://tax.test/12','name':'Boots'})
    raw['category']['@id'] = 'https://tax.test/99'
    term = observe_categories(raw,context=CONTEXT)[0].terms[0]
    by_facet = {f.binding.facet:f for f in term.facts}
    assert by_facet['native_id'].support == SupportState.UNSUPPORTED
    assert by_facet['label'].support == SupportState.OBSERVED
    oversized = observe_categories(schema('x'*4097),context=CONTEXT)[0].terms[0]
    assert oversized.facts[0].support == SupportState.UNSUPPORTED
    model = {'title':'Dress','product_type':'Boots'}
    capture(model,URL,'llm',source={})
    observation = observe_categories(model,context=CONTEXT)[0]
    assert observation.terms[0].facts[0].support == SupportState.UNSUPPORTED
    assert observation.completeness == 'unknown'


@pytest.mark.parametrize('cap', [0,1,2])
def test_c22_global_terms_and_relation_caps(cap):
    observations = observe_categories(schema(['Boots','Sale','Hats']),context=AdapterContext(SCOPE,CategoryLimits(terms=cap,relation_refs=cap)))
    assert sum(len(o.terms) for o in observations) == cap
    assert all(o.completeness == 'partial' for o in observations)
    assert all(o.reason == 'category_budget_reached' for o in observations)
