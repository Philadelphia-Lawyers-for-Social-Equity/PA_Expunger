# -*- coding: utf-8 -*-
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import IO, Union

from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

from extraction import DocketReader

logger = logging.getLogger(__name__)

REPLACEMENTS = {"NOT_INSERTED_CHARACTER_REGEX": DocketReader.generate_content_regex(),
                "INSERTED_PROPS_OPEN": DocketReader.properties_open,
                "INSERTED_PROPS_CLOSE": DocketReader.properties_close,
                "INSERTED_NEWLINE": DocketReader.newline,
                "INSERTED_TAB": DocketReader.tab,
                "INSERTED_COMES_BEFORE": DocketReader.comes_before}

singles = ["defendant_name", "docket_number", "judge", "otn", "originating_docket", "cross_court_docket(s)",
           "complaint_date", "dob", "alias", "event_disposition", "case_event", "disposition_finality", "sequence",
           "charge_description", "grade", "statute", "offense_disposition",
           ]


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class DocketVisitor(NodeVisitor):
    """Produce the docket data."""

    def generic_visit(self, node, visited_children):
        """Default behavior is to go further down the tree."""
        return flatten(visited_children) or node

    def visit_whole_docket(self, node, visited_children):
        """Merge the sections represented by the parsed tree"""
        docket_info = {}
        # page_header, *visited_children = visited_children
        for visited_child in flatten(visited_children):
            if isinstance(visited_child, dict):
                docket_info.update(visited_child)
        return docket_info

    def visit_docket_number(self, node, visited_children):
        # logger.debug("visit_docket_number:" + node.text.strip())
        return {"docket_number": node.text.strip()}

    def visit_defendant_name(self, node, visited_children):
        # logger.debug("visit_defendant_name:" + node.text.strip())
        return {"defendant_name": node.text.strip()}

    def visit_judge(self, node, visited_children):
        return {"judge": node.text.strip()}

    def visit_otn(self, node, visited_children):
        return {"otn": node.text.strip()}

    def visit_originating_docket_number(self, node, visited_children):
        return {"originating_docket": node.text.strip()}

    def visit_cross_court_docket_numbers(self, node, visited_children):
        return {"cross_court_docket(s)": node.text.strip()}

    def visit_complaint_date(self, node, visited_children):
        return {"complaint_date": node.text.strip()}

    def visit_dob(self, node, visited_children):
        return {"dob": node.text.strip()}

    def visit_aliases(self, node, visited_children):
        aliases = []
        for child in flatten(visited_children):
            if "alias" in child:
                aliases.append(child["alias"])
        logger.debug(f"aliases: {aliases}")
        return {"aliases": aliases}

    def visit_alias(self, node, visited_children):
        return {"alias": node.text.strip()}

    def visit_section_disposition(self, node, visited_children):
        # logger.debug(dumps([child.text for child in node.children[1].children[0].children[0].children[3].children], indent=2))
        case_events = []
        header, visited_children = visited_children
        logger.debug("visited_case_events: " + str(visited_children))
        case_event = {}
        charges = []
        for child in visited_children:
            logger.debug("section_disposition child: " + str(child))
            if 'event_disposition' in child and 'event_disposition' in case_event:
                case_event["charges"] = charges
                case_events.append(case_event)
                case_event = child
                charges = []
            elif 'charge_info' in child:
                charges.append(child['charge_info'])
            else:
                case_event.update(child)
        case_event["charges"] = charges
        case_events.append(case_event)
        return {"section_disposition": case_events}

    def visit_event_disposition(self, node, visited_children):
        return {"event_disposition": node.text.strip()}

    def visit_case_event(self, node, visited_children):
        return {"case_event": node.text.strip()}

    def visit_disposition_finality(self, node, visited_children):
        return {"disposition_finality": node.text.strip()}

    def visit_charge_info_oneline(self, node, visited_children):
        # unnecessary?
        charge_info = {}
        for child in flatten(visited_children):
            charge_info.update(child)
        return {"charge_info": charge_info}

    def visit_charge_info_multiline(self, node, visited_children):
        charge_info = {}
        charge_description_lines = []
        # Sequence and first line of charge description:
        # for child in visited_children:
        for child in flatten(visited_children):
            if "charge_description" in child:
                charge_description_lines.append(child.pop("charge_description"))
            charge_info.update(child)

        charge_info["charge_description"] = ' '.join(charge_description_lines).strip()
        return {"charge_info": charge_info}

    def visit_sequence(self, node, visited_children):
        # Replacement only necessary because dockets sometimes use 99,999 for dismissed/withdrawn charges
        return {'sequence': node.text.strip().replace(',', '')}

    def visit_charge_description(self, node, visited_children):
        return {'charge_description': node.text.strip()}

    def visit_grade(self, node, visited_children):
        # logger.debug(f"grade node.expr: {node.text}")
        return {"grade": node.text.strip()}

    def visit_statute(self, node, visited_children):
        return {"statute": node.text.strip()}

    def visit_offense_disposition(self, node, visited_children):
        return {"offense_disposition": node.text.strip()}


def add_term_method(term: str, cls: type):
    def visit_term(self, node, visited_children):
        return {term: node.text.strip()}

    method_name = "visit_" + term
    setattr(cls, method_name, visit_term)


# for term in singles:
#     add_term_method(term, DocketVisitor)

# Helpers

def flatten(visited_children):
    """Recursively flatten a list of iterables, removing all non-visited nodes."""

    def can_flatten(thing):
        if isinstance(thing, (str, dict, bytes, tuple)):
            return False
        return isinstance(thing, Iterable)

    for item in visited_children:
        if type(item) == Node:
            continue

        if not can_flatten(item):
            yield item
        else:
            yield from flatten(item)


def get_grammar_from_file(ppeg_file_path: str) -> Grammar:
    with open(ppeg_file_path, 'r') as grammar_file:
        rules_text = grammar_file.read()
    for key, value in REPLACEMENTS.items():
        rules_text = rules_text.replace(key, value)
    return Grammar(rules_text)


def text_from_pdf(file: Union[str, IO, Path], human_readable=False):
    """Read text from an open PDF"""
    reader = DocketReader(file)
    extracted_text = reader.extract_text()
    if human_readable:
        return extracted_text.replace(reader.newline, '\n')
    return extracted_text


def parse_pdf(file: Union[str, IO, Path]):
    """
    From a PDF, return complete parser result.
    """
    text = text_from_pdf(file)

    # TODO: put this in distribution, convert to wheel?
    ppeg_file_path = r'platform/docket_parser/docket_parser/docket_grammar_rules.ppeg'

    docket_grammar = get_grammar_from_file(ppeg_file_path)

    try:
        tree = docket_grammar.parse(text)
    except ParseError as err:
        logger.error("Unable to parse pdf")
        raise err

    visitor = DocketVisitor()
    parsed = visitor.visit(tree)
    return parsed
