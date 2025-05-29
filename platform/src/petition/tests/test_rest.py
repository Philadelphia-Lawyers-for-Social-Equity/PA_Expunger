import re

import pytest
from django.test import TestCase
from django.urls import reverse
from expunger.tests.test_rest import Authenticated
from petition import factories
from expunger.factories import OrganizationFactory, AttorneyFactory

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
        organization = OrganizationFactory()
        attorney = AttorneyFactory()

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
                "arrest_date": petition.arrest_date,
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
            "category": "Docket",
            "organization": {
                "name": organization.name,
                "address": {
                    "pk": 1,
                    "street1": organization.address.street1,
                    "street2": organization.address.street2,
                    "city": organization.address.city,
                    "state": organization.address.state,
                    "zipcode": organization.address.zipcode
                },
                "phone": organization.phone,
                "pk": 1,
                "url": "http://localhost:8000/api/v0.2.0/expunger/organization/1",
            },
            "attorney": {
                "name": f"{attorney.user.first_name} {attorney.user.last_name}",
                "bar": attorney.bar,
                "pk": 1,
                "url": "http://localhost:8000/api/v0.2.0/expunger/attorney/1/",
                "user_id": 1,
            },
        }

    def test_petition(self):
        """Petitions can be produced via REST"""

        data = self.petition_fields()

        url = reverse("petition:generate")
        res = self.authenticated_client.post(url, data, content_type="application/json")
        self.assertEqual(res.status_code, 200)


class TestGeneratorReportAPI(Authenticated, TestCase):
    """Check that the generator report REST API works"""

    def test_generator_report(self):
        """Generator report can be produced via REST API"""
        
        data = {
            "name": "Jon Doe",
            "dob": "1900-10-22",
            "actions": {
                "partial": 1,
                "full": 1,
            },
            "petitionSummaries": [
                {
                    "docket_numbers": ['CP-451-CR-4896578-1000', 'CP-51-MD-7321720-7237'],
                    "otn": "D 321123-5",
                    "action": "partial",
                    "error": False,
                },
                {
                    "docket_numbers": ['CP-51-CR-1562453-2000'],
                    "otn": "L 741258-3",
                    "action": "full",
                    "error": False,
                },
            ],
        }

        url = reverse("petition:generator-report")
        res = self.authenticated_client.post(url, data, content_type="application/json")
        self.assertEqual(res.status_code, 200)


class TestDocketParserAPI(Authenticated, TestCase):
    """Tests for the REST docket processing API"""

    def test_post_docket(self):
        """Check that posting a specific docket file works and generates expected information."""
        url = reverse("petition:parse-docket")

        pdf_path = test_data_path / "dockets" / "pdfs" / "anon_merge-cp-01.pdf"

        with pdf_path.open("rb") as file:
            res = self.authenticated_client.post(url, {"docket_file": file})
        self.assertEqual(res.status_code, 200)
        # I spent an hour looking for documentation of the .json method of Response, or its definition in source code,
        # and couldn't find anything. Can't tell if it comes from rest_framework or base django.
        # I did find some usages of it without explanation in django-rest-framework tests/test_requests_client.py
        jsr = res.json()

        # Not storing sensitive PII in tests, instead checking that result has correct shape
        petitioner = jsr["petitioner"]
        assert len(petitioner["name"]) == 14
        assert len(petitioner["aliases"]) == 1
        assert len(petitioner["aliases"][0]) == 12
        dob = petitioner["dob"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", dob), f"Incorrect or missing date of birth: {dob}"

        self.assertEqual(
            jsr["petitions"][0]["docket_info"],
            {
                "judge": "Fleisher, Leslie",
                "complaint_date": "1913-11-16",
                "arrest_date": "1902-04-11",
                "otn": "T 760873-7",
                "ratio": "full",
            }
        )

        self.assertEqual(
            jsr["petitions"][0]["docket_numbers"],
            ["CP-51-CR-8442151-4164", "MC-51-CR-2011455-6885"]
        )

        self.assertEqual(
            jsr["petitions"][0]["charges"],
            [
                {
                    "description": "FORGERY",
                    "statute": "18 § 4101",
                    "date": "1917-02-28",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "THEFT BY UNLAWFUL TAKING OR DISPOSITION",
                    "statute": "18 § 3921",
                    "date": "1917-02-28",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "THEFT BY DECEPTION",
                    "statute": "18 § 3922",
                    "date": "1917-02-28",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "THEFT BY RECEIVING STOLEN PROPERTY",
                    "statute": "18 § 3925",
                    "date": "1917-02-28",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "TAMPERING WITH RECORDS OR IDENTIFICATION",
                    "statute": "18 § 4104",
                    "date": "1917-02-28",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                },
                {
                    "description": "Bad Checks",
                    "statute": "18 § 4105 §§ A1",
                    "date": "1917-02-28",
                    "grade": "M2",
                    "disposition": "Guilty Plea"
                },
                {
                    "description": "SECURING EXEC DOCUMENTS BY DECEPTION",
                    "statute": "18 § 4114",
                    "date": "1917-02-28",
                    "grade": None,
                    "disposition": "Nolle Prossed"
                }
            ]
        )

    def test_post_fines(self):
        """Get amounts for fines & fees."""
        url = reverse("petition:parse-docket")
        pdf_path = test_data_path / "dockets" / "pdfs" / "anon_merge-cp-01.pdf"

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

    def test_post_court_summary(self):
        """Check that posting a specific court summary file workds and generates
        expected information"""
        url = reverse("petition:parse-docket")

        pdf_path = test_data_path / "court_summaries" / "pdfs" / "anon_publicly-available.pdf"
        with pdf_path.open("rb") as file:
            res = self.authenticated_client.post(url, {"docket_file": file})
        self.assertEqual(res.status_code, 200)
        jsr = res.json()

        petitioner = jsr["petitioner"]
        assert len(petitioner["name"]) == 12
        assert len(petitioner["aliases"]) == 3
        assert len(petitioner["aliases"][0]) == 19
        dob = petitioner["dob"]
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", dob), f"Incorrect or missing date of birth: {dob}"

        assert len(jsr["petitions"]) == 2

        self.assertEqual(
            jsr["petitions"][0]["docket_info"],
            {
                "arrest_date": "1912-01-11",
                "complaint_date": None,
                "judge": "Hayden, Charles",
                "otn": "P 975786-5",
                "ratio": "full"
            }
        )

        self.assertEqual(
            jsr["petitions"][0]["docket_numbers"],
            ["CP-51-CR-1335055-0346", "MC-51-CR-6340310-2635"]
        )

        self.assertEqual(
            jsr["petitions"][0]["charges"],
            [
                {
                    "description": "Robbery-Inflict Threat Imm Bod Inj",
                    "statute": "18 § 3701",
                    "date": None,
                    "grade": None,
                    "disposition": None
                },
                {
                    "description": "Criminal Attempt - Theft By Unlaw Taking-Movable Prop",
                    "statute": "18 § 901",
                    "date": None,
                    "grade": None,
                    "disposition": None
                },
                {
                    "description": "Criminal Mischief - Damage Property",
                    "statute": "18 § 3304",
                    "date": None,
                    "grade": None,
                    "disposition": None
                },
                {
                    "description": "Robbery-Inflict Threat Imm Bod Inj",
                    "statute": "18 § 3701 §§ A1IV",
                    "date": "1940-09-27",
                    "grade": "F2",
                    "disposition": "Held for Court"
                },
                {
                    "description": "Criminal Attempt - Theft By Unlaw Taking-Movable Prop",
                    "statute": "18 § 901 §§ A",
                    "date": "1940-09-27",
                    "grade": "M1",
                    "disposition": "Held for Court"
                },
                {
                    "description": "Criminal Mischief - Damage Property",
                    "statute": "18 § 3304 §§ A5",
                    "date": "1940-09-27",
                    "grade": "M2",
                    "disposition": "Held for Court"
                }
            ]
        )

        self.assertEqual(
            jsr["petitions"][1]["docket_numbers"],
            ["MC-51-CR-0515540-5251"]
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
                expected_petition_keys = {"charges", "docket_info", "docket_numbers", "fines", "category"}
                assert set(response.json()["petitions"][0].keys()) == expected_petition_keys

    def test_multidockets_1(self):
        """Ensure we get relevant docket numbers from anon_merge-cp-01.pdf"""
        expect = ["CP-51-CR-8442151-4164", "MC-51-CR-2011455-6885"]

        pdf_path = test_data_path / "dockets" / "pdfs" / "anon_merge-cp-01.pdf"
        url = reverse("petition:parse-docket")

        with pdf_path.open("rb") as f:
            res = self.authenticated_client.post(url, {"docket_file": f})

        jsr = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertNotIn("error", jsr, msg=f"Unexpected error: {jsr}")
        self.assertEqual(jsr["petitions"][0]["docket_numbers"], expect)

    def test_multidockets_2(self):
        """Ensure we get relevant docket numbers from anon_merge-mc-02.pdf"""
        expect = ["MC-51-CR-5319217-9189", "CP-51-CR-6693526-3219"]

        pdf_path = test_data_path / "dockets" / "pdfs" / "anon_merge-mc-02.pdf"
        url = reverse("petition:parse-docket")

        with pdf_path.open("rb") as f:
            res = self.authenticated_client.post(url, {"docket_file": f})

        jsr = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertNotIn("error", jsr, msg=f"Unexpected error: {jsr}")
        self.assertEqual(jsr["petitions"][0]["docket_numbers"], expect)

    def test_all_court_summaries(self):
        """Check that each test court summary can be processed without error.
        (Does not check for correct result)"""
        url = reverse("petition:parse-docket")
        test_court_summary_paths = (test_data_path / "court_summaries" / "pdfs").glob("*.pdf")
        for test_court_summary_path in test_court_summary_paths:
            with test_court_summary_path.open("rb") as f:
                response = self.authenticated_client.post(url, {"docket_file": f})
                assert response.status_code == 200
                expected_keys = {"petitioner", "petitions"}
                assert set(response.json().keys()) == expected_keys
                expected_petition_keys = {"charges", "docket_info", "docket_numbers", "fines", "category", "county"}
                assert set(response.json()["petitions"][0].keys()) == expected_petition_keys

    def test_court_summary_grouping(self):
        """Check that dockets in a court summary are correctly grouped
        by OTN or docket number when no OTN exists"""
        url = reverse("petition:parse-docket")

        pdf_path = test_data_path / "court_summaries" / "pdfs" / "anon_multiple_counties.pdf"
        with pdf_path.open("rb") as file:
            res = self.authenticated_client.post(url, {"docket_file": file})
        jsr = res.json()

        self.assertEqual(
            jsr["petitions"][0]["docket_numbers"],
            ['CP-46-CR-6218516-7626', 'CP-51-MD-7321720-7237']
        )

        self.assertEqual(
            jsr["petitions"][6]["docket_numbers"],
            ['CP-51-SA-5372500-7138']
        )

        self.assertEqual(
            jsr["petitions"][7]["docket_numbers"],
            ['MC-51-CR-9272001-5085']
        )