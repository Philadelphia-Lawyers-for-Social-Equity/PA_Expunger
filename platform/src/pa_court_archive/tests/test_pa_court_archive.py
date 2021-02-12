# -*- coding: utf-8 -*-
from django.test import TestCase
from django.urls import reverse

from pa_court_archive import factories
from pa_court_archive import serializers

from expunger.tests.test_rest import Authenticated


class TestPaCourtArchive(TestCase):
    """Ensure the PA Court Archive works."""

    def test_merge_name(self):
        """We should combine names with or without a middle name."""

        assert serializers.merge_name("James", "Jones", "Earl") == \
            "James Earl Jones"

        assert serializers.merge_name("James", "Jones", None) == \
            "James Jones"

        assert serializers.merge_name("James", "Jones") == \
            "James Jones"

    def test_merge_statute(self):
        """We can construct a statute from components."""
        assert serializers.merge_statute(None, None, None) is None
        assert serializers.merge_statute("0", "0", "0") is None
        assert serializers.merge_statute(0, 0, 0) is None
        assert serializers.merge_statute(None, "902", "A") is None

        assert serializers.merge_statute("18", None, None) == "18"
        assert serializers.merge_statute("18", None, "A") == "18"
        assert serializers.merge_statute("18", "0", "0") == "18"
        assert serializers.merge_statute("18", 0, 0) == "18"

        assert serializers.merge_statute("18", "902", None) == "18 § 902"
        assert serializers.merge_statute("18", "902", "0") == "18 § 902"
        assert serializers.merge_statute("18", "902", 0) == "18 § 902"

        assert serializers.merge_statute("18", "902", "A") == "18 § 902 §§ A"

    def test_factory_generation(self):
        """Make sure each factory can be constructed."""
        factories.ArresteeFactory()
        factories.CaseFactory()
        factories.DocketFactory()
        factories.OffenseFactory()

    def test_make_petition_fields(self):
        """Test convesion of PaRecord to petitition_fields."""
        case = factories.CaseFactory()
        serializer = serializers.CaseToPetitionFieldsSerializer(case)

        arrestee = case.arrestees.first()
        self.assertEqual(
            serializer.data["petitioner"],
            {"name": serializers.merge_name(
                arrestee.first_name, arrestee.last_name,
                arrestee.middle_name),
             "aliases": None,
             "dob": arrestee.birth_date.isoformat()})

        self.assertEqual(
            serializer.data["petition"],
            {"otn": case.otn,
             "arrest_date": None,
             "arrest_officer": None,
             "arrest_agency": None,
             "judge": case.disposing_judge,
             "ratio": None})

        dockets = case.docket_set.all()
        self.assertEqual(
            serializer.data["dockets"],
            [x.docket_number for x in dockets])

        charges = []

        for docket in dockets:
            for offense in docket.offense_set.all():
                charges.append({
                    "statute": serializers.merge_statute(
                        offense.inchoate_statute_title,
                        offense.inchoate_statute_section,
                        offense.inchoate_statute_subsection),
                    "description": offense.description,
                    "grade": offense.grade,
                    "date": offense.date.isoformat(),
                    "disposition": offense.disposition
                })

        self.assertEqual(serializer.data["charges"], charges)

    def test_serialize_with_empty_values(self):
        """
        Make sure the serializer survives if all nullable values are empty.
        """
        case = factories.CaseFactory()
        arrestee = case.arrestees.first()

        arrestee.first_name = None
        arrestee.middle_name = None
        arrestee.gender_code = None
        arrestee.race_code = None
        arrestee.birth_date = None

        case.filed_date = None
        case.city = None
        case.county = None
        case.state = None
        case.zip = None
        case.disposition = None
        case.disposition_date = None
        case.disposing_judge = None

        docket = case.docket_set.filter(offense__isnull=False).first()
        offense = docket.offense_set.first()

        offense.disposition = None
        offense.date = None
        offense.disposition_date = None
        offense.originating_sequence = None
        offense.statute_type = None
        offense.statute_title = None
        offense.statute_section = None
        offense.statute_subsection = None
        offense.inchoate_statute_title = None
        offense.inchoate_statute_section = None
        offense.inchoate_statute_subsection = None
        offense.grade = None

        case.save()
        serializer = serializers.CaseToPetitionFieldsSerializer(case)
        serializer.to_representation(case)


class TestApi(Authenticated, TestCase):
    """Make sure the REST interface works."""

    def test_api_is_available(self):
        """Make sure the api is running."""

        data = {"first_name": "Harry", "last_name": "Potter"}
        url = reverse("pa_court_archive:search")
        res = self.authenticated_client.get(url, data, content_type="application/json")
        self.assertEqual(res.status_code, 200, msg="bad response: %s" % res.content)
