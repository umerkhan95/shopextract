"""Map detection diagnostics onto the C1 response contract.

``generic`` with confidence 0 is a real answer only when the store page was
read. When the page itself could not be fetched, the platform is unknown and
the command fails with the cause; when the probe deadline expired, the answer
is returned as partial.
"""

from ._cli_core import CliFailure

_PAGE_STATUS_CAUSES = {401: "blocked", 403: "blocked", 429: "rate_limited"}


def detect_failure(context, url):
    if context.rate_limited:
        return CliFailure("E_OPERATION", "Platform detection was rate limited by the store.",
                          cause="rate_limited", retryable=True, errors=list(context.errors),
                          retry_after_seconds=context.retry_after_seconds)
    if context.result.platform.value != "generic" or context.timed_out or context.page_status == 200:
        return None
    if context.page_status in _PAGE_STATUS_CAUSES:
        cause = _PAGE_STATUS_CAUSES[context.page_status]
    else:
        from ._cli_extract import _source_failure
        # Only the page's own failure decides; API probe 404s are expected elsewhere.
        page_errors = [error for error in context.errors
                       if error.startswith(url) or error.endswith(" " + url)]
        cause = _source_failure({"errors": page_errors}).cause
    return CliFailure("E_OPERATION", "The store page could not be read; the platform is unknown.",
                      cause=cause, retryable=cause in {"rate_limited", "network_unreachable"},
                      errors=list(context.errors))


def detect_warnings(context):
    return ["detection_timeout"] if context.timed_out else []
