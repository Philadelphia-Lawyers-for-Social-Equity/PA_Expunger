import datetime
import logging
import os
import traceback
from typing import List, Tuple

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

        logger.debug("Profile %s found attorney %s" % (profile, profile.attorney))

        try:
            context = {
                "organization": profile.organization,
                "attorney": profile.attorney,
                "petitioner": models.Petitioner.from_dict(request.data["petitioner"]),
                "petition": models.Petition.from_dict(request.data["petition"]),
                "dockets": [
                    models.DocketId.from_dict(d)
                    for d in request.data.get("dockets", [])
                ],
                "restitution": models.Restitution.from_dict(
                    request.data["restitution"]
                ),
                "charges": [
                    models.Charge.from_dict(c) for c in request.data.get("charges", [])
                ],
            }
        except KeyError as err:
            msg = "Missing field: %s" % (err)
            logger.warn(msg)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug("Petition POSTed with context: %s" % context)

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
        except Exception as exception:
            tb = traceback.format_exc()
            short_msg = f"Parse error {exception}"
            logger.warning(tb)
            return Response({"error": short_msg})

        ratio, charges = charges_from_parser(parsed)
        content = {
            "petitioner": petitioner_from_parser(parsed),
            "petition": petition_from_parser(parsed, ratio),
            "dockets": dockets_from_parser(parsed),
            "charges": charges,
            "restitution": restitution_from_parser(parsed),
        }

        logger.debug("Parsed: %s", content)
        return Response(content)


# Helpers


def petitioner_from_parser(parsed: dict) -> dict:
    """
    Produce the petitioner data based on the docket parser output.
    """
    petitioner = {"name": parsed.get("defendant_name"),
                  "aliases": parsed.get("aliases"),
                  "dob": None}

    dob = parsed.get("dob")
    if dob is not None:
        petitioner["dob"] = dob.isoformat()

    return petitioner


def petition_from_parser(parsed: dict, ratio: models.PetitionRatio):
    """
    Produce the petition data based on the docket parser output.
    """
    return {
        "otn": parsed.get("otn"),
        "complaint_date": parsed.get("complaint_date"),
        "judge": parsed.get("judge"),
        "ratio": ratio.name,
    }


def dockets_from_parser(parsed: dict) -> List[str]:
    """
    Produce the docket numbers based on the docket parser output.
    """
    dockets = []
    primary = parsed.get("docket_number")
    if primary is not None:
        dockets.append(primary)

    originating = parsed.get("originating_docket_number")
    if originating is not None:
        dockets.append(originating)

    cross_court = parsed.get("cross_court_docket_numbers")
    if cross_court is not None:
        cross_court = cross_court.split(',')
        for cross_court_number in cross_court:
            dockets.append(cross_court_number.strip())

    return dockets


def charges_from_parser(parsed: dict) -> Tuple[models.PetitionRatio, List[dict]]:
    """
    Produces the ratio, charges based on the docket parser output.
    """
    expungeable_dispositions = [
        "Nolle Prossed",
        "ARD - County",
        "Not Guilty",
        "Dismissed",
        "Withdrawn",
    ]

    def is_expungeable(offense_disposition) -> bool:
        for expungeable_disposition in expungeable_dispositions:
            if expungeable_disposition.lower() in offense_disposition.lower():
                return True
        return False

    expungeable_charges = []
    case_events = parsed.get("section_disposition", {})
    ratio = models.PetitionRatio.full
    if not any(case_event.get("disposition_finality") == "Final Disposition" for case_event in case_events):
        logger.error("No final disposition found.")
        # raise ValueError("No final disposition found.")

    for case_event in case_events:
        if case_event.get("disposition_finality") != "Final Disposition":
            continue

        if "charges" not in case_event:
            logger.error(f"No charges found for {case_event.get('case_event')} (Final Disposition)")
            # raise ValueError(f"No charges found for {case_event.get('case_event')} (Final Disposition)")

        disposition_date = case_event.get("disposition_date")
        for charge in case_event["charges"]:
            if "offense_disposition" not in charge:
                logger.error(f"Charge must include a disposition, got: {charge}")
                # raise ValueError(f"Charge must include a disposition, got: {charge}")

            if is_expungeable(charge["offense_disposition"]):
                adapted_charge = adapt_charge(charge, disposition_date)
                expungeable_charges.append(adapted_charge)
            else:
                ratio = models.PetitionRatio.partial

    return ratio, expungeable_charges


def restitution_from_parser(parsed: dict) -> dict:
    """Produce restitution data based on the docket parser output."""
    assessment = parsed.get("assessment")
    payments = parsed.get("payments")
    adjustments = parsed.get("adjustments")
    paid = None
    if payments is not None and adjustments is not None:
        paid = -payments - adjustments
    return {"total": assessment, "paid": paid}


def date_string(d):
    try:
        return "%02d-%02d-%04d" % (d.month, d.day, d.year)
    except AttributeError:
        logger.warn("Invalid date object: %s" % (str(d)))
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
        "statute": charge.get("statute"),
        "description": charge.get("charge_description"),
        "grade": charge.get("grade"),
        "date": disposition_date,
        "disposition": charge.get("offense_disposition"),
    }
