# -*- coding: utf-8 -*-

import json
from pathlib import Path

import pytest
from deepdiff import DeepDiff
from docket_parser.core import flatten, parse_pdf

DATA_PATH = Path(__file__).parent.joinpath("data")


def check_expect(check, expected, msg=''):
    """Assert that two given items are the same. If they differ, gives description of differences"""
    # If it ever becomes an issue, can use ignore_order=True here.
    diff = DeepDiff(expected, check)
    message = msg + '\nDifference from checked to expected:\n' + diff.pretty()
    if diff != {}:
        pytest.fail(message)


class TestParsing:
    def test_multiline_charge(self):
        test_docket_path = DATA_PATH.joinpath("dockets/merge-cp-02.pdf")
        expected_result_path = DATA_PATH.joinpath("json/merge-cp-02.json")
        with open(expected_result_path, 'rb') as expected_result_file:
            expected_dict = json.load(expected_result_file)
        if 'section_disposition' not in expected_dict:
            raise ValueError(f"Did not find 'section_disposition' in the test file {expected_result_path}")
        result_dict = parse_pdf(test_docket_path)
        for index, case_event in enumerate(expected_dict['section_disposition']):
            result_charges = result_dict['section_disposition'][index]['charges']
            expected_charges = case_event['charges']
            check_expect(result_charges, expected_charges,
                         "Charge with multi-line description did not get parsed correctly")

    def test_all_dockets(self):
        # Consider using pytest-regtest or pytest-canonical-data plugins in future
        test_docket_paths = tuple(DATA_PATH.glob("dockets/*.pdf"))
        expected_results_dir = DATA_PATH.joinpath("json")
        # expected_result_paths = DATA_PATH.glob("json/*.json")
        expected_result_paths = []
        for test_docket_path in test_docket_paths:
            if 'not_crystal' in test_docket_path.name:
                continue
            expected_result_filename = test_docket_path.name.replace('.pdf', '.json')
            expected_result_path = expected_results_dir.joinpath(expected_result_filename)
            expected_result_paths.append(expected_result_path)

        test_expect_pairs = tuple(zip(test_docket_paths, expected_result_paths))
        assert len(test_expect_pairs) > 0, "Didn't find any test pdf/json result pairs"
        for test_docket_path, expected_result_path in test_expect_pairs:
            result = parse_pdf(test_docket_path)
            # Convert for comparison
            result = json.loads(json.dumps(result, default=repr))
            with open(expected_result_path, 'rb') as expected_result_file:
                expected = json.load(expected_result_file)

            failure_msg = f"Parsed result from {test_docket_path.name} not equal to expected result" \
                          f" from {expected_result_path.name}"
            check_expect(result, expected, failure_msg)


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
        """Ensure we flatten multiple nested lists."""
        assert list(flatten([[[1], [2, 3]], 4, [[[5], 6], 7], 8])) == \
               [1, 2, 3, 4, 5, 6, 7, 8]
