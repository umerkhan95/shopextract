"""Compile identical immutable schema snapshots once; validate every response."""
from functools import lru_cache
import json
from jsonschema.validators import validator_for


@lru_cache(maxsize=16)
def _compiled(canonical_schema):
    # Private fresh snapshot prevents mutations of advertised dictionaries from
    # changing a cached validator. Same draft selection as jsonschema.validate.
    document=json.loads(canonical_schema)
    validator_type=validator_for(document)
    validator_type.check_schema(document)
    return validator_type(document)


def schema_validate(instance, schema):
    canonical=json.dumps(schema,sort_keys=True,separators=(',',':'))
    _compiled(canonical).validate(instance)
