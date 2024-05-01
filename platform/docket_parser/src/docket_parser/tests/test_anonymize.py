import re
from pathlib import Path

import pytest

from docket_parser import test_data_path, anonymize_pdf
from docket_parser.anonymize import load_replacements, anonymize_pdfs, logger as anonymize_logger
from docket_parser.extraction import DocketReader
from docket_parser.parsing import text_from_pdf, parse_pdf
from docket_parser.tests import get_pdf_paths, get_anon_replacement_paths, find_anonymization_file


class TestDocketAnonymize:
    @pytest.mark.parametrize('pdf_path', get_pdf_paths()[0], ids=get_pdf_paths()[1])
    def test_all_documents(self, pdf_path):
        """For each test document, check that the anonymized document has the same number of segments
        as the test document, and check that parsing the anonymized document returns information for all
        the parsed sections of the test document."""
        name_replacement_prompt = False
        anonymized_pdf = anonymize_pdfs([pdf_path], [find_anonymization_file(pdf_path)], name_replacement_prompt)
        anonymized_path = pdf_path.parent.parent / "output" / pdf_path.name.replace(".pdf", "_anonymized.pdf")

        segments_from_pdf = text_from_pdf(pdf_path).split(DocketReader.terminator)
        segments_from_anonymized_pdf = text_from_pdf(anonymized_path).split(DocketReader.terminator)
        assert len(segments_from_anonymized_pdf) == len(segments_from_pdf), \
            "Extracted text from anonymized document has incorrect segment count"

        document_info = parse_pdf(pdf_path)
        anonymized_info = parse_pdf(anonymized_pdf[0])
        parsed_sections = list(document_info.keys())
        for section in parsed_sections:
            if section == 'aliases':
                assert len(anonymized_info.pop('aliases')) == len(document_info.pop('aliases'))
            else:
                assert anonymized_info.pop(section) is not None

    def test_replacements_from_file(self):
        """Load a specific replacement file and check some properties of the resulting dictionary."""
        replacement_file_path = test_data_path / "court_summaries" / "anonymization" / "multiple_categories.anonymize"
        replacements_dict = load_replacements(replacement_file_path)
        assert len(replacements_dict) == 17
        assert all(isinstance(key, re.Pattern) for key in replacements_dict.keys())
        assert "19101" in replacements_dict.values()

    def test_get_chars(self):
        pdf_paths = get_pdf_paths()[0]
        bold_chars_acc = set(chr(i) for i in range(256))
        normal_chars_acc = set(chr(i) for i in range(256))
        for path in pdf_paths:
            pdf = DocketReader(path)
            fonts = pdf.pages[0].fonts
            bold_font = fonts['/9']
            bold_chars = set(bold_font.unicode_to_cid_map.keys())
            bold_chars_acc.intersection_update(bold_chars)
            if '/a' in fonts:
                normal_font = fonts['/a']
            else:
                normal_font = fonts['/d']
            normal_chars = set(normal_font.unicode_to_cid_map.keys())
            normal_chars_acc.intersection_update(normal_chars)
        bold_chars_acc = ''.join(sorted(bold_chars_acc))
        normal_chars_acc = ''.join(sorted(normal_chars_acc))
        assert 'C' in bold_chars_acc and 'C' in normal_chars_acc
        assert '7' not in bold_chars_acc and '7' not in normal_chars_acc
        # TODO: Currently this test finds the characters that are found in every pdf's fonts.
        # The assert statements may fail if pdfs are added or removed from the list; something else should be checked.

    @pytest.mark.parametrize('anon_replacement_path', get_anon_replacement_paths()[0],
                             ids=get_anon_replacement_paths()[1])
    def test_anonymize_all(self, anon_replacement_path):
        """For all test pdfs, anonymize the pdf and check that it does not contain
           strings that were supposed to be replaced."""
        pdf_path = (anon_replacement_path.parent.parent / "pdfs" / anon_replacement_path.name).with_suffix(".pdf")
        replacements = load_replacements(anon_replacement_path)
        sensitive_info = list(replacements.keys())
        anonymized_pdf = anonymize_pdf(pdf_path, replacements)
        segments_from_anonymized_pdf = text_from_pdf(anonymized_pdf).split(DocketReader.terminator)
        assert not any(
            pattern.search(segment) for segment in segments_from_anonymized_pdf for pattern in sensitive_info)


    def test_anonymize_batch(self):
        """For multiple related .anonymize files that share replacement info, anonymize the corresponding pdfs using
           anonymize_pdfs and check that the anonymized pdfs do not contain strings that were supposed to be replaced."""
        anon_replacement_paths = get_anon_replacement_paths()[0]
        replacement_paths = []
        for path in anon_replacement_paths:
            if 'merge-cp-02' in repr(path) or 'merge-mc-02' in repr(path):
                replacement_paths.append(path)
        pdf_paths = [(path.parent.parent / "pdfs" / path.name).with_suffix(".pdf") for path in replacement_paths]
        replacements = [load_replacements(replacement_path) for replacement_path in replacement_paths]
        name_replacement_prompt = False
        anonymized_pdfs = anonymize_pdfs(pdf_paths, replacement_paths, name_replacement_prompt)
        for i, anonymized_pdf in enumerate(anonymized_pdfs):
            segments_from_anonymized_pdf = text_from_pdf(anonymized_pdf).split(DocketReader.terminator)
            sensitive_info = list(replacements[i].keys())
            assert not any(pattern.search(segment) for segment in segments_from_anonymized_pdf for pattern in sensitive_info)


    def test_warn_squish(self, caplog):
        pdf_path = get_pdf_paths()[0][-1]
        replacements_dict = {re.compile("[^-]-[^-]"):
                                 lambda match: match.string[match.start():match.end()].replace("-", "---")}

        with caplog.at_level("DEBUG", anonymize_logger.name):
            anonymized_pdf = anonymize_pdf(pdf_path, replacements_dict, (1., .9, .9))
        print(caplog.messages)
        with open(pdf_path.parent.parent / "output" / "test_warn_squish.pdf", "wb") as destination_file:
            destination_file.write(anonymized_pdf.getvalue())
        assert any("---" in msg and "squish" in msg for msg in caplog.messages), \
            "A warning should be logged when a replacement is made that squishes characters together a lot"


    def test_name_replacement(self, monkeypatch):
        """Load a specific replacement file and test name replacement using the CLI"""
        pdf_path = [test_data_path / "dockets" / "pdfs" / "event_without_charges.pdf"]
        replacements_path = [test_data_path / "dockets" / "anonymization" / "event_without_charges.anonymize"]
        name_replacement_prompt = True

        name_replacements = ["Ctrbbk", "Brrtiyby"]
        inputs = iter(name_replacements)
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        anonymized_pdf = anonymize_pdfs(pdf_path, replacements_path, name_replacement_prompt)
        parse_anonymized = parse_pdf(anonymized_pdf[0])
        anonymized_name = parse_anonymized["defendant_name"].split(" ")
        assert len(name_replacements) == len(anonymized_name)
        assert set(name_replacements) == set(anonymized_name)

