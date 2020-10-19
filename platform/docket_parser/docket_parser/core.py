# -*- coding: utf-8 -*-

import logging
from datetime import date

from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

import pdftotext


logger = logging.Logger(__name__)


docket_decoder = Grammar(r"""
    result =
        ( section_docket
        / section_case_information
        / section_status_information
        / section_defendant_information
        / section_disposition
        / section_financial_information
        / junk
        )+

    section_docket =
        ( !"CRIMINAL DOCKET" "DOCKET")
        ( defendant
        / docket
        / (!section_head junk)
        )+

    defendant = "Commonwealth of Pennsylvania" next_line next_line
                space+ "v." next_line
                space* defendant_name next_line
    defendant_name = name+

    docket = "Docket Number" colon docket_id
    docket_id = court dash ~"\d\d" dash case_type dash ~"\d\d\d\d\d\d\d"
                dash ~"\d\d\d\d"
    court = "CP" / "MC"
    case_type = "CR" / "SU" / "MD"

    section_case_information =
        "CASE INFORMATION"
        ( judge
        / otn
        / date_filed
        / arrest_agency
        / arrest_officer
        / originating_docket
        / district_control_number
        / (!section_head junk)
        )+

    judge = "Judge Assigned" colon judge_name
    judge_name = name+

    otn = "OTN" colon otn_id
    otn_id = ~"\w" space ~"\d\d\d\d\d\d" "-" ~"\d"

    date_filed = "Date Filed" colon date

    arrest_agency = "Arresting Agency" colon arrest_agency_name
    arrest_agency_name = name+

    arrest_officer = "Arresting Officer" colon arrest_officer_name
    arrest_officer_name = name+

    originating_docket = "Originating Docket No" colon space* docket_id
    district_control_number = "District Control Number" (space*) dcn
    dcn = alphanum+

    section_status_information =
        "STATUS INFORMATION"
        ( arrest_date
        / (!section_head junk)
        )+

    arrest_date = "Arrest Date" colon space* date

    section_defendant_information =
        "DEFENDANT INFORMATION"
        ( dob
        / aliases
        / (!section_head junk)
        )+

    dob = "Date Of Birth" colon ws date
    aliases = "Alias Name\n" (space* alias "\n")+
    alias = !"CASE" name+

    section_disposition =
        "DISPOSITION SENTENCING/PENALTIES"
        ( disposition
        / (!section_head junk)
        )+

    disposition = space* integer space "/" space charge_description space+
                  offense_disposition space+ (grade space+)? statute next_line
                  (space+ charge_description "\n")?
                  (space+ name+ space* date next_line)?
    charge_description = name+
    offense_disposition = name+
    grade = ( (alphanum alphanum alphanum)
            / (alphanum alphanum)
            / alphanum
            ) space !"§"

    statute = (long_statute / short_statute)
    short_statute = alphanum+ space "§" space alphanum+
    long_statute = short_statute space "§§" space alphanum+

    section_financial_information =
        "CASE FINANCIAL INFORMATION"
        ( grand_totals
        / (!section_head junk)
        )+

    grand_totals = "Grand Totals" colon space+ money space+ money space+
                    money space+ money space+ money
    money = ("$" numeric) / ("($" numeric ")")

    section_head =
        ( "CASE INFORMATION"
        / "STATUS INFORMATION"
        / "CASE PARTICIPANTS"
        / "DEFENDANT INFORMATION"
        / "CHARGES"
        / "DISPOSITION SENTENCING/PENALTIES"
        / "COMMONWEALTH INFORMATION"
        / "ATTORNEY INFORMATION"
        / "CASE FINANCIAL INFORMATION"
        / "ENTRIES"
        )

    name = (letter+ / punct) space?

    next_line = ~"."* "\n"
    junk = (word / ws)
    word = ~"[^\s]"+
    ws = ~"\s"+

    colon = space? ":" space?
    dash = "-"
    date = ~"\d\d/\d\d/\d\d\d\d"

    letter = ~"[A-Za-z]"
    integer = ~"[\d]"+
    alphanum = ~"[A-Za-z0-9]"
    numeric = (~"[0-9]" / "." / ",")+
    punct = ~"[^A-Za-z0-9\s]"
    space = " "
    """)


class DocketExtractor(NodeVisitor):
    "Produce the docket data."

    def generic_visit(self, node, visited_children):
        """Default behavior is to go further down the tree."""
        return visited_children or node

    def visit_result(self, node, visited_children):
        """Merge the sections represented by the parsed tree"""
        result = {}

        for child in flatten(visited_children):
            name = tname(child)

            if name and name[:7] == "section":
                logger.debug("result found section %s", name)

                if name in result.keys():

                    if type(result[name]) is list:
                        result[name] += tval(child)
                    elif type(result[name]) is dict:
                        result[name].update(tval(child))
                    else:
                        logger.error("Unexpected result type: %s is %s", name,
                                     type(result[name]))
                else:
                    result[name] = tval(child)

        return result

    def visit_section_docket(self, node, visited_children):
        """Handle the docket section."""
        result = {
            "docket": val_named("docket", visited_children),
            "defendant": val_named("defendant", visited_children)
        }
        return ("section_docket", result)

    def visit_defendant(self, node, visited_children):
        result = tval(visited_children[7])
        logger.debug("defendant: %s", result)
        return ("defendant", result)

    def visit_defendant_name(self, node, visited_children):
        return ("defendant_name", node.text.strip())

    def visit_docket(self, node, visited_children):
        result = tval(visited_children[2])
        logger.debug("docket: %s", result)
        return ("docket", result)

    def visit_docket_id(self, node, visited_children):
        return ("docket_id", node.text.strip())

    def visit_section_case_information(self, node, visited_children):
        result = {}

        for item in flatten(visited_children):
            name = tname(item)

            if name is not None:
                result[name] = tval(item)

        return ("section_case_information", result)

    def visit_judge(self, node, visited_children):
        result = tval(visited_children[2])
        logger.debug("judge: %s", result)
        return ("judge", result)

    def visit_judge_name(self, node, visited_children):
        return ("judge_name", node.text.strip())

    def visit_otn(self, node, visited_children):
        result = tval(visited_children[-1])
        logger.debug("otn: %s", result)
        return ("otn", result)

    def visit_otn_id(self, node, visited_children):
        return ("otn_id", node.text.strip())

    def visit_date_filed(self, node, visited_children):
        return ("date_filed", tval(visited_children[-1]))

    def visit_arrest_agency(self, node, visited_children):
        return ("arrest_agency", tval(visited_children[-1]))

    def visit_arrest_agency_name(self, node, visited_children):
        return ("arrest_agency_name", node.text.strip())

    def visit_arrest_officer(self, node, visited_children):
        return ("arrest_officer", tval(visited_children[-1]))

    def visit_arrest_officer_name(self, node, visited_children):
        return ("arrest_officer_name", node.text.strip())

    def visit_originating_docket(self, node, visited_children):
        result = val_named("docket_id", visited_children)
        return ("originating_docket", val_named("docket_id", visited_children))

    def visit_district_control_number(self, node, visited_children):
        return ("district_control_number", tval(visited_children[2]))

    def visit_dcn(self, node, visited_children):
        return ("dcn", node.text.strip())

    def visit_section_status_information(self, node, visited_children):
        result = {
            "arrest_date": val_named("arrest_date", visited_children)
        }
        return ("section_status_information", result)

    def visit_arrest_date(self, node, visited_children):
        return ("arrest_date", tval(visited_children[-1]))

    def visit_section_disposition(self, node, visited_children):
        flat = flatten(visited_children[1])
        dispositions = [tval(x) for x in flat if tname(x) == "disposition"]

        logger.debug("section_disposition found %d dispositions",
                     len(dispositions))

        if len(dispositions) == 0:
            return

        return ("section_disposition", dispositions)

    def visit_section_defendant_information(self, node, visited_children):
        result = {
            "dob": val_named("dob", visited_children),
            "aliases": val_named("aliases", visited_children)
        }
        return ("section_defendant_information", result)

    def visit_dob(self, node, visited_children):
        return ("dob", tval(visited_children[-1]))

    def visit_aliases(self, node, visited_children):
        result = [tval(x) for x in flatten(visited_children[1]) if tname(x) == "alias"]
        logger.debug("aliases: %s", result)
        return ("aliases", result)

    def visit_alias(self, node, visited_children):
        return ("alias", node.text.strip())

    def visit_disposition(self, node, visited_children):
        result = {
            "sequence": tval(visited_children[1]),
            "charge_description": tval(visited_children[5]),
            "offense_disposition": tval(visited_children[7]),
            "grade": val_named("grade", visited_children[9]),
            "statute": tval(visited_children[10]),
            "date": val_named("date", visited_children[13])
        }

        extra = val_named("charge_description", (visited_children[12]))

        if extra:
            result["charge_description"] += " " + extra

        logger.debug("disposition %s", result)
        return ("disposition", result)

    def visit_charge_description(self, node, visited_children):
        return ("charge_description", node.text.strip())

    def visit_offense_disposition(self, node, visited_children):
        return ("offense_disposition", node.text.strip())

    def visit_grade(self, node, visited_children):
        return ("grade", node.text.strip())

    def visit_statute(self, node, visited_children):
        return ("statute", tval(visited_children[0]))

    def visit_short_statute(self, node, visited_children):
        return ("short_statute", node.text.strip())

    def visit_long_statute(self, node, visited_children):
        return ("long_statute", node.text.strip())

    def visit_section_financial_information(self, node, visited_children):
        return ("section_financial_information",
                val_named("grand_totals", visited_children))

    def visit_grand_totals(self, node, visited_children):
        result = {
            "assessment": tval(visited_children[3]),
            "payments": tval(visited_children[5]),
            "adjustments": tval(visited_children[7]),
            "non-monetary": tval(visited_children[9]),
            "total": tval(visited_children[11])
        }
        return ("grand_totals", result)

    def visit_money(self, node, visited_children):
        if node.text[0] == "$":
            amount = val_named("numeric", visited_children)
        elif node.text[:2] == "($":
            amount = val_named("numeric", visited_children) * -1
        else:
            raise ValueError("unexpected money match: %s", node.text)

        logger.debug("money with amount: %s", amount)
        return ("money", amount)

    def visit_numeric(self, node, visited_children):
        t = node.text.strip().replace(",", "")
        number = float(t)
        return("numeric", number)

    def visit_date(self, node, visited_children):
        month, day, year = node.text.split("/")
        return ("date", date(int(year), int(month), int(day)))

    def visit_integer(self, node, visited_children):
        text = node.text.strip()
        return ("integer", int(text))

    def visit_alphanum(self, node, visited_children):
        return ("alphanum", node.text.strip())

    def visit_name(self, node, visited_children):
        return ("name", node.text.strip())

    def visit_junk(self, node, visited_children):
        return

# Helpers


def debug_list(items):
    i = 0

    for x in items:
        logger.debug("[%d]: %s", i, x)
        i += 1


def tname(tup):
    """Produce the first item in a tuple, or None for invalid sources."""
    try:
        result = tup[0]
    except IndexError:
        return
    except TypeError:
        return

    return result


def tval(tup):
    """Produce the second item in a tuple, or None for invalid sources."""
    try:
        result = tup[1]
    except IndexError:
        return
    except TypeError:
        return

    return result


def flatten(lol):
    """Reduce a recursive list to a flat one, removing all empty values."""

    def can_flatten(thing):

        if type(thing) in [str, tuple]:
            return False

        try:
            iter(thing)
        except:
            return False
        return True

    for item in lol:

        if type(item) == Node:
            continue

        if not can_flatten(item):
            yield item
        else:
            yield from flatten(item)


def val_named(name, items):
    """Get a named value from a list of items if available."""
    flat = flatten(items)

    for item in flat:
        if tname(item) == name:
            return tval(item)

    logger.debug("Could not find %s", name)


def parse_pdf(file_data):
    """
    From an open PDF, produce complete parser result.
    """
    pdf = pdftotext.PDF(file_data)
    text = "\n\n".join(pdf)

    try:
        tree = docket_decoder.parse(text)
    except ParseError as err:
        logger.error("Unable to parse pdf")
        raise err

    composer = DocketExtractor()
    result = composer.visit(tree)
    return result
