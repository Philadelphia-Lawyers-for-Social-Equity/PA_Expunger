import logging
import os
import jinja2
from docxtpl import DocxTemplate

from django.http import HttpResponse

from django.utils.datastructures import MultiValueDictKeyError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import docket_parser

from . import models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger("django")
logger.info("LogLevel is: %s" % logger.level)
logger.info("DJANGO_LOG_LEVEL: %s" % os.environ.get("DJANGO_LOG_LEVEL"))


class PetitionAPIView(APIView):

    def post(self, request, *args, **kwargs):
        logger.debug("PetitionAPIView post")
        profile = request.user.expungerprofile

        logger.debug(
            "Profile %s found attorney %s" % (profile, profile.attorney))

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
                "restitution":
                    models.Restitution.from_dict(request.data["restitution"]),
                "charges": [models.Charge.from_dict(c) for c in
                            request.data.get("charges", [])]
            }
        except KeyError as err:
            msg = "Missing field: %s" % str(err)
            logger.warn(msg)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug("Petition POSTed with context: %s" % context)

        docx = os.path.join(
            BASE_DIR, "petition", "templates", "petition", "petition.docx")
        document = DocxTemplate(docx)

        jinja_env = jinja2.Environment()
        jinja_env.filters["comma_join"] = lambda v: ", ".join(v)
        jinja_env.filters["date"] = date_string

        document.render(context, jinja_env)
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response['Content-Disposition'] = 'attachment; filename="petition.docx"'
        document.save(response)

        return response


class DocketParserAPIView(APIView):

    def post(self, request, *args, **kwargs):
        logger.debug("DocketParserAPIView post")

        profile = request.user.expungerprofile

        try:
            df = request.FILES["docket_file"]
        except MultiValueDictKeyError:
            msg = "No docket_file, got %s" % request.FILES.keys()
            logger.warn(msg)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed = docket_parser.parse_pdf(df)
        except Exception as err:
            msg = "Parse error %s" % str(err)
            logger.warn(msg)
            return Response({"error": msg})

        content = {
            "petitioner": petitioner_from_parser(parsed),
            "petition": petition_from_parser(parsed),
            "dockets": dockets_from_parser(parsed),
            "charges": charges_from_parser(parsed),
            "restitution": restitution_from_parser(parsed)
        }

        logger.info("Parsed: %s", content)
        return Response(content)


# Helpers

def petitioner_from_parser(parsed):
    """
    Produce the petioner data based on the docket parser output.
    """
    petitioner = {}

    if "section_docket" in parsed:
        petitioner["name"] = parsed["section_docket"].get("defendant", None)

    if "section_defendant_information" in parsed:
        petitioner["aliases"] = parsed["section_defendant_information"].get(
            "aliases", [])

        dob = parsed["section_defendant_information"].get("dob", None)

        if dob is not None:
            petitioner["dob"] = dob.isoformat()

    return petitioner


def petition_from_parser(parsed):
    """
    Produce the petition data based on the docket parser output.
    """
    if "section_case_information" not in parsed:
        return {}

    case_info = parsed["section_case_information"]
    officer = case_info.get("arrest_officer", None)

    if officer is None or officer == "Affiant":
        officer = case_info.get("arrest_agency")

    if "section_status_information" in parsed:
        arrest_date = parsed["section_status_information"].get(
            "arrest_date", None)
    else:
        arrest_date = None

    return {
        "otn": case_info.get("otn"),
        "arrest_officer": officer,
        "arrest_agency": case_info.get("arrest_agency"),
        "judge": case_info.get("judge"),
        "arrest_date": arrest_date
        }


def dockets_from_parser(parsed):
    """
    Produce the docket numbers based on the docket parser output.
    """
    dockets = []

    if "section_docket" in parsed:
        primary = parsed["section_docket"].get("docket", None)

        if primary is not None:
            dockets.append(primary)

    if "section_case_information" in parsed:
        originating = \
            parsed["section_case_information"].get("originating_docket", None)

        if originating is not None:
            dockets.append(originating)

    return dockets


def charges_from_parser(parsed):
    """
    Produces the charges based on the docket parser output.
    """
    charges = []

    if "section_disposition" in parsed:

        for disp in parsed["section_disposition"]:
            if include_charge(disp):
                charges.append(disposition_to_charge(disp))

    return charges


def restitution_from_parser(parsed):
    """Produce restitution data based on the docket parser output."""

    if "section_financial_information" not in parsed:
        return {}

    data = parsed["section_financial_information"]
    total = data.get("assessment", 0)
    paid = abs(data.get("payments", 0)) + abs(data.get("adjustments", 0))

    return {
        "total": total,
        "paid": paid
    }


def include_charge(disp):
    """
    Produce true if a charge qualifies for expungement.
    """
    if "offense_disposition" not in disp:
        raise ValueError("Charge must include a disposition, got: %s" % disp)

    return disp["offense_disposition"] in [
        "Nolle Prossed", "ARD - County", "Not Guilty", "Dismissed",
        "Withdrawn"]


def date_string(d):
    try:
        return "%02d-%02d-%04d" % (d.month, d.day, d.year)
    except AttributeError:
        logger.warn("Invalid date object: %s" % (str(d)))
        return ""


def disposition_to_charge(disp):
    """
    Convert a parsed dispositions to a dict of a charge.

    Arg:
        A single disposition dict, as delivered by the parser
    Return:
        A charge dict, per the api doc
    """
    charge_date = disp.get("date", None)

    if charge_date is not None:
        charge_date = charge_date.isoformat()

    return {
        "statute": disp.get("statute", None),
        "description": disp.get("charge_description", None),
        "grade": disp.get("grade", None),
        "date": charge_date,
        "disposition": disp.get("offense_disposition", None)
    }
