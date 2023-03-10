# -*- coding: utf-8 -*-
import logging
import traceback
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import IO, Union, List

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
                "INSERTED_COMES_BEFORE": DocketReader.comes_before}

# noinspection PyMethodMayBeStatic, PyUnusedLocal
class DocketVisitor(NodeVisitor):
    """NodeVisitor to go through a parse tree and get the relevant information for expungement petitions"""

    # These terms should be treated as leaves in the parse tree.
    leaves = ["defendant_name", "docket_number", "judge", "otn", "originating_docket_number",
              "cross_court_docket_numbers", "alias", "event_disposition", "case_event", "disposition_finality",
              "sequence", "charge_description", "grade", "statute", "offense_disposition"
              ]
    dates = ["dob", "disposition_date", "complaint_date"]
    money_terms = ["assessment", "total", "non_monetary", "adjustments", "payments"]

    def __init__(self):
        super().__init__()
        for leaf_name in self.leaves:
            self.add_leaf_visitor(leaf_name)
        for date_name in self.dates:
            self.add_date_visitor(date_name)
        for money_name in self.money_terms:
            self.add_money_visitor(money_name)

    @classmethod
    def add_leaf_visitor(cls, leaf_name: str):
        """Add a visit method for a given leaf name, which returns a dictionary containing only the leaf name as key
        and the stripped text of node as value.
        """

        def visit_leaf(self, node, visited_children):
            return {leaf_name: node.text.strip()}

        method_name = "visit_" + leaf_name
        setattr(cls, method_name, visit_leaf)

    @classmethod
    def add_date_visitor(cls, date_name: str):
        """Add a visit method for a given date name, which returns a dictionary containing only the date name as key
        and a date object as value.
        """

        def visit_date(self, node, visited_children):
            date_string = node.text.strip()
            month, day, year = date_string.split("/")
            return {date_name: date(int(year), int(month), int(day))}

        method_name = "visit_" + date_name
        setattr(cls, method_name, visit_date)

    @classmethod
    def add_money_visitor(cls, money_term: str):
        """Add a visit method for a given money term, which returns a dictionary containing only the money term as key
        and a float as value.
        """

        def visit_money(self, node, visited_children):
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

    def visit_whole_docket(self, node, visited_children):
        docket_info = {}
        # page_header, *visited_children = visited_children
        for visited_child in flatten(visited_children):
            if isinstance(visited_child, dict):
                docket_info.update(visited_child)
        return docket_info

    def visit_aliases(self, node, visited_children):
        aliases = []
        for child in flatten(visited_children):
            if "alias" in child:
                aliases.append(child["alias"])
        logger.debug(f"aliases: {aliases}")
        return {"aliases": aliases}

    def visit_section_disposition(self, node, visited_children):
        case_events = []
        header, visited_case_events = visited_children
        for visited_case_event in visited_case_events:
            case_event = {}
            charges = []
            for child in flatten(visited_case_event):
                if 'charge_info' in child:
                    charges.append(child['charge_info'])
                elif isinstance(child, dict):
                    case_event.update(child)
            case_event["charges"] = charges
            case_events.append(case_event)
        return {"section_disposition": case_events}

    def visit_charge_info(self, node, visited_children):
        charge_info = {}
        charge_description_lines = []
        for child in flatten(visited_children):
            if "charge_description" in child:
                charge_description_lines.append(child.pop("charge_description"))
            charge_info.update(child)

        charge_info["charge_description"] = ' '.join(charge_description_lines).strip()
        return {"charge_info": charge_info}

    def visit_disposition_grade_statute(self, node, visited_children):
        visited_offense_disposition, *visited_other_children = visited_children
        offense_disposition_lines = []
        result = {}
        for child in flatten(visited_offense_disposition):
            if "offense_disposition" in child:
                offense_disposition_lines.append(child["offense_disposition"])

        result = {"offense_disposition":
                  ' '.join(offense_disposition_lines).strip()}

        for child in flatten(visited_other_children):
            if isinstance(child, dict):
                result.update(child)
        return result


# Helpers

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


def get_grammar_from_file(ppeg_file_or_path: Union[str, Path, IO]) -> Grammar:
    """Return a parsimonious Grammar object from given file or path"""
    if isinstance(ppeg_file_or_path, IO):
        rules_text = ppeg_file_or_path.read()
    else:
        with open(ppeg_file_or_path, 'r', encoding='utf-8') as grammar_file:
            rules_text = grammar_file.read()
    for key, value in REPLACEMENTS.items():
        if "REGEX" not in key.upper():
            value = repr(value)[1:-1]
        rules_text = rules_text.replace(key, value)
    return Grammar(rules_text)


def text_from_pdf(file: Union[str, IO, Path], human_readable=False) -> str:
    """Get text from a PDF file or path"""
    reader = DocketReader(file)
    extracted_text = reader.extract_text()
    if human_readable:
        return extracted_text.replace(reader.terminator, '\n')
    return extracted_text


def get_cause_without_context(exc: VisitationError) -> str:
    """Get the cause of a VisitationError as a string, without the parse tree context."""
    tb = traceback.format_exception(exc)
    original_traceback_string = ''
    for line in tb:
        if "The above exception was the direct cause of the following exception:" in line:
            return original_traceback_string
        original_traceback_string += line
    return original_traceback_string


def parse_pdf(file: Union[str, IO, Path]) -> dict[str, Union[str, List[Union[str, dict]]]]:
    """From a PDF, return information necessary for generating expungement petitions."""
    text = text_from_pdf(file)
    ppeg_file_path = Path(__file__).parent.joinpath("docket_grammar.ppeg")

    docket_grammar = get_grammar_from_file(ppeg_file_path)

    try:
        tree = docket_grammar.parse(text)
    except ParseError as err:
        logger.error("Unable to parse pdf")
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
