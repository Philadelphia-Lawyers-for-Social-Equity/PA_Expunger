# Glossary (resusable data structure definitions)

**Petition Fields** is a data structure (typically JSON or python dict)
containing:

    - petitioner:
        - name: string, full name
        - aliases: list of strings, aliases of petitioner
        - dob: petitioners date of birth, iso formatted, such as
                "2019-10-17"
        - ssn: social security number. Only used as input on generator.
        - address: # Only used as input on generator.
            - street1: string, address line 1
            - street2: string, address line 2
            - city: string
            - state: string, two letter US state code
            - zipcode: string of numbers
    - petitions (list of dicts containing):
        -docket info
            - otn: string
            - judge: string, full name of the judge
            - ratio: string, may be "full" if every charge could be
                    expunged, or "partial" if some charges have been
                    excluded.
            - complaint date: iso formatted date or null
            - arrest date: iso formatted date or null
        - docket numbers: List of docket numbers
        - charges (list of dicts containing):
            - statute: string
            - description: string
            - grade: string (usually 2-3 chars)
            - date: date, formatted such as “2020-10-11”
            - disposition: string
        - fines (dict of):
            - total: decimal number
            - paid: decimal number
        - county: string (this field is only included if the parsed document is a court summary)
        - category: string (this field is only included if the parsed document is a court summary)

# API

## Errors

Every failing request returns JSON with a `detail` key holding a message
intended to be shown to the user as-is:

```json
{"detail": "We couldn't read “summary.pdf”. Make sure it's a PA docket sheet or court summary PDF."}
```

This holds for errors raised by the application and for those raised by Django
REST Framework itself (401 on a missing or expired token, 405, 429). Clients
should read `detail` and render it; there is no error code to branch on.

| Status | Meaning |
| --- | --- |
| 400 | Something is missing or malformed in the request. `detail` names it. |
| 401 | No access token, or it has expired. Refresh and retry. |
| 422 | The request was well formed, but a document could not be parsed. |
| 500 | Unanticipated failure. `detail` is generic; the cause is in the server log. |

Two caveats for client authors:

- The `generate/` and `generator-report/` endpoints return a `.docx` body on
  success, so a client requesting them as binary must decode the response body
  before reading `detail` on failure.
- A DRF `ValidationError` — which nothing currently raises, but a future
  serializer would — returns a field-keyed object rather than a `detail` string.

## Authentication

The API handles authentication via JSON Web Tokens, as provided by [django rest
framework simple
jwt](https://github.com/davesque/django-rest-framework-simplejwt). Endpoints
are:

- **api/v0.2.0/auth/token/**
  - POST accepts: `{"username": "xxx", "password": "yyy"}`
  - returns: `{"access": "...", "refresh": "..."}`
  - The access token is used in the `Authorization: Bearer ...`
    when making later requests to private endpoints
  - The refresh token can be used to retrieve a fresh access token when the
    access token expires.
- **api/v0.2.0/refresh/token**

  - POST accepts: `{"refresh": "..."}`
  - returns: `{"access": "..."}`

- **api/v0.2.0/expunger/attorney/<pk>**
  - Requires access token
  - GET returns attorney json, including:
    - url (api link for this attorney)
    - pk (integer id)
    - bar (attorney's bar identifier, string)
    - name (annorney's full name

## Expunger

The expunger section of the API is intended to handle profile & system
information that affects the user rather than the petition. For example,
allowing the user to select their default attorney or update their email
address.

- **api/v0.2.0/expunger/attorneys/**

  - Requires access token header
  - GET produces list of available attorneys, each formatted as above

- **api/v0.2.0/expunger/organization/<pk>**

  - Requires access token header
  - GET returns organization json, including:
    - url (api link for this organization)
    - pk (integer id)
    - name
    - phone
    - address
      - street1
      - street2 (may be null)
      - city
      - state
      - zipcode

- **api/v0.2.0/expunger/organizations**

  - Requires access token header
  - GET produces a list of available organizations, each formatted as above

- **api/v0.2.0/expunger/dockets**

  - Requires access token header
  - GET produces a list of dockets that match the firstName and lastName query parameters
    - The endpoint will return an error if firstName and lastName are not both present

- **api/v0.2.0/expunger/my-profile/**
  - Requires access token header
  - GET produces the authenticated users profile, or 404, including
    - attorney (see the attorney endpoint for all details)
    - organization (see the organization endpoint for all details)
    - user
      - first_name
      - last_name
      - email
      - username
  - POST allows the creation of a new profile, if the user has none
    - accepts `{"attorney": attorney pk, "organization": organization pk}`
    - attorney and organization are required
  - PUT allows updating an existing profile
    - accepts `{"attorney": attorney pk, "organization": organization pk}`
    - attorney and organization are optional

## Petition

The petition section handles the preparation of petition paperwork and docket
parsing. This is where the real work gets done.

- **api/v0.2.0/petition/generate/**

  - Requires access token header
  - POST with valid data produces a microsoft .docx petition
  - Expects JSON of
    - petitioner
      - name: string, full name
      - aliases: list of strings, aliases of the petitioner
      - dob: petitioners date of birth, iso formatted, such as
        "2019-10-17"
      - ssn: string, petitioner's social security number
      - address:
        - street1: string
        - street2: string or null
        - city: string
        - state: string, two character state abbreviation
        - zipcode: string formatted zip code
    - petition
      - date: iso formatted date, such as "2019-10-17"
      - ratio: string, must be "full" if every charge is to be
      expunged, or "partial" if some charges are excluded.
      - otn: string
      - judge: string, full name of the judge
      - complaint_date: iso formatted date or null
      - arrest_date: iso formated date or null
    - dockets: list of strings, each string is a docket number
    - fines:
      - total: decimal number
      - paid: decimal number
    - charges: (list of dicts containing)
      - date: iso formated date
      - statute: string
      - grade: string
      - description: string
      - disposition: string
  - Errors
    - 400 if any of the fields above is absent; `detail` names the missing one

- **api/v0.2.0/petition/parse-docket/**
    - Requires access token header
    - POST of one or more docket files produces JSON of Petition Fields
    - Expects multipart form data
      - docket_file: one or more PDFs. Repeat the key for multiple files.
      - petitioner: optional JSON object of already-known petitioner fields,
        merged into the parsed result
    - Files are grouped into petitions by OTN, so N files may produce fewer
      than N petitions
    - Errors
      - 400 if no `docket_file` was sent, or if `petitioner` is present but is
        not valid JSON
      - 422 if a file could not be parsed. `detail` names the file. The whole
        request fails; no petitions are returned for the files that did parse.

- **api/v0.2.0/petition/generator-report/**
    - Requires access token header
    - POST produces a microsoft .docx summary of a generation session
    - Expects JSON of
      - name: string, full name of the petitioner
      - dob: iso formatted date
      - actions: list of strings
      - petitionSummaries: list
    - Errors
      - 400 if any of the four fields is absent; `detail` names the missing one

- **api/v0.2.1/pa_court_archive/search**
    - Requires access token header
    -  GET request allows searching, with:
        - required fields:
            - first_name: string, first name of client to search
            - last_name: string, last name of client to search
        - returns list of Petition Fields, may be an empty list
