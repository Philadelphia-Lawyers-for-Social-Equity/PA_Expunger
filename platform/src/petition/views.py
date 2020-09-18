import logging
import os
import jinja2
from docxtpl import DocxTemplate

from django.http import HttpResponse

from django.utils.datastructures import MultiValueDictKeyError

from rest_framework.views import APIView
from rest_framework.response import Response

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
                "docket":
                    models.DocketId.from_dict(request.data["docket"]),
                "restitution":
                    models.Restitution.from_dict(request.data["restitution"]),
                "charges": [models.Charge.from_dict(c) for c in
                            request.data.get("charges", [])]
            }
        except KeyError as err:
            msg = "Missing field: %s" % str(err)
            logger.warn(msg)
            return Response({"error": msg})

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
            return Response({"error": msg})

        try:
            parsed = docket_parser.parse_pdf(df)
        except Exception as err:
            msg = "Parse error %s" % str(err)
            logger.warn(msg)
            return Response({"error": msg})

        content = {
            "petitioner": {},
            "petition": {},
            "docket": None,
            "charges": []
        }

        if "section_docket" in parsed:
            content["docket"] = parsed["section_docket"].get("docket", None)
            content["petitioner"]["name"] = parsed["section_docket"].get("defendant", None)

        if "section_defendant_information" in parsed:
            content["petitioner"]["aliases"] = \
                parsed["section_defendant_information"].get("aliases")

            dob = parsed["section_defendant_information"].get("dob", None)

            if dob is not None:
                content["petitioner"]["dob"] = dob.isoformat()

        if "section_case_information" in parsed:
            content["petition"] = case_information_to_petition(
                parsed["section_case_information"])

        if "section_status_information" in parsed:
            arrest_date = parsed["section_status_information"].get(
                "arrest_date", None)

            if arrest_date is not None:
                arrest_date = arrest_date.isoformat()
                content["petition"]["arrest_date"] = arrest_date

        if "section_disposition" in parsed:
            for disp in parsed["section_disposition"]:
                if include_charge(disp):
                    content["charges"].append(disposition_to_charge(disp))

        if "section_financial_information" in parsed:
            content["restitution"] = {
                "total": parsed["section_financial_information"]["total"],
                "paid":
                    abs(parsed["section_financial_information"]["payments"])
            }

        logger.info("Parsed: %s", content)
        return Response(content)


# Helpers

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


def case_information_to_petition(case_info):
    """Convert the case information to the petition portion of the api."""

    return {
        "otn": case_info.get("otn"),
        "arrest_officer": case_info.get("arrest_officer"),
        "arrest_agency": case_info.get("arrest_agency"),
        "judge": case_info.get("judge")
        }


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
