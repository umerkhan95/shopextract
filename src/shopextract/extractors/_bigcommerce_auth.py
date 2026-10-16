"""Explicit GraphQL token families and read-only customer context.

Token issuance, signature verification and revocation belong to BigCommerce.
Never infer a token's family by decoding an unverified JWT.
"""


AUTH_OPTIONS = {'token_type', 'customer_access_token', 'customer_id'}


def validate_auth(token_type='storefront', access_token=None,
                  customer_access_token=None, customer_id=None):
    if token_type not in ('storefront', 'private', 'impersonation'):
        raise ValueError('BigCommerce token_type must be storefront, private or impersonation')
    for value in (access_token, customer_access_token):
        if value is not None and (not isinstance(value, str) or not value or
                                  any(ord(c) <= 32 or ord(c) >= 127 for c in value)):
            raise ValueError('BigCommerce token must be a nonempty ASCII header value')
    if token_type != 'storefront' and not access_token:
        raise ValueError('BigCommerce server-side token must be supplied explicitly')
    if customer_access_token and (token_type != 'private' or customer_id is not None):
        raise ValueError('Customer access token requires private mode without customer_id')
    if customer_id is not None:
        if (token_type != 'impersonation' or not isinstance(customer_id, str) or
                not customer_id.isascii() or not customer_id.isdecimal() or int(customer_id) <= 0):
            raise ValueError('customer_id requires impersonation mode and a positive decimal ID')
    elif token_type == 'impersonation':
        raise ValueError('Impersonation mode requires customer_id')


def auth_headers(token, token_type, origin, customer_access_token=None, customer_id=None):
    validate_auth(token_type, token, customer_access_token, customer_id)
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}
    if token_type == 'storefront':
        headers['Origin'] = origin
    if customer_access_token:
        headers['X-Bc-Customer-Access-Token'] = customer_access_token
        # Otherwise invalidated sessions silently become anonymous pricing.
        headers['X-BC-Error-On-Invalid-Customer-Access-Token'] = 'true'
    if customer_id:
        headers['X-Bc-Customer-Id'] = customer_id
    return headers
