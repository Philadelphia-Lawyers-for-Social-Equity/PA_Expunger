import datetime
import logging
import json
import os
import re
from typing import List, Tuple

import jinja2
from django.http import HttpResponse
from docxtpl import DocxTemplate, RichText
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

import docket_parser
from . import models
from .errors import MalformedRequest, MissingField, ParseFailed
from expunger.models import Organization, Attorney

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger("django")
logger.info(f"LogLevel is: {logger.level}")
logger.info(f"DJANGO_LOG_LEVEL: {os.environ.get('DJANGO_LOG_LEVEL')}")


class PetitionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug("PetitionAPIView post")

        try:
            context = {
                "organization": Organization.from_dict(request.data["organization"]),
                "attorney": Attorney.from_dict(request.data["attorney"]),
                "petitioner":
                    models.Petitioner.from_dict(request.data["petitioner"]),
                "petition":
                    models.Petition.from_dict(request.data["petition"]),
                "dockets": request.data.get("dockets", []),
                "fines":
                    models.Fines.from_dict(request.data["fines"]),
                "charges": [models.Charge.from_dict(c) for c in
                            request.data.get("charges", [])]
            }
            dispositions = set([charge.disposition for charge in context["charges"] if charge.disposition is not None])
            context["dispositions"] = ', '.join(dispositions)
        except KeyError as err:
            # `err.args[0]` is the missing key, not the exception text -- a name
            # from our own payload contract, so it is safe to show. str(err)
            # would wrap it in quotes.
            logger.warning("Missing field %s in petition payload", err.args[0])
            raise MissingField(f"Missing required field: {err.args[0]}.")

        # Format address to allow for new lines to populate.
        context["organization"].formattedAddress = format_address_for_template(context["organization"].address)
        context["petitioner"].formattedAddress = format_address_for_template(context["petitioner"].address)
        
        # Any charges with no disposition are given disposition of 'unk'
        for charge in context["charges"]:
            if charge.grade == None:
                charge.grade = 'unk'

        logger.debug(f"Petition POSTed with context: {context}")

        docx = os.path.join(
            BASE_DIR, "petition", "templates", "petition", "petition.docx"
        )
        document = DocxTemplate(docx)

        jinja_env = jinja2.Environment()
        jinja_env.filters["comma_join"] = lambda v: ", ".join(v)
        jinja_env.filters["date"] = date_string

        document.render(context, jinja_env)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = 'attachment; filename="petition.docx"'
        document.save(response)

        return response


class GeneratorReportAPIView(APIView):
    def post(self, request: Request, *args, **kwargs):
        logger.debug("GeneratorReportAPIView post")

        try:
            context = {
                "name": request.data["name"],
                "dob": request.data["dob"],
                "actions": request.data["actions"],
                "petition_summaries": request.data["petitionSummaries"]
            }
        except KeyError as err:
            # Report the key the client sent, not our template's name for it:
            # "petitionSummaries" is what a caller can look for in their own
            # payload, whereas the context key is "petition_summaries".
            logger.warning("Missing field %s in generator report payload", err.args[0])
            raise MissingField(f"Missing required field: {err.args[0]}.")

        logger.debug(f"Summary POSTed with context: {context}")

        docx = os.path.join(
            BASE_DIR, "petition", "templates", "petition", "generator-report.docx"
        )
        document = DocxTemplate(docx)

        jinja_env = jinja2.Environment()

        document.render(context, jinja_env)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = 'attachment; filename="generator-report.docx"'
        document.save(response)

        return response


class DocketParserAPIView(APIView):
    def post(self, request: Request, *args, **kwargs):
        logger.debug("DocketParserAPIView post")

        df = request.FILES.getlist("docket_file")
        if not df:
            # The key names go to the log, not the response -- dict_keys([...])
            # in a browser is a Python repr, and the user can't act on it.
            logger.warning("No docket_file in upload; got %s", list(request.FILES.keys()))
            raise MissingField("No files were uploaded.")

        petitioner_json = request.POST.get("petitioner")
        petitioner = {}
        if petitioner_json:
            try:
                petitionerFromRequest = json.loads(petitioner_json)
                if isinstance(petitionerFromRequest, dict):
                    # Drop keys with falsy values
                    petitioner = {key: value for key, value in petitionerFromRequest.items() if value}
            except json.JSONDecodeError:
                # Don't log the blob itself -- it is the petitioner's name, DOB
                # and address. Position and length are enough to debug from.
                logger.warning(
                    "Could not decode petitioner JSON (%d bytes)", len(petitioner_json)
                )
                raise MalformedRequest(
                    "The petitioner information sent with the upload wasn't valid."
                )

        # store parsed files without OTNs here and sort them into grouped_dockets last
        parsed_no_otn = []

        # reference dictionary for associating dockets to OTNs
        docket_to_otn = {}

        content = {
            "petitioner": petitioner,
            "petitions": [],
        }
        parsed_files = []
        for file in df:
            try:
                parsed_files.append(docket_parser.parse_pdf(file))
            except Exception:
                # The exception never reaches the browser. A parsimonious
                # ParseError stringifies to a snippet of the document being
                # parsed -- for a real client, their name, date of birth and
                # charges. Full traceback to the log; a message we wrote to the
                # user. `file.name` is safe to interpolate: they chose it.
                #
                # One message for every cause, deliberately. There are three
                # distinguishable failures here -- unopenable PDF, readable PDF
                # that isn't a court document, and a real docket whose format
                # the grammar can't handle -- and only the last is our bug
                # rather than a bad upload. Telling them apart means either
                # importing pypdf and parsimonious into this view or having
                # docket_parser raise its own types; see the TODO in errors.py.
                # Until then the wording stays vague about *why*, because a
                # single catch cannot honestly claim to know.
                #
                # Raising aborts the whole upload, so one bad file loses the
                # good ones. That matches today's behavior and is not a
                # decision -- returning the petitions we could build plus a
                # warning naming the file is the friendlier option, and it is
                # waiting on warnings[] (issue #19, group 3).
                logger.exception("Parse failed for %s", file.name)
                raise ParseFailed(
                    f"We couldn't read “{file.name}”. "
                    "Make sure it's a PA docket sheet or court summary PDF."
                )

        grouped_dockets = {}

        # Move the court summary(ies) to the start of the list so OTNs will be in order of appearance in court summary
        parsed_files.sort(key=lambda d: d.get('type') != 'court summary')

        for parsed in parsed_files:
            # grouping parsed files by OTN or docket/cross court docket numbers
            if parsed.get('type') == 'docket':
                if parsed.get("otn"):
                    update_group_dockets(grouped_dockets, docket_to_otn, parsed)
                else:
                    # Defer grouping dockets without OTNs
                    parsed_no_otn.append(parsed)
                
            elif parsed.get('type') == 'court summary':
                court_summary_dockets = parsed.pop('dockets', [])
                for docket in court_summary_dockets:
                    parsed_section = {**parsed, **docket}
                    if parsed_section.get("otn"):
                        update_group_dockets(grouped_dockets, docket_to_otn, parsed_section)
                    else:
                        # Defer grouping dockets without OTNs
                        parsed_no_otn.append(parsed_section)

        # match OTN-less dockets with OTNs in grouped_dockets
        while parsed_no_otn:
            parsed = parsed_no_otn.pop()
            docket_number = parsed.get("docket_number")
            if not (key := docket_to_otn.get(docket_number)):
                key = docket_number
            grouped_dockets.setdefault(key, []).append(parsed)

        # add each docket's petitioner and petition info to content
        for docket, group in grouped_dockets.items():
            most_recent_disposition = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")
            petition = {
                "docket_info": {},
                "docket_numbers": [],
                "charges": [],
                "fines": {},
                "category": "",
            }
            for parsed in group:
                petitioner = petitioner_from_parser(parsed)
                content["petitioner"] = petitioner | content["petitioner"]
                if content["petitioner"]["name"] != petitioner["name"]:
                    content["petitioner"].setdefault("aliases", []).append(petitioner["name"])
                if petitioner["aliases"] is not None:
                    for alias in petitioner["aliases"]:
                        if alias not in content["petitioner"]["aliases"]:
                            content["petitioner"]["aliases"].append(alias)
                
                if parsed["type"] == "court summary":
                    # TODO: handle dockets from court summaries that have county data other than: {'county': 'Philadelphia'}.
                    # The same OTN and/or docket numbers might have been addressed by courts in multiple counties, 
                    # eg. Philadelphia County and Montgomery County

                    # "county" key used to alert user when a court summary record is from a county other than Philadelphia County
                    petition["county"] = parsed.get("county")
                    
                    if parsed["category"] == 'Archived':
                        # "category" key used to alert user when petition info is only taken from a court summary
                        # or an archived docket from a court summary
                        if not petition["category"]:
                            petition["category"] = parsed["category"]

                        if parsed.get("docket_number") not in petition["docket_numbers"]:
                            petition["docket_numbers"].append(parsed.get("docket_number"))

                    elif not petition["category"]:
                        petition["category"] = parsed["category"]
                else:
                    petition["category"] = "Docket"

                parsed_docket_numbers = docket_numbers_from_parser(parsed)
                for parsed_docket_number in parsed_docket_numbers:
                    if parsed_docket_number not in petition["docket_numbers"]:
                        petition["docket_numbers"].append(parsed_docket_number)

                parsed_charges = []
                if parsed["type"] == "docket":
                    parsed_charges = charges_from_docket(parsed)
                else:
                    parsed_charges = charges_from_court_summary(parsed)

                petition["charges"] += parsed_charges

                # Prioritizing docket_info and fines based on the most recent disposition date
                disposition_date = [datetime.datetime.strptime(charge["date"], "%Y-%m-%d") for charge in parsed_charges if charge["date"]]
                disposition_date.sort(reverse=True)

                if disposition_date:
                    if disposition_date[0] > most_recent_disposition:
                        most_recent_disposition = disposition_date[0]
                        petition["docket_info"] = petition_from_parser(parsed)
                        if parsed["type"] == "docket":
                            petition["fines"] = models.Fines.from_dict(fines_from_parser(parsed)).to_dict()
                if not petition["docket_info"]:
                    petition["docket_info"] = petition_from_parser(parsed)
                if not petition["fines"] and parsed["type"] == "docket":
                    petition["fines"] = models.Fines.from_dict(fines_from_parser(parsed)).to_dict()

            content["petitions"].append(petition)
            # remove duplicates while preserving order
            content["petitioner"]["aliases"] = list(dict.fromkeys(content["petitioner"]["aliases"]))

        logger.debug(f"Request: {request.data}")
        logger.debug(f"Parsed: {content}")
        return Response(content)


# Helpers

def update_group_dockets(grouped_dockets: dict, docket_to_otn: dict, parsed_docket: dict) -> None:
    if key := parsed_docket.get("otn"):
        for docket_number in docket_numbers_from_parser(parsed_docket):
            docket_to_otn[docket_number] = key
    else:
        key = parsed_docket.get("docket_number")
    grouped_dockets.setdefault(key, []).append(parsed_docket)


def petitioner_from_parser(parsed: dict) -> dict:
    """
    Produce the petitioner data based on the docket parser output.
    """
    petitioner = {"name": parsed.get("defendant_name"),
                  "aliases": parsed.get("aliases", []),
                  "dob": None}

    dob = parsed.get("dob")
    if dob is not None:
        petitioner["dob"] = dob.isoformat()

    return petitioner


def petition_from_parser(parsed: dict):
    """
    Produce the petition data based on the docket parser output.
    """
    return {
        "otn": parsed.get("otn"),
        "complaint_date": parsed.get("complaint_date"),
        "arrest_date": parsed.get("arrest_date"),
        "judge": parsed.get("judge"),
        "ratio": models.PetitionRatio.full.name
    }


def docket_numbers_from_parser(parsed: dict) -> List[str]:
    """
    Produce the docket numbers based on the docket parser output.
    """
    # If we care about which docket number is originating/cross court/primary, should return a dictionary instead.
    docket_numbers = []
    primary = parsed.get("docket_number")
    if primary is not None:
        docket_numbers.append(primary)

    originating = parsed.get("originating_docket_number")
    if originating is not None:
        docket_numbers.append(originating)

    cross_court = parsed.get("cross_court_docket_numbers")
    if cross_court is not None:
        # This processing could be moved to parser
        cross_court = cross_court.split(',')
        for cross_court_number in cross_court:
            docket_numbers.append(cross_court_number.strip())

    def docket_number_filter(docket_number):
        return docket_number[:3] in ("MC-", "CP-")

    docket_numbers = list(filter(docket_number_filter, docket_numbers))
    # remove duplicates while preserving order
    docket_numbers = list(dict.fromkeys(docket_numbers))

    return docket_numbers


def charges_from_docket(parsed: dict) -> List[dict]:
    """
    Produces the charges based on the docket parser output.
    """

    charges = []
    case_events = parsed.get("section_disposition", {})
    if not any(case_event.get("disposition_finality") == "Final Disposition" for case_event in case_events):
        logger.error("No final disposition found.")

    for case_event in case_events:
        if case_event.get("disposition_finality") != "Final Disposition":
            continue

        if "charges" not in case_event:
            logger.error(f"No charges found for {case_event.get('case_event')} (Final Disposition)")

        disposition_date = case_event.get("disposition_date")
        for charge in case_event["charges"]:
            if "offense_disposition" not in charge:
                logger.error(f"Charge must include a disposition, got: {charge}")

            adapted_charge = adapt_charge(charge, disposition_date)
            charges.append(adapted_charge)

    return charges


def charges_from_court_summary(parsed: dict) -> List[dict]:
    """
    Produces the charges based on the court summary parser output.
    """
    charges = []
    disposition_date = parsed.get("disposition_date")
    if parsed.get("charges"):
        for charge in parsed["charges"]:
            adapted_charge = adapt_charge(charge, disposition_date)
            charges.append(adapted_charge)
    return charges


def fines_from_parser(parsed):
    """Produce fines data based on the docket parser output."""

    money_sections = ["assessment", "total", "non_monetary", "adjustments", "payments"]

    for section in money_sections:
        if parsed.get(section, None) is None:
            return {}
        else:
            continue

    total = parsed.get("assessment", 0)
    paid = abs(parsed.get("payments", 0)) + abs(parsed.get("adjustments", 0))

    return {"total": total, "paid": paid}


def date_string(d):
    try:
        return f"{d.month:02d}-{d.day:02d}-{d.year:04d}"
    except AttributeError:
        logger.warning(f"Invalid date object: {str(d)}")
        return ""


def adapt_charge(charge: dict, disposition_date: datetime.date) -> dict:
    """
    Convert a parsed charge to what api expects
    Args:
        charge:
            A single charge dict, as delivered by the parser
        disposition_date:
            Date of dispositional event, as delivered by the parser
    Return:
        A charge dict, per the api doc
    """
    if disposition_date is not None:
        disposition_date = disposition_date.isoformat()

    return {
        "description": charge.get("charge_description"),
        "statute": charge.get("statute"),
        "date": disposition_date,
        "grade": charge.get("grade"),
        "disposition": charge.get("offense_disposition") or charge.get("disposition"),
    }

# Template library will not recoganize \n unless it is in rtf format.
# This function will parse it as RTF, instead of doing it in the __str__ function of the Address class.
#  This keeps our __str__ function clean of template specific logic.
def format_address_for_template(address: models.Address) -> RichText:

    if address is None:
        return RichText('')
    s = re.sub(r'[\n\r]+', '\n', str(address))
    formattedAddress = RichText(str(s))
    return formattedAddress
