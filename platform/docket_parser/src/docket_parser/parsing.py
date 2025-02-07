import datetime
import logging
import re
import traceback
from collections.abc import Iterable
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any, BinaryIO, TextIO

from parsimonious.exceptions import ParseError, VisitationError
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

from .extraction import DocketReader

logger = logging.getLogger(__name__)

REPLACEMENTS = {"NOT_INSERTED_CHARACTER_REGEX": DocketReader.generate_content_regex(),
                "INSERTED_PROPS_OPEN": DocketReader.properties_open,
                "INSERTED_PROPS_CLOSE": DocketReader.properties_close,
                "INSERTED_TERMINATOR": DocketReader.terminator,
                "INSERTED_TAB": DocketReader.tab,
                "INSERTED_COMES_BEFORE": DocketReader.comes_before,
                "INSERTED_BOX_WRAP": DocketReader.box_wrap}


class DocumentType(StrEnum):
    COURT_SUMMARY = "court summary"
    DOCKET = "docket"

    def grammar_path(self) -> Path:
        if self.value == "court summary":
            return Path(__file__).parent.joinpath("court_summary_grammar.ppeg")
        elif self.value == "docket":
            return Path(__file__).parent.joinpath("docket_grammar.ppeg")

    def visitor(self) -> NodeVisitor:
        if self.value == "court summary":
            return CourtSummaryVisitor()
        elif self.value == "docket":
            return DocketVisitor()


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class CourtSummaryVisitor(NodeVisitor):
    string_leaves = ["defendant_name_reversed", "docket_number", "otn", "dcn", "county",
                     "proc_status", "judge", "grade", "statute", "sequence_number", "disposition", "charge_description"]
    date_leaves = ["dob", "disposition_date", "arrest_date"]

    def __init__(self) -> None:
        super().__init__()
        for leaf_name in self.string_leaves:
            self.add_leaf_visitor(leaf_name)
        for date_name in self.date_leaves:
            self.add_date_visitor(date_name)

    @classmethod
    def add_leaf_visitor(cls, leaf_name: str) -> None:
        """Add a visit method for a given leaf name, which returns a dictionary containing only the leaf name as key
        and the stripped text of node as value.
        """

        def visit_leaf(self, node, visited_children) -> dict[str, str]:
            text: str = node.text.strip()
            text = text.replace(DocketReader.box_wrap, '')
            logger.debug({leaf_name: text})
            return {leaf_name: text}

        method_name = "visit_" + leaf_name
        setattr(cls, method_name, visit_leaf)

    @classmethod
    def add_date_visitor(cls, date_name: str) -> None:
        """Add a visit method for a given date name, which returns a dictionary containing only the date name as key
        and a date object as value.
        """

        def visit_date(self, node, visited_children) -> dict[str, datetime.date]:
            date_string = node.text.strip()
            logger.debug({date_name: date_string})
            month, day, year = date_string.split("/")
            return {date_name: date(int(year), int(month), int(day))}

        method_name = "visit_" + date_name
        setattr(cls, method_name, visit_date)

    def generic_visit(self, node, visited_children) -> Node | list:
        """Default behavior is to go further down the tree."""
        return visited_children or node

    def visit_whole_summary(self, node, visited_children) -> dict:
        summary_info = {"dockets": []}
        for visited_child in flatten(visited_children):
            if "docket_number" in visited_child:
                summary_info["dockets"].append(visited_child)
            elif isinstance(visited_child, dict):
                summary_info.update(visited_child)
        return summary_info

    def visit_aliases(self, node, visited_children) -> dict:
        aliases = node.text.strip().split(DocketReader.box_wrap)
        # "WARRANT OUTSTANDING" can show up directly below aliases. Hopefully that's not anyone's actual alias.
        if "WARRANT" in aliases[-1]:
            aliases.pop()
        return {"aliases": aliases}

    def visit_category_section(self, node, visited_children) -> list[dict]:
        category_name = node.text.split(DocketReader.properties_open)[0].strip()
        for visited_child in flatten(visited_children):
            if "docket_number" in visited_child:
                visited_child["category"] = category_name
        return visited_children

    def visit_county_section(self, node, visited_children) -> list[dict]:
        county_name = None
        for visited_child in flatten(visited_children):
            if "county" in visited_child:
                county_name = visited_child.pop("county")
            if "docket_number" in visited_child:
                if not county_name:
                    raise RuntimeError("Failed to find county before docket number")
                visited_child["county"] = county_name
        return visited_children

    def visit_docket_section(self, node, visited_children):
        docket_info = {}
        for visited_child in flatten(visited_children):
            if isinstance(visited_child, dict):
                logger.debug(visited_child)
                docket_info.update(visited_child)
        return docket_info

    def visit_charges_section(self, node, visited_children):
        charges = []
        for visited_child in flatten(visited_children):
            if isinstance(visited_child, dict):
                logger.debug(visited_child)
                charges.append(visited_child)
        return {"charges": charges}

    def visit_charge_segment(self, node, visited_children):
        charge = {}
        for visited_child in flatten(visited_children):
            if isinstance(visited_child, dict):
                charge.update(visited_child)
        return charge


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class DocketVisitor(NodeVisitor):
    """NodeVisitor to go through a parse tree and get the relevant information for expungement petitions"""

    # These are nodes which don't have any children that we care about.
    # They are leaves in the *visited* tree, i.e. they have no visited children.
    # Could rename to visited_leaves if this is confusing.
    string_leaves = ["defendant_name_reversed", "docket_number", "judge", "otn", "originating_docket_number",
                     "cross_court_docket_numbers", "alias", "event_disposition", "case_event", "disposition_finality",
                     "sequence", "charge_description_part", "grade", "statute", "offense_disposition_part"
                     ]
    date_leaves = ["dob", "disposition_date", "complaint_date"]
    money_leaves = ["assessment", "total", "non_monetary", "adjustments", "payments"]

    def __init__(self) -> None:
        super().__init__()
        for leaf_name in self.string_leaves:
            self.add_leaf_visitor(leaf_name)
        for date_name in self.date_leaves:
            self.add_date_visitor(date_name)
        for money_name in self.money_leaves:
            self.add_money_visitor(money_name)

    @classmethod
    def add_leaf_visitor(cls, leaf_name: str) -> None:
        """Add a visit method for a given leaf name, which returns a dictionary containing only the leaf name as key
        and the stripped text of node as value.
        """

        def visit_leaf(self, node, visited_children) -> dict[str, str]:
            logger.debug({leaf_name: node.text.strip()})
            return {leaf_name: node.text.strip()}

        method_name = "visit_" + leaf_name
        setattr(cls, method_name, visit_leaf)

    @classmethod
    def add_date_visitor(cls, date_name: str) -> None:
        """Add a visit method for a given date name, which returns a dictionary containing only the date name as key
        and a date object as value.
        """

        def visit_date(self, node, visited_children) -> dict[str, datetime.date]:
            date_string = node.text.strip()
            logger.debug({date_name: date_string})
            month, day, year = date_string.split("/")
            return {date_name: date(int(year), int(month), int(day))}

        method_name = "visit_" + date_name
        setattr(cls, method_name, visit_date)

    @classmethod
    def add_money_visitor(cls, money_term: str) -> None:
        """Add a visit method for a given money name, which returns a dictionary containing only the money name as key
        and a float as value.
        """

        def visit_money(self, node, visited_children) -> dict[str, float]:
            money = node.text.strip()
            money = money.replace(',', '')
            money_float = 0.0
            if money[0] == '$':
                money_float = float(money[1:])
            elif money[0] == "(":
                money_float = -float(money[2:-1])
            else:
                raise ParseError(f"Expected money term to start with $ or ($\n"
                                 f"Instead found {money}")
            return {money_term: money_float}

        method_name = "visit_" + money_term
        setattr(cls, method_name, visit_money)

    def generic_visit(self, node, visited_children) -> Node | list:
        """Default behavior is to go further down the tree."""
        return visited_children or node

    def visit_whole_docket(self, node, visited_children) -> dict[str, str | list[dict] | float | datetime.date]:
        docket_info = {}
        for visited_child in flatten(visited_children):
            if isinstance(visited_child, dict):
                docket_info.update(visited_child)
        return docket_info

    def visit_aliases(self, node, visited_children) -> dict[str, list[str]]:
        aliases = []
        for child in flatten(visited_children):
            if "alias" in child:
                aliases.append(child["alias"])
        return {"aliases": aliases}

    def visit_section_disposition(self, node, visited_children) -> dict[str, list[dict[str, Any]]]:
        case_events = []
        header, visited_case_events = visited_children
        for visited_case_event in visited_case_events:
            case_event = {}
            charges = []
            for child in flatten(visited_case_event):
                if 'charge_info' in child:
                    charges.append(child.pop('charge_info'))
                case_event.update(child)
            case_event["charges"] = charges
            case_events.append(case_event)
        return {"section_disposition": case_events}

    def visit_charge_info(self, node, visited_children) -> dict[str, dict[str, str]]:
        charge_info = {}
        charge_description_parts = []
        for child in flatten(visited_children):
            if "charge_description_part" in child:
                charge_description_parts.append(child.pop("charge_description_part"))
            charge_info.update(child)

        charge_info["charge_description"] = ' '.join(charge_description_parts).strip()
        return {"charge_info": charge_info}

    def visit_disposition_grade_statute(self, node, visited_children) -> dict[str, str]:
        # This is almost the same as visit_charge_info, except for what it returns.
        # Wonder if there's a way to refactor...
        disposition_grade_statute = {}
        offense_disposition_parts = []
        for child in flatten(visited_children):
            if "offense_disposition_part" in child:
                offense_disposition_parts.append(child.pop("offense_disposition_part"))
            disposition_grade_statute.update(child)

        disposition_grade_statute["offense_disposition"] = ' '.join(offense_disposition_parts).strip()
        return disposition_grade_statute


# Helpers

def get_document_type(text) -> DocumentType:
    """ Given the extracted text of a document, return the appropriate instance of DocumentType.
    If we can't determine document type, raiser error.
    """
    line_2 = text.split('\n')[1]
    if "docket" in line_2.lower():
        return DocumentType.DOCKET
    if "court summary" in line_2.lower():
        return DocumentType.COURT_SUMMARY
    raise ParseError("Could not determine document type")


def remove_docket_page_breaks(extracted_text: str) -> str:
    """Remove all page breaks text extracted from a docket.
    This allows us to simplify grammar by not needing to check for page breaks everywhere"""
    # This function may be useful in the future but is not currently used.
    input_lines = extracted_text.split(DocketReader.terminator)
    output_lines = [input_lines[0]]
    in_page_break = False
    props_open = re.escape(DocketReader.properties_open)
    not_props_open = '[^' + props_open + ']*'
    props_close = re.escape(DocketReader.properties_close)
    not_props_close = '[^' + props_close + ']*'
    properties_regex = props_open + not_props_close + props_close
    versus_line_regex = r"v\. *" + properties_regex
    date_regex = r"\d{1,2}/\d{1,2}/\d{4}"
    printed_date_line_regex = re.compile(r"Printed:\s*" + date_regex + not_props_open + properties_regex)

    for index, line in enumerate(input_lines[1:], start=1):
        if in_page_break:
            if re.match(versus_line_regex, input_lines[index - 1]):
                logger.debug(f"end page break matched: {input_lines[index - 1]}")
                in_page_break = False
        elif re.match(printed_date_line_regex, line):
            logger.debug(f"begin page break matched: {line}")
            in_page_break = True
        else:
            output_lines.append(line)

    return DocketReader.terminator.join(output_lines) + DocketReader.terminator


def remove_court_summary_page_breaks(extracted_text: str) -> str:
    """Remove all page breaks text extracted from a court summary.
    This allows us to simplify grammar by not needing to check for page breaks everywhere"""
    input_lines = extracted_text.split(DocketReader.terminator)
    output_lines = [input_lines[0]]
    in_page_break = False
    box_wrap = re.escape(DocketReader.box_wrap)
    props_open = re.escape(DocketReader.properties_open)
    not_props_open = '[^' + props_open + ']*'
    props_close = re.escape(DocketReader.properties_close)
    not_props_close = '[^' + props_close + ']*'
    properties_regex = props_open + not_props_close + props_close
    bold_properties_regex = props_open + not_props_close + 'bold' + props_close
    continuation_regex = not_props_open + r'\(Continued\)' + bold_properties_regex
    # Fix case where (Continued) is in a text box with line below it:
    continuation_textbox_regex = not_props_open + r'\(Continued\)' + box_wrap + not_props_open + bold_properties_regex
    date_regex = r"\d{1,2}/\d{1,2}/\d{4}"
    printed_date_line_regex = re.compile(r"Printed:\s*" + date_regex + not_props_open + properties_regex)

    for index, line in enumerate(input_lines[1:], start=1):
        if in_page_break:
            if re.match(continuation_regex, input_lines[index - 1]) and \
                    not re.match(continuation_regex, line):
                logger.debug(f"end page break matched: {input_lines[index - 1]}")
                in_page_break = False

                if re.match(continuation_textbox_regex, line):
                    # Include anything after '(Continued)' textbox wrap
                    post_page_break = line.split(DocketReader.box_wrap, 1)[1]
                    output_lines.append(post_page_break)
                else:
                    output_lines.append(line)
        elif re.match(printed_date_line_regex, line):
            logger.debug(f"begin page break matched: {line}")
            in_page_break = True
        else:
            output_lines.append(line)

    return DocketReader.terminator.join(output_lines) + DocketReader.terminator


def remove_page_breaks(extracted_text: str) -> str:
    """Return extracted text with page breaks removed."""
    document_type = get_document_type(extracted_text)
    if document_type == DocumentType.DOCKET:
        return remove_docket_page_breaks(extracted_text)
    elif document_type == DocumentType.COURT_SUMMARY:
        return remove_court_summary_page_breaks(extracted_text)


def flatten(visited_children):
    """Recursively flatten a list of iterables, removing all non-visited nodes."""

    def can_flatten(thing):
        if isinstance(thing, (str, dict, bytes)):
            return False
        return isinstance(thing, Iterable)

    for item in visited_children:
        if type(item) == Node:
            continue

        if not can_flatten(item):
            yield item
        else:
            yield from flatten(item)


def get_grammar_from_file(ppeg_file_or_path: str | Path | TextIO) -> Grammar:
    """Return a parsimonious Grammar object from given file or path."""
    if isinstance(ppeg_file_or_path, TextIO):
        rules_text = ppeg_file_or_path.read()
    else:
        with open(ppeg_file_or_path, 'r', encoding='utf-8') as grammar_file:
            rules_text = grammar_file.read()
    for key, value in REPLACEMENTS.items():
        if "REGEX" not in key.upper():
            # the regex will already be properly escaped, this escapes the other characters.
            value = repr(value)[1:-1]
        rules_text = rules_text.replace(key, value)
    return Grammar(rules_text)


def text_from_pdf(file: str | BinaryIO | Path) -> str:
    """Get text from a PDF file or path"""
    reader = DocketReader(file)
    extracted_text = reader.extract_text()
    return extracted_text


def get_cause_without_context(exc: VisitationError) -> str:
    """Get the cause of a VisitationError as a string, without the parse tree context."""
    # Because the parse trees for dockets are very large, the full context of where in the parse tree an error occurred
    # can be thousands of lines long, which is usually not helpful in debugging.
    tb = traceback.format_exception(exc)
    original_traceback_string = ''
    for line in tb:
        if "The above exception was the direct cause of the following exception:" in line:
            return original_traceback_string
        original_traceback_string += line
    return original_traceback_string


def parse_pdf(file: str | BinaryIO | Path) -> dict[str, str | list[str | dict]]:
    """From a PDF, return information necessary for generating expungement petitions."""
    text = text_from_pdf(file)
    return parse_extracted_text(text)


def reversed_name_to_normal(reversed_name: str) -> str:
    """Input: a reversed name, like 'Doe, John'
    Output: Swap names around the comma, e.g. 'John Doe'
    """
    # This will error if ", " doesn't appear exactly once
    before_comma, after_comma = reversed_name.split(", ")
    return after_comma + ' ' + before_comma


def parse_extracted_text(text: str) -> dict[str, str | list[dict] | float | datetime.date]:
    # First determine what kind of document the extracted text is from:
    document_type = get_document_type(text)

    ppeg_path = document_type.grammar_path()
    grammar = get_grammar_from_file(ppeg_path)
    if document_type == DocumentType.COURT_SUMMARY:
        text = remove_page_breaks(text)

    try:
        tree = grammar.parse(text)
    except ParseError as err:
        logger.error("Unable to parse extracted text")
        raise err

    visitor = document_type.visitor()
    parsed = {}
    try:
        parsed = visitor.visit(tree)
        parsed['type'] = document_type.value
    except VisitationError as e:
        msg = "VisitationError caused by:\n" + get_cause_without_context(e)
        logger.error(msg)
    parsed["defendant_name"] = reversed_name_to_normal(parsed["defendant_name_reversed"])
    return parsed
