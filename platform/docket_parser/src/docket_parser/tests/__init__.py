from pathlib import Path

from docket_parser import document_types, test_data_path


def get_ids(paths: list[Path]) -> list[str]:
    return [path.stem for path in paths]


def get_pdf_paths() -> list[Path]:
    pdf_paths = []
    for document_type in document_types:
        paths = (test_data_path / document_type / 'pdfs').glob("*.pdf")
        pdf_paths.extend(paths)
    return pdf_paths


def get_anon_replacement_paths() -> list[Path]:
    anon_replacement_paths = []
    for document_type in document_types:
        paths = (test_data_path / document_type / 'anonymization').glob("*.anonymize")
        anon_replacement_paths.extend(paths)
    return anon_replacement_paths


def find_anonymization_file(pdf_path: Path) -> Path:
    anonymization_filename = pdf_path.name.replace(".pdf", ".anonymize")
    matching_paths = [path for path in test_data_path.rglob("*/" + anonymization_filename) if path.is_file()]
    if len(matching_paths) == 0:
        raise FileNotFoundError(f"Could not find anonymization file corresponding to {pdf_path}")
    return matching_paths[0]
