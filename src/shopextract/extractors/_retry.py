"""Single retry delay bounded by the current operation deadline."""
import asyncio
import math
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from .._execution import remaining_execution_seconds


async def wait_for_retry(header,default=2):
    try:
        delay=float(header)
        if not math.isfinite(delay) or delay<0:raise ValueError()
    except (ValueError,TypeError):
        try:
            at=parsedate_to_datetime(header)
            if at.tzinfo is None:at=at.replace(tzinfo=timezone.utc)
            delay=max(0.0,(at-datetime.now(timezone.utc)).total_seconds())
        except (ValueError,TypeError,OverflowError,AttributeError):delay=default
    remaining=remaining_execution_seconds()
    if remaining is not None and (remaining<=0 or delay>=remaining):return False
    await asyncio.sleep(delay)
    remaining=remaining_execution_seconds()
    return remaining is None or remaining>0
