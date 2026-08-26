"""User-facing errors for the petition app.

This module is the catalog of everything the backend is allowed to tell a user.
If a message is not defined here, it should not reach a browser.

Why raising beats returning
---------------------------

`return Response(...)` only works in the view method itself. `charges_from_docket()`
and `fines_from_parser()` run several frames down and physically cannot return a
response -- which is why their four failure cases became `logger.error` calls and
nothing else. A raise crosses those frames. That's not incidental; it's a large
part of why the "warnings on successful responses" problem ended up log-only in
the first place.

Never interpolate exception text into a detail message. `parsimonious.exceptions.
ParseError` includes a snippet of the document being parsed, which for a real
client is their name, date of birth, and charges. Interpolate only values that
are safe by construction -- a filename the user just chose, a field name, a
count. The full exception belongs in the log.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


# `default_code` stayed on each class. It isn't serialized -- the handler returns
# `detail` and nothing else -- but DRF attaches it to the `ErrorDetail` and it is
# what `get_codes()` would read, so it costs nothing and keeps the door open if
# the frontend ever needs to branch on the kind of error rather than the prose.
class PetitionError(APIException):
    """Base for errors we intend an end user to read."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Something went wrong processing your request."
    default_code = "petition_error"


class UnreadablePdf(PetitionError):
    default_detail = "That file could not be opened as a PDF."
    default_code = "unreadable_pdf"


class UnsupportedDocument(PetitionError):
    default_detail = "That file isn't a PA court document we can read."
    default_code = "unsupported_document"


class ParseFailed(PetitionError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "We couldn't read this document. It may use a court format we don't handle yet."
    default_code = "parse_failed"


class MissingField(PetitionError):
    # The response carries `detail` and nothing else, so name the field in the
    # message itself -- MissingField("Please enter an SSN.") rather than relying
    # on a separate key. A field name is safe to interpolate; see above.
    default_code = "missing_field"
    default_detail = "A required field is missing."


# TODO(#19): map docket_parser exceptions onto the classes above so every call
# site converts them the same way. PdfReadError -> UnreadablePdf; ParseError from
# get_document_type() -> UnsupportedDocument; ParseError from Grammar.parse() ->
# ParseFailed.
#
# Open question: importing pypdf and parsimonious into a Django view couples this
# app to docket_parser's transitive dependencies. The alternative is for
# docket_parser to raise its own exception types that this module maps from.
