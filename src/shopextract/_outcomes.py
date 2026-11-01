"""Pure extraction outcomes shared by Python, CLI and native tools."""
from typing import Literal, Sequence

ExtractionOutcome = Literal['failed', 'partial', 'complete']


def assess_extraction_outcome(*, product_count: int, catalog_complete: bool | None,
                             errors: Sequence[object] = (),
                             incompleteness_reasons: Sequence[str] = ()) -> ExtractionOutcome:
    if product_count == 0:
        return 'failed'
    if catalog_complete is True and not errors and not incompleteness_reasons:
        return 'complete'
    return 'partial'
