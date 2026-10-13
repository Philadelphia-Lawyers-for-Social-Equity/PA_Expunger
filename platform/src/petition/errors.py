"""
This is the catalog of every user-facing error message, each with a safe default
that call sites may only specialize with values safe by construction
(filenames, field names) — never raw exception text, which can leak PII. 

Raising rather than returning is deliberate: it's the only way to signal failure 
from deep helper functions that can't return a Response, which is also why those 
failures became log-only warnings in the first place.
return Response(...)` only works in the view method itself.

`default_code` stayed on each class. It isn't serialized -- the handler returns
`detail` and nothing else -- but DRF attaches it to the `ErrorDetail` and it is
what `get_codes()` would read, so it costs nothing and keeps the door open if
the frontend ever needs to branch on the kind of error rather than the prose.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class PetitionError(APIException):
    """Base for errors we intend an end user to read."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Something went wrong processing your request."
    default_code = "petition_error"


# docket_parser raising its own types requires editing the standalone package, its CLI, and its tests
class ParseFailed(PetitionError):
    # Currently the catch-all for every parse failure, so the message must not
    # name a cause. Prefer passing a message that names the file since in a
    # multi-file upload knowing *which* file failed is most of the help.
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "We couldn't read that document. Make sure it's a PA docket sheet or court summary PDF."
    default_code = "parse_failed"


class MissingField(PetitionError):
    # Something the request should have carried and didn't. The response carries
    # `detail` and nothing else, so name the field in the message itself --
    # MissingField("Please enter an SSN.") rather than relying on a separate key
    default_code = "missing_field"
    default_detail = "A required field is missing."


class MalformedRequest(PetitionError):
    # Present but unusable: JSON that won't decode, a value in a shape we can't
    # read. Distinct from ParseFailed, which is about the *contents* of an
    # uploaded document rather than the request wrapping it.
    default_code = "malformed_request"
    default_detail = "The request couldn't be read."
