from pathlib import Path

from docket_parser import document_types, test_data_path


def get_pdf_paths() -> tuple[list[Path], list[str]]:
    pdf_paths = []
    for document_type in document_types:
        paths = (test_data_path / document_type / 'pdfs').glob("*.pdf")
        pdf_paths.extend(paths)
    ids = [path.stem for path in pdf_paths]
    return pdf_paths, ids


def get_anon_replacement_paths() -> tuple[list[Path], list[str]]:
    anon_replacement_paths = []
    for document_type in document_types:
        paths = (test_data_path / document_type / 'anonymization').glob("*.anonymize")
        anon_replacement_paths.extend(paths)
    ids = [path.stem for path in anon_replacement_paths]
    return anon_replacement_paths, ids


def find_anonymization_file(pdf_path: Path) -> Path:
    anonymization_filename = pdf_path.name.replace(".pdf", ".anonymize")
    matching_paths = [path for path in test_data_path.rglob("*/" + anonymization_filename) if path.is_file()]
    if len(matching_paths) == 0:
        raise FileNotFoundError(f"Could not find anonymization file corresponding to {pdf_path}")
    return matching_paths[0]
