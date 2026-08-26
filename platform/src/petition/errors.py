"""User-facing errors for the petition app.

This module is the catalog of what the backend is allowed to tell a user. Every
class here carries a safe default message; a call site may pass a more specific
one when it knows something the class cannot -- which file failed, which field is
blank -- but it may only build that message from values that are safe by
construction. Nothing should reach a browser except through a class defined here.

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


# Nothing raises the next two yet. `DocketParserAPIView` converts every parse
# failure to `ParseFailed` because it cannot tell the three causes apart -- see
# the TODO at the bottom. They are the vocabulary for the day it can, not
# leftovers.
class UnreadablePdf(PetitionError):
    default_detail = "That file could not be opened as a PDF."
    default_code = "unreadable_pdf"


class UnsupportedDocument(PetitionError):
    default_detail = "That file isn't a PA court document we can read."
    default_code = "unsupported_document"


class ParseFailed(PetitionError):
    # Currently the catch-all for every parse failure, so the message must not
    # name a cause: "unsupported county format" is a confident lie to someone
    # who uploaded a Word document. Prefer passing a message that names the
    # file -- ParseFailed(f"We couldn't read “{name}”. ...") -- since in a
    # multi-file upload knowing *which* file failed is most of the help.
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "We couldn't read that document. Make sure it's a PA docket sheet or court summary PDF."
    default_code = "parse_failed"


class MissingField(PetitionError):
    # Something the request should have carried and didn't. The response carries
    # `detail` and nothing else, so name the field in the message itself --
    # MissingField("Please enter an SSN.") rather than relying on a separate
    # key. A field name is safe to interpolate; see above.
    #
    # Not for a field that is present but unusable -- that is MalformedRequest.
    # The two read the same to a careless caller and differently to the user:
    # one means "you left something out", the other "what you sent is broken".
    default_code = "missing_field"
    default_detail = "A required field is missing."


class MalformedRequest(PetitionError):
    # Present but unusable: JSON that won't decode, a value in a shape we can't
    # read. Distinct from ParseFailed, which is about the *contents* of an
    # uploaded document rather than the request wrapping it.
    default_code = "malformed_request"
    default_detail = "The request couldn't be read."


# TODO(#19): tell the three parse failures apart. `DocketParserAPIView` catches
# Exception once and raises ParseFailed, which closes the PII leak and names the
# file but says the same thing for all three causes:
#
#     PdfReadError                       -> UnreadablePdf       (bad file)
#     ParseError from get_document_type() -> UnsupportedDocument (wrong document)
#     ParseError from Grammar.parse()     -> ParseFailed         (our gap)
#
# Only the third is our bug rather than a bad upload, and only the first two are
# something the user can act on, so the distinction is worth having.
#
# What blocks it: the middle two are the *same exception type*, separable only by
# which call raised them. A view cannot see that. So either this module maps from
# pypdf and parsimonious types -- coupling the Django app to docket_parser's
# transitive dependencies, and still not resolving the collision -- or
# docket_parser raises its own types and this module maps from those. The second
# is the only one that can distinguish them, at the cost of editing the
# standalone package and its CLI and tests.
#
# Either way, verify against real failures first: a scanned image-only PDF opens
# fine in pypdf and fails later as an unrecognized type, so it does not land
# where the table above suggests.
