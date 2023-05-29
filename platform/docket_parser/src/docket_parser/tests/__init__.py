from pathlib import Path

from deepdiff import DeepDiff
import pytest
from docket_parser import document_types, test_data_path


def check_expect(check, expected, msg=''):
    """Assert that two given items are the same. If they differ, gives description of differences"""
    # If it ever becomes an issue, can use ignore_order=True here.
    diff = DeepDiff(expected, check)
    if diff != {}:
        message = msg + '\nDifference from checked to expected:\n' + diff.pretty()
        pytest.fail(message)


def get_pdf_paths() -> tuple[list[Path], list[str]]:
    """Returns a tuple with two items. The first is a list of paths of test pdfs.
    The second is a list of strings, which are the file names for the paths, in the same order.
    This function is intended to work with the pytest.mark.parametrize fixture."""
    pdf_paths = []
    for document_type in document_types:
        paths = (test_data_path / document_type / 'pdfs').glob("*.pdf")
        pdf_paths.extend(paths)
    ids = [path.stem for path in pdf_paths]
    return pdf_paths, ids
