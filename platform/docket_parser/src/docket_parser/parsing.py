# -*- coding: utf-8 -*-
import datetime
import logging
import re
import traceback
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import IO, List, Any

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


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class DocketVisitor(NodeVisitor):
    """NodeVisitor to go through a parse tree and get the relevant information for expungement petitions"""

    # These are terms which don't have any children that we care about.
    # They should be leaves in the *visited* tree, i.e. they should have no visited children.
    # The leaves of the (not visited) parse tree are string literals.
    string_leaves = ["defendant_name", "docket_number", "judge", "otn", "originating_docket_number",
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
    def add_leaf_visitor(cls, leaf_name: str):
        """Add a visit method for a given leaf name, which returns a dictionary containing only the leaf name as key
        and the stripped text of node as value.
        """

        def visit_leaf(self, node, visited_children) -> dict[str, str]:
            return {leaf_name: node.text.strip()}

        method_name = "visit_" + leaf_name
        setattr(cls, method_name, visit_leaf)

    @classmethod
    def add_date_visitor(cls, date_name: str):
        """Add a visit method for a given date name, which returns a dictionary containing only the date name as key
        and a date object as value.
        """

        def visit_date(self, node, visited_children) -> dict[str, datetime.date]:
            date_string = node.text.strip()
            month, day, year = date_string.split("/")
            return {date_name: date(int(year), int(month), int(day))}

        method_name = "visit_" + date_name
        setattr(cls, method_name, visit_date)

    @classmethod
    def add_money_visitor(cls, money_term: str):
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

    def generic_visit(self, node, visited_children):
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


def remove_page_breaks(extracted_text: str) -> str:
    """Remove all page breaks from extracted text.
    This allows us to simplify grammar by not needing to check for page breaks everywhere"""
    # Not sure how to write a good test for this fn
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
    printed_date_line_regex = "Printed:" + not_props_open + properties_regex

    for index, line in enumerate(input_lines[1:], start=1):
        if in_page_break:
            if re.match(versus_line_regex, input_lines[index - 1]):
                logger.debug(f"end pbreak matched: {input_lines[index - 1]}")
                in_page_break = False
        elif re.match(printed_date_line_regex, line):
            logger.debug(f"begin pbreak matched: {line}")
            in_page_break = True
        else:
            output_lines.append(line)

    return DocketReader.terminator.join(output_lines) + DocketReader.terminator


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


def get_grammar_from_file(ppeg_file_or_path: str | Path | IO) -> Grammar:
    """Return a parsimonious Grammar object from given file or path."""
    if isinstance(ppeg_file_or_path, IO):
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


def text_from_pdf(file: str | IO | Path, human_readable=False) -> str:
    """Get text from a PDF file or path"""
    reader = DocketReader(file)
    extracted_text = reader.extract_text()
    if human_readable:
        return extracted_text.replace(reader.terminator, '\n')
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


def parse_pdf(file: str | IO | Path) -> dict[str, str | List[str | dict]]:
    """From a PDF, return information necessary for generating expungement petitions."""
    text = text_from_pdf(file)
    return parse_extracted_text(text)


def parse_extracted_text(text: str) -> dict[str, str | list[dict] | float | datetime.date]:
    ppeg_file_path = Path(__file__).parent.joinpath("docket_grammar.ppeg")

    docket_grammar = get_grammar_from_file(ppeg_file_path)

    try:
        tree = docket_grammar.parse(text)
    except ParseError as err:
        logger.error("Unable to parse extracted text")
        raise err

    visitor = DocketVisitor()
    parsed = {}
    try:
        parsed = visitor.visit(tree)
    except VisitationError as e:
        msg = "VisitationError caused by:\n" + get_cause_without_context(e)
        logger.error(msg)
    # convert to json?
    return parsed
