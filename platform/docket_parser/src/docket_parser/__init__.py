from pathlib import Path

from .parsing import parse_pdf
from .anonymize import anonymize_pdf

test_data_path = Path(__file__).parent / "tests" / "data"
document_types = ("dockets", "court_summaries")
