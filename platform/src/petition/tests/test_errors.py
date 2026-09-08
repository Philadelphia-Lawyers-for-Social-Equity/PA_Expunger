"""Tests for `config.exception_handler`.

Every other assertion in the backend suite is on a 200 or a 201, so before this
file nothing in CI ever reached the exception handler -- the `EXCEPTION_HANDLER`
setting was installed, two commits changed behavior on top of it, and a green
run said nothing about whether any of it worked.

The handler lives in `config/`, not here, but the errors it serves are
`petition.errors` and the views that raise them are this app's. Keeping the
whole error path in one file beats splitting it across two directories for the
sake of matching the source tree.

The three tests here cover the handler's three behaviors, which are the whole of
what this project owns in it: call DRF, handle the `None`, propagate everything
else. Anything DRF decides -- what shape a `ValidationError` body takes, which
exceptions it recognizes -- is deliberately not asserted here.
"""

from config.exception_handler import exception_handler
from petition.errors import ParseFailed


def test_recognized_exception_is_returned_not_swallowed():
    """A response DRF built is passed back, not dropped.

    This tests one line -- the trailing `return response` -- and it is the most
    valuable test in the file, because that line looks like a redundant
    statement and has already been deleted once. Removing it makes the function
    fall off the end returning `None` for every exception DRF *did* recognize,
    and `handle_exception()` reads `None` as a decline and calls
    `raise_uncaught_exception()`. Every `APIException` in the project would
    route to the HTML 500 this module exists to prevent -- including the 401
    that `IsAuthenticated` raises on every endpoint, which is by far the
    most-travelled path through here.

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
    makes `logger.exception` the only record a crash leaves: delete it and
    crashes become silent, with the user seeing the generic message from the
    test below and nobody able to find out what happened.

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

    Calling the handler directly rather than through a request keeps this to
    three assertions with no client, database or patching. The cost is that it
    proves only that the branch computes the right thing; see the note below for
    what it cannot see.
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


# TODO(#19): this does not test that the handler is *reached*.
#
# It imports the function and calls it, so it passes even with
# `EXCEPTION_HANDLER` deleted from `config/settings/base.py`. Every realistic
# regression is in the wiring rather than in the four lines above:
#
#   - the setting removed, or its dotted path misspelled (which fails silently
#     -- DRF just falls back to its own handler)
#   - the trailing `return response`, which has been deleted once already and
#     which routes every APIException, including the 401 that `IsAuthenticated`
#     raises on every endpoint, into the HTML 500 this module exists to prevent
#   - DRF no longer returning `None` for the exception types assumed here
#
# Covering those needs a request-level test. Two are worth having:
#
# 1. `ParseFailed` from `petition:parse-docket` returns 422 with none of the
#    exception text in the body -- the regression test for the PII leak, since a
#    parsimonious ParseError stringifies to a snippet of the document being
#    parsed. Mock `docket_parser.parse_pdf` to raise an exception whose message
#    is obvious PII; a genuinely malformed PDF raises `PdfReadError`, which
#    carries nothing sensitive and would pass while the leak was open. Because
#    `ParseFailed` is an `APIException`, this also covers `return response`.
#
# 2. The `None` branch end to end. Harder than it sounds: reaching it means
#    finding code the views do not already guard, and `DocketParserAPIView`
#    catches `Exception` around the parser. Patching `petition.views.DocxTemplate`
#    to raise in `GeneratorReportAPIView` works, since it runs after that view's
#    own try/except. Set `raise_request_exception = False` on the test client
#    first, or a regression propagates the exception into the test instead of
#    letting Django build the HTML response the assertion is meant to catch.
