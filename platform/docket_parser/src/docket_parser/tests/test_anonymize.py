import re

from docket_parser import test_data_path, anonymize_pdf
from docket_parser.anonymize import load_replacements
from docket_parser.extraction import DocketReader
from docket_parser.parsing import text_from_pdf
from docket_parser.tests import get_pdf_paths


class TestDocketAnonymize:
    # TODO: rewrite this test to work with current anonymize_pdf function
    # @pytest.mark.parametrize('pdf_path', get_pdf_paths()[0], ids=get_pdf_paths()[1])
    # def test_all_documents(self, pdf_path):
    #     """For each test document, check that anonymization function removes sensitive info from the document,
    #     and that the anonymized document can still be parsed to get non-sensitive info."""
    #
    #     # Instead of using json (known correct names), just get sensitive info from parsing the pdf
    #     anonymized_pdf = anonymize_pdf(pdf_path)
    #     document_info = parse_pdf(pdf_path)
    #     document_non_sensitive_info = document_info.copy()
    #
    #     # Move sensitive info into another list
    #     defendant_names = []
    #     if "defendant_name" in document_non_sensitive_info:
    #         defendant_names = document_non_sensitive_info.pop("defendant_name")
    #         defendant_names = defendant_names.split(' ')
    #     elif "defendant_name_reversed" in document_non_sensitive_info:
    #         defendant_names = document_non_sensitive_info.pop("defendant_name_reversed")
    #         defendant_names = defendant_names.replace(',', '')
    #         defendant_names = defendant_names.split(' ')
    #
    #     # Will need to change this if names can have more than one comma
    #     aliases = document_non_sensitive_info.pop("aliases", [])
    #     sensitive_info = aliases + defendant_names
    #
    #     segments_from_pdf = text_from_pdf(pdf_path).split(DocketReader.terminator)
    #     segments_from_anonymized_pdf = text_from_pdf(anonymized_pdf).split(DocketReader.terminator)
    #
    #     def has_sensitive_info(text: str):
    #         return any(string in text for string in sensitive_info)
    #
    #     assert len(segments_from_anonymized_pdf) == len(segments_from_pdf), \
    #         "Extracted text from anonymized document has incorrect segment count"
    #     segment_pairs = zip(segments_from_pdf, segments_from_anonymized_pdf)
    #     for segment, anonymized_segment in segment_pairs:
    #         if not has_sensitive_info(segment):
    #             assert segment == anonymized_segment, "Segment without sensitive info was modified"
    #
    #         assert not has_sensitive_info(anonymized_segment), \
    #             f"Sensitive info found in anonymized document: {anonymized_segment}"
    #
    #     parsed_anonymized = parse_pdf(anonymized_pdf)
    #     assert len(parsed_anonymized.pop('aliases')) == len(aliases)
    #     assert parsed_anonymized.pop('defendant_name') is not None
    #     check_expect(parsed_anonymized, document_non_sensitive_info,
    #                  "Parsed result of anonymized document is incorrect")

    def test_one(self):
        """Check that after anonymizing a pdf, the replaced patterns are not found"""
        replacement_file_path = test_data_path / "court_summaries" / "anonymization" / "multiple_categories.anonymize"
        pdf_path = test_data_path / "court_summaries" / "pdfs" / "multiple_categories.pdf"
        replacements_dict = load_replacements(replacement_file_path)
        sensitive_info = list(replacements_dict.keys())
        anonymized_pdf = anonymize_pdf(pdf_path, replacements_dict)
        segments_from_anonymized_pdf = text_from_pdf(anonymized_pdf).split(DocketReader.terminator)
        assert not any(
            pattern.search(segment) for segment in segments_from_anonymized_pdf for pattern in sensitive_info)

    def test_replacements_from_file(self):
        """Load a specific replacement file and check some properties of the resulting dictionary."""
        replacement_file_path = test_data_path / "court_summaries" / "anonymization" / "multiple_categories.anonymize"
        replacements_dict = load_replacements(replacement_file_path)
        assert len(replacements_dict) == 18
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
