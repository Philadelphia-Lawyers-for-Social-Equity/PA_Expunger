from rest_framework import serializers

from . import models


class PaRecordToPetitionFieldsSerializer(serializers.Serializer):
    """Produce the PaRecord as petition_fields."""

    petitioner = serializers.SerializerMethodField()
    petition = serializers.SerializerMethodField()
    dockets = serializers.SerializerMethodField()
    charges = serializers.SerializerMethodField()

    def get_petitioner(self, obj):
        return {
            "name": merge_name(obj.first_name, obj.last_name, obj.middle_name),
            "aliases": None,
            "dob": obj.birthdate}

    def get_petition(self, obj):
        return {
            "otn": obj.offense_tracking_number,
            "arrest_date": None,
            "arrest_officer": None,
            "arrest_agency": None,
            "judge": obj.disposing_judge,
            "ratio": None}

    def get_dockets(self, obj):
        return [obj.docket_number]

    def get_charges(self, obj):
        return [{"statute": merge_statute(
                    obj.inchoate_statute_title,
                    obj.inchoate_statute_section,
                    obj.inchoate_statute_subsection),
                 "description": obj.offense_description,
                 "grade": obj.offense_grade,
                 "date": obj.offense_date,
                 "disposition": obj.offense_disposition}]


# Helpers

def merge_name(first, last, middle=None):
    """Produce a viable name string, excluding None values."""
    return " ".join([x for x in [first, middle, last] if x is not None])


def merge_statute(title, section, subsection):
    """Produce the statute."""

    if title is None or title == "0" or title == 0:
        return

    if section is None or section == "0" or section == 0:
        return str(title).strip()

    if subsection is None or subsection == "0" or subsection == 0:
        return "%s § %s" % (str(title).strip(), str(section).strip())

    return "%s § %s §§ %s" % (
        str(title).strip(), str(section).strip(), str(subsection).strip())
