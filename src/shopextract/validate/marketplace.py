"""Marketplace-specific product validation rules.

Each marketplace has its own required fields, format rules, and value
constraints. validate() checks all products against the chosen marketplace
and returns a ValidationReport with issues.
"""

from __future__ import annotations

from .._models import ValidationIssue, ValidationReport

# Marketplace rule definitions: required fields + format constraints
_MARKETPLACE_RULES: dict[str, dict] = {
    "google_shopping": {
        "required": ["title", "price", "image_url", "product_url"],
        "recommended": ["gtin"],
        "constraints": {
            "description": {"max_length": 5000},
            "title": {"max_length": 150},
        },
    },
    "idealo": {
        "required": [
            "title", "price", "product_url", "image_url",
            "sku_or_external_id", "delivery_time", "delivery_cost",
        ],
        "recommended": ["gtin"],
        "constraints": {
            "title": {"max_length": 255},
        },
    },
    "amazon": {
        "required": ["title", "price", "image_url", "gtin", "brand", "condition"],
        "recommended": [],
        "constraints": {
            "title": {"max_length": 200},
            "description": {"max_length": 2000},
        },
    },
    "ebay": {
        "required": ["title", "price", "image_url", "condition"],
        "recommended": ["gtin"],
        "constraints": {
            "title": {"max_length": 80},
        },
    },
}

_SUPPORTED_MARKETPLACES = list(_MARKETPLACE_RULES.keys())


def validate(
    products: list[dict],
    marketplace: str = "google_shopping",
) -> ValidationReport:
    """Validate products against marketplace requirements.

    Args:
        products: List of product dicts to validate.
        marketplace: Target marketplace name.

    Returns:
        ValidationReport with valid/invalid counts and issues.
    """
    if marketplace not in _MARKETPLACE_RULES:
        raise ValueError(
            f"Unsupported marketplace: {marketplace!r}. "
            f"Supported: {_SUPPORTED_MARKETPLACES}"
        )

    rules = _MARKETPLACE_RULES[marketplace]
    report = ValidationReport(marketplace=marketplace, total=len(products))
    invalid_indices: set[int] = set()

    for idx, product in enumerate(products):
        title = _get_str(product, "title")
        issues = _check_required(idx, title, product, rules)
        issues.extend(_check_constraints(idx, title, product, rules))
        issues.extend(_check_recommended(idx, title, product, rules))

        for issue in issues:
            report.issues.append(issue)
            if issue.severity == "error":
                invalid_indices.add(idx)
            else:
                report.warnings += 1

    report.invalid = len(invalid_indices)
    report.valid = report.total - report.invalid
    return report


def _check_required(
    idx: int, title: str, product: dict, rules: dict,
) -> list[ValidationIssue]:
    """Check that all required fields are present and non-empty."""
    issues: list[ValidationIssue] = []
    for field_name in rules.get("required", []):
        if field_name == "sku_or_external_id":
            if not _get_str(product, "sku") and not _get_str(product, "external_id"):
                issues.append(ValidationIssue(
                    product_index=idx, product_title=title,
                    field="sku/external_id",
                    error="Either 'sku' or 'external_id' is required",
                ))
            continue

        value = _get_str(product, field_name)
        if not value:
            issues.append(ValidationIssue(
                product_index=idx, product_title=title,
                field=field_name, error=f"Required field '{field_name}' is missing or empty",
            ))
    return issues


def _check_constraints(
    idx: int, title: str, product: dict, rules: dict,
) -> list[ValidationIssue]:
    """Check field format and value constraints."""
    issues: list[ValidationIssue] = []
    constraints = rules.get("constraints", {})

    for field_name, constraint in constraints.items():
        value = _get_str(product, field_name)
        if not value:
            continue

        max_len = constraint.get("max_length")
        if max_len and len(value) > max_len:
            issues.append(ValidationIssue(
                product_index=idx, product_title=title,
                field=field_name,
                error=f"Exceeds max length ({len(value)} > {max_len})",
            ))

    price = product.get("price")
    if price is not None and _is_numeric(price) and float(price) < 0:
        issues.append(ValidationIssue(
            product_index=idx, product_title=title,
            field="price", error="Price cannot be negative",
        ))

    return issues


def _check_recommended(
    idx: int, title: str, product: dict, rules: dict,
) -> list[ValidationIssue]:
    """Check recommended (warning-level) fields."""
    issues: list[ValidationIssue] = []
    for field_name in rules.get("recommended", []):
        value = _get_str(product, field_name)
        if not value:
            issues.append(ValidationIssue(
                product_index=idx, product_title=title,
                field=field_name,
                error=f"Recommended field '{field_name}' is missing",
                severity="warning",
            ))
    return issues


def _get_str(product: dict, key: str) -> str:
    """Get a string value from product dict, handling None."""
    val = product.get(key)
    if val is None:
        return ""
    return str(val).strip()


def _is_numeric(value: object) -> bool:
    """Check if a value can be interpreted as a number."""
    try:
        float(value)  # type: ignore[arg-type]
        return True
    except (TypeError, ValueError):
        return False
