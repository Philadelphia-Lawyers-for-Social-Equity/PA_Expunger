import json

import pytest
from deepdiff import DeepDiff

from docket_parser import test_data_path
from docket_parser.parsing import flatten, parse_extracted_text, parse_pdf, remove_page_breaks

DATA_PATH = test_data_path


def check_expect(check, expected, msg=''):
    """Assert that two given items are the same. If they differ, gives description of differences"""
    # If it ever becomes an issue, can use ignore_order=True here.
    diff = DeepDiff(expected, check)
    if diff != {}:
        message = msg + '\nDifference from checked to expected:\n' + diff.pretty()
        pytest.fail(message)


class TestParsing:
    def test_multiline_charge(self):
        """Check one specific example of a multi-line charge description."""
        test_extracted_text_path = DATA_PATH / "dockets/merge-cp-02.pdf"
        expected_result_path = DATA_PATH / "json/merge-cp-02.json"
        with open(expected_result_path, 'rb') as expected_result_file:
            expected_dict = json.load(expected_result_file)
        if 'section_disposition' not in expected_dict:
            raise ValueError(f"Did not find 'section_disposition' in the test file {expected_result_path}")
        result_dict = parse_pdf(test_extracted_text_path)
        for index, case_event in enumerate(expected_dict['section_disposition']):
            result_charges = result_dict['section_disposition'][index]['charges']
            expected_charges = case_event['charges']
            check_expect(result_charges, expected_charges,
                         "Charge with multi-line description did not get parsed correctly")

    @pytest.mark.slow
    def test_all_dockets(self):
        """Regression test, check that the parsed information from each saved extracted text matches
        known correct json"""
        # Consider using pytest-regtest or pytest-canonical-data plugins in future
        test_extracted_paths = tuple(DATA_PATH.glob("extracted/*.txt"))
        expected_results_dir = DATA_PATH / "json"
        expected_result_paths = []
        for test_extracted_path in test_extracted_paths:
            expected_result_filename = test_extracted_path.name.replace('.txt', '.json')
            expected_result_path = expected_results_dir / expected_result_filename
            expected_result_paths.append(expected_result_path)

        test_expect_pairs = tuple(zip(test_extracted_paths, expected_result_paths))
        assert len(test_expect_pairs) > 0, "Didn't find any test extracted txt/json result pairs"
        for test_extracted_path, expected_result_path in test_expect_pairs:
            with open(test_extracted_path, 'r', encoding='utf-8') as file:
                extracted_text = file.read()
            result = parse_extracted_text(extracted_text)
            # Convert for comparison
            result = json.loads(json.dumps(result, default=repr))
            with open(expected_result_path, 'rb') as expected_result_file:
                expected = json.load(expected_result_file)

            failure_msg = f"Parsed result from {test_extracted_path.name} not equal to expected result" \
                          f" from {expected_result_path.name}"
            check_expect(result, expected, failure_msg)


class TestHelpers:

    def test_remove_page_breaks(self):
        """Regression test, check that output from remove_page_breaks is equal to known good output"""
        expected_result_paths = tuple((DATA_PATH / 'page_break').glob('*.txt'))
        test_paths = []
        for expected_result_path in expected_result_paths:
            test_filename = expected_result_path.name.replace('-no-page-break', '')
            test_path = DATA_PATH / 'extracted' / test_filename
            if test_path.is_file():
                test_paths.append(test_path)
            else:
                raise FileNotFoundError(f"No matching text file with page breaks found for {expected_result_path}")
        test_expect_pairs = tuple(zip(test_paths, expected_result_paths))
        assert len(test_expect_pairs) > 0, "Didn't find any test/result pairs"
        for test_extracted_path, expected_result_path in test_expect_pairs:
            with open(test_extracted_path, 'r', encoding='utf-8') as file:
                extracted_text = file.read()
            with open(expected_result_path, 'r', encoding='utf-8') as file:
                expected = file.read()
            result = remove_page_breaks(extracted_text)
            assert expected == result, "Difference found between remove_page_breaks output and expected result."

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
