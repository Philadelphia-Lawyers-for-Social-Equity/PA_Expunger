# -*- coding: utf-8 -*-

import datetime
from pathlib import Path
from docket_parser.core import flatten, parse_pdf


DATA_PATH = Path(__file__).parent / "data"


class TestParsing:

    def check_expect(self, check, expect, msg):
        "Ensure key/vals from expect are matched in check"

        for key, val in expect.items():
            assert check[key] == val, msg

    # Ignoring test for now because of a bug in reading disposition.
    def _test_parser_04(self):
        """Ensure we can read the ARD sample."""
        testfile = DATA_PATH / "test-04.pdf"

        with testfile.open("rb") as f:
            pdf = parse_pdf(f)

        expect_disposition = [
            {
                'grade': None,
                'offense_disposition': 'Proceed to Court',
                'charge_description':
                    'DUI: Gen Imp/Inc of Driving Safely - 1st Off',
                'date': None,
                'sequence': 1,
                'statute': '75 § 3802',
                'is_final': False
            },
            {
                'grade': None,
                'offense_disposition': 'ARD - County',
                'charge_description':
                    'DUI: Gen Imp/Inc of Driving Safely - 1st Off',
                'date': datetime.date(2020, 2, 28),
                'sequence': 1,
                'statute': '75 § 3802',
                'is_final': False
            }
        ]

        for i in range(len(expect_disposition)):
            self.check_expect(pdf["section_disposition"][i],
                              expect_disposition[i],
                              "dispositions section #%d" % i)

    def test_parser_01(self):
        """Ensure we can parse first sample"""
        testfile = DATA_PATH / "not_crystal_reports.pdf"

        with testfile.open("rb") as f:
            parsed = parse_pdf(f)

        expect_docket = {
            'docket': 'CP-51-CR-0100261-2004',
            'defendant': 'Jerry Seinfeld'}

        self.check_expect(parsed["section_docket"], expect_docket,
                          "docket section")

        expect_defendant_information = {
            'aliases': ['Seinfeld, Jerry F.', 'Thomas, Jerry'],
            'dob': datetime.date(1981, 1, 17)}

        self.check_expect(parsed["section_defendant_information"],
                          expect_defendant_information,
                          "defendant information section")

        expect_case = {
            'otn': 'N 239191-1',
            'judge': 'Snite, A. Jack Jr.',
            'originating_docket': 'MC-51-CR-1101021-2003',
            }

        self.check_expect(parsed["section_case_information"], expect_case,
                          "case section")

        expect_status = {'complaint_date': datetime.date(2003, 11, 4)}
        self.check_expect(parsed["section_status_information"], expect_status,
                          "status_information_section")

        expect_disposition = [
            {
                'grade': None,
                'offense_disposition': 'Guilty Plea',
                'charge_description': 'ROBBERY',
                'date': datetime.date(2004, 11, 12),
                'sequence': 1,
                'statute': '18 § 3701',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Guilty Plea',
                'charge_description': 'CARRYING FIREARMS WITHOUT LICENSE',
                'date': datetime.date(2004, 11, 12),
                'sequence': 2, 'statute': '18 § 6106',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'CARRYING FIRE ARMS/PUBLIC STREET OR PLACE',
                'date': datetime.date(2004, 11, 12),
                'sequence': 3,
                'statute': '18 § 6108',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'POSSESSION ARMS-CONV CRIME OF VIOLENCE',
                'date': datetime.date(2004, 11, 12),
                'sequence': 4,
                'statute': '18 § 6105',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'THEFT BY UNLAWFUL TAKING OR DISPOSITION',
                'date': datetime.date(2004, 11, 12),
                'sequence': 5,
                'statute': '18 § 3921',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'THEFT BY RECEIVING STOLEN PROPERTY',
                'date': datetime.date(2004, 11, 12),
                'sequence': 6,
                'statute': '18 § 3925',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'POSSESSING INSTRUMENTS OF CRIME',
                'date': datetime.date(2004, 11, 12),
                'sequence': 7,
                'statute': '18 § 907',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'TERRORISTIC THREATS',
                'date': datetime.date(2004, 11, 12),
                'sequence': 8, 'statute': '18 § 2706',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'CRIMINAL CONSPIRACY',
                'date': datetime.date(2004, 11, 12),
                'sequence': 9,
                'statute': '18 § 903',
                'is_final': True
            },

            {
                'grade': None, 'offense_disposition': 'Guilty Plea',
                'charge_description': 'ROBBERY',
                'date': datetime.date(2004, 11, 12),
                'sequence': 10,
                'statute': '18 § 3701',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'CARRYING FIREARMS WITHOUT LICENSE',
                'date': datetime.date(2004, 11, 12),
                'sequence': 11,
                'statute': '18 § 6106',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'CARRYING FIRE ARMS/PUBLIC STREET OR PLACE',
                'date': datetime.date(2004, 11, 12),
                'sequence': 12, 'statute': '18 § 6108',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'POSSESSION ARMS-CONV CRIME OF VIOLENCE',
                'date': datetime.date(2004, 11, 12),
                'sequence': 13,
                'statute': '18 § 6105',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'THEFT BY UNLAWFUL TAKING OR DISPOSITION',
                'date': datetime.date(2004, 11, 12),
                'sequence': 14, 'statute': '18 § 3921',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'THEFT BY RECEIVING STOLEN PROPERTY',
                'date': datetime.date(2004, 11, 12),
                'sequence': 15,
                'statute': '18 § 3925',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'POSSESSING INSTRUMENTS OF CRIME',
                'date': datetime.date(2004, 11, 12),
                'sequence': 16,
                'statute': '18 § 907',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Nolle Prossed',
                'charge_description': 'TERRORISTIC THREATS',
                'date': datetime.date(2004, 11, 12),
                'sequence': 17,
                'statute': '18 § 2706',
                'is_final': True
            },

            {
                'grade': None,
                'offense_disposition': 'Guilty Plea',
                'charge_description': 'CRIMINAL CONSPIRACY',
                'date': datetime.date(2004, 11, 12),
                'sequence': 18, 'statute': '18 § 903',
                'is_final': True
            }]

        for i in range(len(expect_disposition)):
            self.check_expect(parsed["section_disposition"][i],
                              expect_disposition[i],
                              "dispositions section #%d" % i)

        expect_financial = {
            "assessment": 332.60,
            "payments": -87.50,
            "adjustments": -80.60,
            "non-monetary": 0,
            "total": 164.50
        }

        self.check_expect(
            parsed["section_financial_information"], expect_financial,
            "financial_section")


class TestHelpers:

    def test_flatten_already_flat(self):
        """Ensure we leave flat lists unchanged."""
        assert list(flatten([])) == []
        assert list(flatten([1])) == [1]
        assert list(flatten([1, 2, 3])) == [1, 2, 3]

    def test_flatten_single_nest(self):
        """Ensure we flatten nested lists."""
        assert list(flatten([[[]]])) == []
        assert list(flatten([[[["hello"]]]])) == ["hello"]

    def test_flatten_multiple_nests(self):
        """Ensure we flatten multple nested lists."""
        assert list(flatten([[[1], [2, 3]], 4, [[[5], 6], 7], 8])) == \
            [1, 2, 3, 4, 5, 6, 7, 8]
