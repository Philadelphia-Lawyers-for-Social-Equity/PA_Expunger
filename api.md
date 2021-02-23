# Glossary (resusable data structure definitions)

**Petition Fields** is a data structure (typically JSON or python dict)
containing:
    - petitioner
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
    - petition
            - otn: string
            - arrest_date: iso formatted date, such as "2019-10-17"
            - arrest_officer: string, arresting officer's full name
            - arrest_agency: string, arresting agency
            - judge: string, full name of the judge
            - ratio: string, may be "full" if every charge could be
                     expunged, or "partial" if some charges have been
                     excluded.
    - dockets: List of docket ids, such as "MC-51-CR-1234567-1995"
    
    - charges (list of):
        - statute: string
        - description: string
        - grade: string (usually 2-3 chars)
        - date: date, formatted such as “2020-10-11”
        - disposition: string
    
    - restitution:
            - total: decimal number
            - paid: decimal number

# API

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
      - dc: string
      - arrest_date: iso formatted date, such as "2019-10-17"
      - arrest_officer: string, arresting officer's full name
      - disposition: string
      - judge: string, full name of the judge
    - docket: String of a docket id, such as "MC-51-CR-1234567-1995"
    - restitution:
      - total: decimal number
      - paid: decimal number

- **api/v0.2.0/petition/parse_docket/**
    - Requires access token header
    - POST of docket file produces JSON of Petition Fields

- **api/v0.2.1/pa_court_archive/search**
    - Requires access token header
    -  GET request allows searching, with:
        - required fields:
            - first_name: string, first name of client to search
            - last_name: string, last name of client to search
        - returns list of Petition Fields, may be an empty list
