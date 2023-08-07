from pathlib import Path

import pytest
from deepdiff import DeepDiff

from docket_parser import test_data_path, document_types
from docket_parser.parsing import flatten, parse_extracted_text, remove_page_breaks

DATA_PATH = test_data_path


def check_expect(check, expected, msg=''):
    """Assert that two given items are the same. If they differ, gives description of differences"""
    # If it ever becomes an issue, can use ignore_order=True here.
    diff = DeepDiff(expected, check)
    if diff != {}:
        message = msg + '\nDifference from checked to expected:\n' + diff.pretty()
        pytest.fail(message)


def get_extracted_document_paths() -> tuple[list[Path], list[str]]:
    extracted_document_paths = []
    for document_type in document_types:
        paths = (DATA_PATH / document_type / 'extracted').glob("*.txt")
        extracted_document_paths.extend(paths)
    ids = [path.stem for path in extracted_document_paths]
    return extracted_document_paths, ids


class TestParsing:
    # Delete this test if/when we decide to use pytest-regressions
    # @pytest.mark.parametrize('document_type', document_types)
    # def test_all_documents(self, document_type: str):
    #     """Regression test, check that the parsed information from each saved extracted text matches
    #     known correct json"""
    #     # Consider using pytest-regtest or pytest-canonical-data plugins in future
    #     extracted_dir = DATA_PATH / document_type / "extracted"
    #     json_dir = DATA_PATH / document_type / "json"
    #     test_extracted_paths = tuple(extracted_dir.glob("*.txt"))
    #     expected_result_paths = []
    #     for test_extracted_path in test_extracted_paths:
    #         expected_result_filename = test_extracted_path.name.replace('.txt', '.json')
    #         expected_result_path = json_dir / expected_result_filename
    #         expected_result_paths.append(expected_result_path)
    #
    #     test_expect_pairs = tuple(zip(test_extracted_paths, expected_result_paths))
    #     assert len(test_expect_pairs) > 0, "Didn't find any test extracted txt/json result pairs"
    #     for test_extracted_path, expected_result_path in test_expect_pairs:
    #         with open(test_extracted_path, 'r', encoding='utf-8') as file:
    #             extracted_text = file.read()
    #         result = parse_extracted_text(extracted_text)
    #         # Convert for comparison
    #         result = json.loads(json.dumps(result, default=repr))
    #         with open(expected_result_path, 'rb') as expected_result_file:
    #             expected = json.load(expected_result_file)
    #
    #         failure_msg = f"Parsed result from {test_extracted_path.name} not equal to expected result" \
    #                       f" from {expected_result_path.name}"
    #         check_expect(result, expected, failure_msg)

    @pytest.mark.parametrize('extracted_document_path', get_extracted_document_paths()[0],
                             ids=get_extracted_document_paths()[1])
    def test_documents(self, data_regression, extracted_document_path):
        with open(extracted_document_path, 'r', encoding='utf-8') as file:
            extracted_text = file.read()
        result = parse_extracted_text(extracted_text)
        data_regression.check(result)

    @pytest.mark.parametrize('document_type', document_types)
    def test_remove_page_breaks(self, document_type):
        """Regression test, check that output from the functions which remove page breaks
        are equal to known good output"""
        page_break_dir = DATA_PATH / document_type / "page_break"
        extracted_dir = DATA_PATH / document_type / "extracted"
        expected_result_paths = tuple(page_break_dir.glob('*.txt'))
        test_paths = []
        for expected_result_path in expected_result_paths:
            test_filename = expected_result_path.name.replace('-no-page-break', '')
            test_path = extracted_dir / test_filename
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
            assert expected == result, "Difference found between remove page breaks output and expected result."


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
