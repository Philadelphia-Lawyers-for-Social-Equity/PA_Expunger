from rest_framework import serializers


class CaseToPetitionFieldsSerializer(serializers.Serializer):
    """Produce the PaRecord as petition_fields."""
    petitioner = serializers.SerializerMethodField()
    petition = serializers.SerializerMethodField()
    dockets = serializers.SerializerMethodField()
    charges = serializers.SerializerMethodField()

    def get_petitioner(self, obj):
        arrestee = obj.arrestees.first()

        if arrestee.birth_date is None:
            dob = None
        else:
            dob = arrestee.birth_date.isoformat()

        return {
            "name": merge_name(
                arrestee.first_name, arrestee.last_name,
                arrestee.middle_name),
            "aliases": None,
            "dob": dob
        }

    def get_petition(self, obj):
        return {
            "otn": obj.otn,
            "arrest_date": None,
            "arrest_officer": None,
            "arrest_agency": None,
            "judge": obj.disposing_judge,
            "ratio": None
        }

    def get_dockets(self, obj):
        return [x.docket_number for x in obj.docket_set.all()]

    def get_charges(self, obj):
        dockets = obj.docket_set.all()
        charges = []

        for docket in dockets:
            for offense in docket.offense_set.all():

                if offense.date is None:
                    date = None
                else:
                    date = offense.date.isoformat()

                charges.append({
                    "statute":  merge_statute(
                        offense.inchoate_statute_title,
                        offense.inchoate_statute_section,
                        offense.inchoate_statute_subsection),
                    "description": offense.description,
                    "grade": offense.grade,
                    "date": date,
                    "disposition": offense.disposition
                })

        return charges


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
