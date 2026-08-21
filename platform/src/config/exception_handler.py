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

2. Serializer validation has a different shape. DRF's `ValidationError` carries a
   dict (`{"bar": ["This field is required."]}`), and the normalizer below would
   stringify it into something ugly. This app validates input by hand rather than
   through serializers, so it is not live today -- see the TODO.
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("django")


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        # DRF didn't recognize this -- an unanticipated crash.
        # Full traceback to the log; nothing specific to the user.
        logger.exception("Unhandled exception in %s", context["view"].__class__.__name__)
        return Response(
            {"detail": "Something went wrong on our end. Please try again.",
             "code": "internal_error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # TODO(#19): special-case rest_framework.exceptions.ValidationError before
    # this point -- pass its response.data through untouched under a "fields" key
    # instead of stringifying the dict. Not reachable until a serializer is used
    # for input validation.
    code = exc.get_codes() if hasattr(exc, "get_codes") else None
    response.data = {
        "detail": str(response.data.get("detail", response.data)),
        "code": code if isinstance(code, str) else "error",
    }
    if getattr(exc, "field", None):
        response.data["field"] = exc.field
    return response
