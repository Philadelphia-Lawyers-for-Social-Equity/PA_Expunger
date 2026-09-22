"""Tests for `config.exception_handler`.

The handler lives in `config/`, not here, but the errors it serves are
`petition.errors` and the views that raise them are this app's

The three tests here cover the handler's three behaviors, which are the whole of
what this project owns in it: call DRF, handle the `None`, propagate everything
else. Anything DRF decides is deliberately not asserted here
"""

from config.exception_handler import exception_handler
from petition.errors import ParseFailed


def test_recognized_exception_is_returned_not_swallowed():
    """A response DRF built is passed back, not dropped.

    `handle_exception()` reads `None` as a decline and calls `raise_uncaught_exception()`

    `response is not None` is the assertion that belongs to us. That DRF builds
    a Response for an `APIException` is DRF's guarantee; propagating it is ours.
    """
    response = exception_handler(ParseFailed("nope"), {"view": object()})

    assert response is not None
    assert response.status_code == 422
    assert response.data == {"detail": "nope"}


def test_unhandled_exception_logs_the_traceback(caplog):
    """The traceback reaches the log, since nothing else records it now.

    Once the handler returns a Response for unhandled exceptions, Django's 500
    path never runs and its `django.request` logger never fires with it. That
    makes `logger.exception` the only record a crash leaves

    The exception is raised inside a real `try/except` because that is how DRF
    calls the handler, and because it matters here: called outside one,
    `logger.exception` finds no active exception and records "NoneType: None"
    for `exc_info`, so this test would pass while capturing no traceback at all.
    """
    try:
        raise RuntimeError("boom")
    except RuntimeError as exc:
        exception_handler(exc, {"view": object()})

    assert "boom" in caplog.text
    assert "RuntimeError" in caplog.text


def test_unhandled_exception_returns_json_500():
    """An exception DRF does not recognize gets a generic JSON 500.

    This is the handler's `None` branch, and the only original logic in the
    module: DRF's default handler builds a Response for `APIException` (plus
    `Http404` and Django's `PermissionDenied`) and returns `None` for anything
    else, at which point `handle_exception()` re-raises and Django renders HTML
    -- which has no `detail` for the frontend, and under DEBUG dumps every
    frame's locals, which in these views hold the parsed docket.
  
    """
    # `context` needs a "view" key and nothing else -- the branch's one use of
    # it is `context["view"].__class__.__name__`, for the log line.
    response = exception_handler(RuntimeError("boom"), {"view": object()})

    assert response.status_code == 500

    # Assert on `.data`, not `.content`. A Response built outside the request
    # cycle has no renderer attached, so touching `.content` raises
    # "AssertionError: .accepted_renderer not set on Response".
    assert response.data == {"detail": "Something went wrong on our end. Please try again."}

    # The equality above is the real assertion: an unhandled exception is by
    # definition one nobody has vetted for what it might contain, so the whole
    # of it stays in the log and none of it goes in the body. "boom" appearing
    # here would mean that rule had been relaxed.