"""Project-wide DRF exception handler.
This replaces DRF's default EXCEPTION_HANDLER — which already runs on every exception
in every view — so it raises the error-handling floor project-wide (including expunger) 
without touching those views, and its one addition is turning DRF's None 
(unhandled exception → Django's HTML 500) into a logged, JSON {"detail": "..."} 500. 

Two caveats: it's now the only thing logging unhandled tracebacks, and a future ValidationError 
would return a body with no detail key at all, breaking the frontend's detail-is-always-a-string contract.
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

