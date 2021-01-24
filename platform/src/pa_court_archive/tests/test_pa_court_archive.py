# -*- coding: utf-8 -*-

from copy import copy

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

    def test_make_petition_fields(self):
        """Test convesion of PaRecord to petitition_fields."""
        parecord = factories.PaRecordFactory()
        uglified = copy(parecord)

        uglified.dob = parecord.birthdate + " 00:00:00.000"
        uglified.zip = parecord.zipcode + ".0"
        uglified.filed_date = parecord.filed_date + " 16:15:00.000"
        uglified.offense_date = parecord.offense_date + " 00:00:00.000"
        uglified.case_disposition_date = parecord.case_disposition_date + \
            " 00:00:00.000"

        serializer = serializers.PaRecordToPetitionFieldsSerializer(uglified)

        self.assertEqual(
            serializer.data["petitioner"],
            {"name": serializers.merge_name(
                parecord.first_name, parecord.last_name,
                parecord.middle_name),
             "aliases": None,
             "dob": parecord.birthdate})

        self.assertEqual(
            serializer.data["petition"],
            {"otn": parecord.offense_tracking_number,
             "arrest_date": None,
             "arrest_officer": None,
             "arrest_agency": None,
             "judge": parecord.disposing_judge,
             "ratio": None})

        self.assertEqual(
            serializer.data["dockets"],
            [parecord.docket_number])

        self.assertEqual(
            serializer.data["charges"],
            [{"statute": serializers.merge_statute(
                parecord.inchoate_statute_title,
                parecord.inchoate_statute_section,
                parecord.inchoate_statute_subsection),
              "description": parecord.offense_description,
              "grade": parecord.offense_grade,
              "date": parecord.offense_date,
              "disposition": parecord.offense_disposition}])


class TestApi(Authenticated, TestCase):
    """Make sure the REST interface works."""

    def test_api_is_available(self):
        """Make sure the api is running."""

        data = {"first_name": "Harry", "last_name": "Potter"}
        url = reverse("pa_court_archive:search")
        res = self.authenticated_client.get(url, data, content_type="application/json")
        self.assertEqual(res.status_code, 200, msg="bad response: %s" %
                         res.content)
