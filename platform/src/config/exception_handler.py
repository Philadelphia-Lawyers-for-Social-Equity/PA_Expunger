"""Project-wide DRF exception handler.

The seam this hooks
-------------------

DRF already wraps every view method in a try/except. `APIView.dispatch()` catches
anything your handler raises and calls `handle_exception(exc)`, which looks up
`REST_FRAMEWORK['EXCEPTION_HANDLER']` and calls it. The default one,
`rest_framework.views.exception_handler`, does two things:

- If the exception is an `APIException` (or `Http404` / `PermissionDenied`), it
  builds a `Response` with that exception's `status_code` and `detail`.
- For anything else, it returns `None` -- and DRF re-raises, so Django turns it
  into a bare 500 (an HTML debug page under DEBUG=True, which is exactly what
  GeneratorReportAPIView produces today).

So this is not a new interception layer. It replaces a function that already runs
on every exception in every DRF view in the project, which is why installing it
also raises the floor for the expunger endpoints without touching them.

Two things to watch
-------------------

1. We now own the traceback. Once this returns a Response for unhandled
   exceptions, Django's 500 path never runs, so its `django.request` logger never
   fires. The `logger.exception(...)` call below is load-bearing -- drop it and
   crashes become silent.

2. `detail` is not always a string. Recognized exceptions pass through in
   whatever shape DRF built, and `ValidationError` carries a dict keyed by field
   name (`{"bar": ["This field is required."]}`) or a bare list, which DRF
   returns as the response body with no `detail` key at all. Nothing in this app
   raises one yet -- input is validated by hand -- but the first serializer added
   changes what the frontend receives.

The response contract, for the frontend's sake: `detail`, a string, on
everything this app raises and on every DRF built-in. See the caveat above for
the one shape that will not have it.
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("django")


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    # DRF is being deliberate here: its contract is that it owns APIException and nothing else.
    # The EXCEPTION_HANDLER setting exists as the documented slot for a project to extend drf_exception_handler

    # `None` is DRF declining the exception, not failing on it: the default
    # handler only builds a Response for APIException (plus Http404 and Django's
    # PermissionDenied, which it converts first). Anything else -- an
    # AttributeError several frames down, a pypdf or parsimonious failure --
    # falls through, and `handle_exception()` calls `raise_uncaught_exception()`.
    # Django then renders HTML: a traceback page under DEBUG, a generic 500
    # otherwise. Neither has a `detail` for the frontend to read, and the DEBUG
    # one dumps every frame's locals, which here hold the parsed docket.
    # Catching the None is what makes an unanticipated crash answerable.
    if response is None:
        # Full traceback to the log; nothing specific to the user.
        logger.exception("Unhandled exception in %s", context["view"].__class__.__name__)
        return Response(
            {"detail": "Something went wrong on our end. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Recognized exceptions pass through as DRF built them: {"detail": "..."}.
    # Returning the response is what stops handle_exception() from treating this
    # as another decline and re-raising.
    return response

