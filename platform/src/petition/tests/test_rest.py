import re

import pytest
from django.test import TestCase
from django.urls import reverse
from expunger.tests.test_rest import Authenticated
from petition import factories

from docket_parser import test_data_path


class TestPetitionAPI(Authenticated, TestCase):
    """Check that the petition generating REST API works"""

    def petition_fields(self):
        """Produce the petition fields expected by the backend."""
        petitioner = factories.PetitionerFactory()
        docket = factories.DocketIdFactory()
        petition = factories.PetitionFactory()
        fines = factories.FinesFactory()
        charges = [factories.ChargeFactory(), factories.ChargeFactory()]

        return {
            "petitioner": {
                "name": petitioner.name,
                "aliases": petitioner.aliases,
                "dob": petitioner.dob.isoformat(),
                "ssn": petitioner.ssn,
                "address": {
                    "street1": petitioner.address.street1,
                    "street2": petitioner.address.street2,
                    "city": petitioner.address.city,
                    "state": petitioner.address.state,
                    "zipcode": petitioner.address.zipcode
                }
            },
            "petition": {
                "date": petition.date,
                "complaint_date": petition.complaint_date,
                "ratio": petition.ratio.name,
                "otn": petition.otn,
                "judge": petition.judge,
            },
            "dockets": [str(docket)],
            "fines": {
                "total": fines.total,
                "paid": fines.paid
            },
            "charges": [
                {
                "date": charges[0].date,
                "statutes": charges[0].statute,
                "grade": charges[0].grade,
                "description": charges[0].description,
                "disposition": charges[0].disposition,
                },
                {
                "date": charges[1].date,
                "statutes": charges[1].statute,
                "grade": charges[1].grade,
                "description": charges[1].description,
                "disposition": charges[1].disposition,
                }
            ],
        }

    def test_petition(self):
        """Petitions can be produced via REST"""

        data = self.petition_fields()

        url = reverse("petition:generate")
        res = self.authenticated_client.post(url, data, content_type="application/json")
        self.assertEqual(res.status_code, 200)


class TestDocketParserAPI(Authenticated, TestCase):
    """Tests for the REST docket processing API"""

    def test_post_docket(self):
        """Check that posting a specific docket file works and generates expected information."""
        url = reverse("petition:parse-docket")

        pdf_path = test_data_path / "dockets" / "pdfs" / "merge-cp-01.pdf"

        with pdf_path.open("rb") as file:
            res = self.authenticated_client.post(url, {"docket_file": file})
        self.assertEqual(res.status_code, 200)
        # I spent an hour looking for documentation of the .json method of Response, or its definition in source code,
        # and couldn't find anything. Can't tell if it comes from rest_framework or base django.
        # I did find some usages of it without explanation in django-rest-framework tests/test_requests_client.py
        jsr = res.json()

        # Not storing sensitive PII in tests, instead checking that result has correct shape
        petitioner = jsr["petitioner"]
        assert len(petitioner["name"]) == 15
        assert len(petitioner["aliases"]) == 1
        assert len(petitioner["aliases"][0]) == 13
        dob = petitioner["dob"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", dob), f"Incorrect or missing date of birth: {dob}"

        self.assertEqual(
            jsr["petitions"][0]["docket_info"],
            {
                "judge": "Fleisher, Leslie",
                "complaint_date": "**REMOVED*",
                "otn": "**REMOVED*",
                "ratio": "full"
            }
        )

        self.assertEqual(
            jsr["petitions"][0]["docket_numbers"],
            ["*******REMOVED*******", "*******REMOVED*******"]
        )

        self.assertEqual(
            jsr["petitions"][0]["charges"],
            [
                {
                    "description": "FORGERY",
                    "statute": "18 § 4101",
                    "date": "**REMOVED*",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "THEFT BY UNLAWFUL TAKING OR DISPOSITION",
                    "statute": "18 § 3921",
                    "date": "**REMOVED*",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "THEFT BY DECEPTION",
                    "statute": "18 § 3922",
                    "date": "**REMOVED*",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "THEFT BY RECEIVING STOLEN PROPERTY",
                    "statute": "18 § 3925",
                    "date": "**REMOVED*",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "TAMPERING WITH RECORDS OR IDENTIFICATION",
                    "statute": "18 § 4104",
                    "date": "**REMOVED*",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "Bad Checks",
                    "statute": "18 § 4105 §§ A1",
                    "date": "**REMOVED*",
                    "grade": "M2",
                    "disposition": "Guilty Plea"
                },
                {
                    "description": "SECURING EXEC DOCUMENTS BY DECEPTION",
                    "statute": "18 § 4114",
                    "date": "**REMOVED*",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                }
            ]
        )

    def test_post_fines(self):
        """Get amounts for fines & fees."""
        url = reverse("petition:parse-docket")
        pdf_path = test_data_path / "dockets" / "pdfs" / "merge-cp-01.pdf"

        with pdf_path.open("rb") as f:
            res = self.authenticated_client.post(url, {"docket_file": f})

        self.assertEqual(res.status_code, 200)
        jsr = res.json()

        self.assertEqual(
            jsr["petitions"][0]["fines"],
            {
                "total": 7842.12,
                "paid": 1196.0 + 1519.48
            }
        )

    @pytest.mark.slow
    def test_all_dockets(self):
        """Check that each test docket can be processed without error. (Does not check for correct result)"""
        url = reverse("petition:parse-docket")
        test_docket_paths = (test_data_path / "dockets" / "pdfs").glob("*.pdf")
        for test_docket_path in test_docket_paths:
            with test_docket_path.open("rb") as f:
                response = self.authenticated_client.post(url, {"docket_file": f})
                assert response.status_code == 200
                expected_keys = {"petitioner", "petitions"}
                assert set(response.json().keys()) == expected_keys
                expected_petition_keys = {"charges", "docket_info", "docket_numbers", "fines"}
                assert set(response.json()["petitions"][0].keys()) == expected_petition_keys

    def test_multidockets_1(self):
        """Ensure we get relevant docket numbers from merge-cp-01.pdf"""
        expect = ["*******REMOVED*******", "*******REMOVED*******"]

        pdf_path = test_data_path / "dockets" / "pdfs" / "merge-cp-01.pdf"
        url = reverse("petition:parse-docket")

        with pdf_path.open("rb") as f:
            res = self.authenticated_client.post(url, {"docket_file": f})

        jsr = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertNotIn("error", jsr, msg=f"Unexpected error: {jsr}")
        self.assertEqual(jsr["petitions"][0]["docket_numbers"], expect)

    def test_multidockets_2(self):
        """Ensure we get relevant docket numbers from merge-mc-02.pdf"""
        expect = ["*******REMOVED*******", "*******REMOVED*******"]

        pdf_path = test_data_path / "dockets" / "pdfs" / "merge-mc-02.pdf"
        url = reverse("petition:parse-docket")

        with pdf_path.open("rb") as f:
            res = self.authenticated_client.post(url, {"docket_file": f})

        jsr = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertNotIn("error", jsr, msg=f"Unexpected error: {jsr}")
        self.assertEqual(jsr["petitions"][0]["docket_numbers"], expect)
