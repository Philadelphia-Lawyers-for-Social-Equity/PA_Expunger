import datetime
import logging
import os
import re
import traceback
from typing import List, Tuple

import jinja2
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from docxtpl import DocxTemplate, RichText
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

import docket_parser
from . import models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger("django")
logger.info(f"LogLevel is: {logger.level}")
logger.info(f"DJANGO_LOG_LEVEL: {os.environ.get('DJANGO_LOG_LEVEL')}")


class PetitionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug("PetitionAPIView post")
        profile = request.user.expungerprofile

        logger.debug(f"Profile {profile} found attorney {profile.attorney}")

        try:
            context = {
                "organization": profile.organization,
                "attorney": profile.attorney,
                "petitioner":
                    models.Petitioner.from_dict(request.data["petitioner"]),
                "petition":
                    models.Petition.from_dict(request.data["petition"]),
                "dockets": [models.DocketId.from_dict(d) for d in
                            request.data.get("dockets", [])],
                "fines":
                    models.Fines.from_dict(request.data["fines"]),
                "charges": [models.Charge.from_dict(c) for c in
                            request.data.get("charges", [])]
            }
            dispositions = set([charge.disposition for charge in context["charges"]])
            context["dispositions"] = ', '.join(dispositions)
        except KeyError as err:
            msg = f"Missing field: {err}"
            logger.warning(msg)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
        
        # Format address to allow for new lines to populate.
        context["organization"].formattedAddress = format_address_for_template(context["organization"].address)
        context["petitioner"].formattedAddress = format_address_for_template(context["petitioner"].address)
        
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


class DocketParserAPIView(APIView):
    def post(self, request: Request, *args, **kwargs):
        logger.debug("DocketParserAPIView post")

        profile = request.user.expungerprofile

        try:
            df = request.FILES.getlist("docket_file")
        except MultiValueDictKeyError:
            msg = f"No docket_file, got {request.FILES.keys()}"
            logger.warning(msg)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        grouped_dockets = {}

        content = {
            "petitioner": None,
            "petitions": []
        }

        for file in df:
            try:
                parsed = docket_parser.parse_pdf(file)
            except Exception as exception:
                tb = traceback.format_exc()
                short_msg = f"Parse error {exception}"
                logger.warning(tb)
                return Response({"error": short_msg})

            # grouping parsed files by OTN or docket/cross court docket numbers
            if parsed.get('type') == 'docket':
                otn = parsed.get("otn")
                if otn is not None:
                    if otn in grouped_dockets:
                        grouped_dockets[otn].append(parsed)
                    else:
                        grouped_dockets[otn] = [parsed]
                else:
                    docket_number = parsed.get("docket_number")
                    if docket_number in grouped_dockets:
                        grouped_dockets[docket_number].append(parsed)
                    else:
                        grouped_dockets[docket_number] = [parsed]
                
            elif parsed.get('type') == 'court summary':
                court_summary_dockets = parsed.pop('dockets', [])
                for docket in court_summary_dockets:
                    parsed_section = {**parsed, **docket}
                    otn = parsed_section.get("otn")
                    if otn is not None:
                        if otn in grouped_dockets:
                            grouped_dockets[otn].append(parsed_section)
                        else:
                            grouped_dockets[otn] = [parsed_section]
                    else:
                        docket_number = parsed_section.get("docket_number")
                        if docket_number in grouped_dockets:
                            grouped_dockets[docket_number].append(parsed_section)
                        else:
                            grouped_dockets[docket_number] = [parsed_section]

        for docket, group in grouped_dockets.items():
            most_recent_disposition = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")
            petition = {
                "docket_info": {},
                "docket_numbers": [],
                "charges": [],
                "fines": {}
            }
            for parsed in group:
                if parsed["type"] == "court summary":
                    # NOTE: handle dockets from court summaries that have county data other than: {'county': 'Philadelphia'}.  The same OTN and/or docket numbers may have been addressed by courts in multiple counties, eg. Philadelphia County and Montgomery County
                    # NOTE from 6/23/2023 meeting with PLSE attorney: "It would be nice to have those petitions drafted for out of county, but it is a low priority"
                    petition["county"] = parsed.get("county")
                        
                    petition["category"] = parsed["category"]
                    if parsed["category"] == 'Archived':
                        # NOTE from 6/23/2023 meeting with PLSE attorney: "After uploading the court summary, we could alert the user to the fact that certain dockets are archived, and then allow them to upload the archived docket sheets."
                        if parsed.get("docket_number") not in petition["docket_numbers"]:
                            petition["docket_numbers"].append(parsed.get("docket_number"))
                        continue 

                petitioner = petitioner_from_parser(parsed)
                if content["petitioner"] is None:
                    content["petitioner"] = petitioner
                else:
                    if content["petitioner"]["name"] != petitioner["name"]:
                        content["petitioner"]["aliases"].append(petitioner["name"])
                    if petitioner["aliases"] is not None:
                        for alias in petitioner["aliases"]:
                            if alias not in content["petitioner"]["aliases"]:
                                content["petitioner"]["aliases"].append(alias)

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

        logger.debug(f"Request: {request.data}")
        logger.debug(f"Parsed: {content}")
        return Response(content)


# Helpers


def petitioner_from_parser(parsed: dict) -> dict:
    """
    Produce the petitioner data based on the docket parser output.
    """
    petitioner = {"name": None,
                  "aliases": parsed.get("aliases"),
                  "dob": None}

    if parsed.get("type") == "docket":
        petitioner["name"] = parsed.get("defendant_name")
    else:
        petitioner["name"] = parsed.get("defendant_name_reversed")

    dob = parsed.get("dob")
    if dob is not None:
        petitioner["dob"] = dob.isoformat()

    return petitioner


def petition_from_parser(parsed: dict):
    """
    Produce the petition data based on the docket parser output.
    """
    petition_dict = {
        "otn": parsed.get("otn"),
        "judge": parsed.get("judge"),
        "ratio": models.PetitionRatio.full.name
    }
    if parsed.get("type") == "docket":
        petition_dict["complaint_date"] = parsed.get("complaint_date")
    else:
        petition_dict["arrest_date"] = parsed.get("arrest_date")

    return petition_dict


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

            adapted_charge = adapt_charge(charge, disposition_date, "docket")
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
            if "disposition" not in charge:
                logger.error(f"Charge must include a disposition, got: {charge}")

            adapted_charge = adapt_charge(charge, disposition_date, "court summary")
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


def adapt_charge(charge: dict, disposition_date: datetime.date, file_type: str) -> dict:
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
    
    
    disposition = None
    disposition_from_docket = charge.get("offence_disposition")
    if disposition_from_docket is not None:
        disposition = disposition_from_docket
    else:
        disposition = charge.get("disposition")


    disposition = None
    disposition_from_docket = charge.get("offence_disposition")
    if disposition_from_docket is not None:
        disposition = disposition_from_docket
    else:
        disposition = charge.get("disposition")

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
