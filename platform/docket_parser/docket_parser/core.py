# -*- coding: utf-8 -*-

import logging
from datetime import date

from parsimonious.exceptions import ParseError
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor
from pypdf import PdfReader


logger = logging.getLogger(__name__)


docket_decoder = Grammar(
    r"""
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

    defendant = page_number "Commonwealth of Pennsylvania" next_line
                "v." next_line
                defendant_name next_line
    page_number = "Page" space integer+ space "of" space integer+
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
        / originating_docket
        / (!section_head junk)
        )+

    judge = "Judge Assigned" colon judge_name
    judge_name = name+

    otn = "OTN" colon otn_id
    otn_id = ~"\w" space ~"\d\d\d\d\d\d" "-" ~"\d"
    
    originating_docket = "Originating Docket No" colon space* docket_id

    section_status_information =
        "STATUS INFORMATION"
        ( arrest_date
        / (!section_head junk)
        )+

    arrest_date = "Arrest Date" colon next_line next_line date

    section_defendant_information =
        defendant_information
        ( dob
        / aliases
        / (!section_head junk)
        )+

    dob = "Date Of Birth" colon date
    aliases = "Alias Name" next_line (space* alias next_line)+
    alias = !"CASE" name+

    section_disposition =
        "DISPOSITION SENTENCING/PENALTIES"
        ( disposition_state
        / disposition
        / (!section_head junk)
        )+

    disposition_state = "Sentence Condition" next_line 
                        (word+ next_line)? 
                        date space+ disposition_state_value
    disposition_state_value = "Final Disposition" / "Not Final"

    disposition = integer space "/" space charge_description (next_line charge_description)?
                  offense_disposition space (grade space+)? statute next_line
                  (name+ space* date)?
    charge_description = (cap_word space+)+
    offense_disposition =
            ( "Guilty Plea"
            / "Nolle Prossed"
            / "Dismissed"
            / "ARD - County"
            / "Proceed to Court"
            / "Withdrawn"
            )
    grade = ( (alphanum alphanum alphanum)
            / (alphanum alphanum)
            / alphanum
            ) space !statute_symbol

    statute = (long_statute / short_statute)
    short_statute = alphanum+ space statute_symbol space alphanum+
    long_statute = short_statute space statute_symbol space alphanum+
    statute_symbol = ("§"+ / "\\xc2\\xa7"+)

    section_financial_information =
        case_financial_information
        ( grand_totals
        / (!section_head junk)
        )+

    grand_totals = "Grand Totals" colon money money money money money
    money = parens? dollar numeric parens? space*
    parens = (~"\(" / ~"\)")
    dollar = ~"\$"

    section_head =
        ( "CASE INFORMATION"
        / "STATUS INFORMATION"
        / "CASE PARTICIPANTS"
        / defendant_information
        / "CHARGES"
        / "DISPOSITION SENTENCING/PENALTIES"
        / "COMMONWEALTH INFORMATION"
        / "ATTORNEY INFORMATION"
        / case_financial_information
        / "ENTRIES"
        )
    defendant_information = 
        ( "DEFENDANT INFORMA TION"
        / "DEFENDANT INFROMATION" 
        )
    case_financial_information = 
        ( "CASE FINANCIAL INFORMA TION"
        / "CASE FINANCIAL INFORMATION"
        )

    # + is too greedy and for judge we want the parser to stop before these words
    name = !("Initiation") (letter+ / punct) space*

    next_line = ~"."* "\n"
    junk = (word / ws)
    cap_word = !offense_disposition (capital / punct)+
    word = ~"[^\s]"+
    ws = ~"\s"+

    colon = space? ":" space*
    dash = "-"
    date = ~"\d\d/\d\d/\d\d\d\d"

    capital = ~"[A-Z]"
    letter = ~"[A-Za-z]"
    integer = ~"[\d]"+
    alphanum = ~"[A-Za-z0-9]"
    numeric = (~"[0-9]" / "." / ",")+
    punct = ~"[^A-Za-z0-9\s]"
    space = " "
    """
)


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
                        logger.error(
                            "Unexpected result type: %s is %s", name, type(result[name])
                        )
                else:
                    result[name] = tval(child)

        return result

    def visit_section_docket(self, node, visited_children):
        """Handle the docket section."""
        result = {
            "docket": val_named("docket", visited_children),
            "defendant": val_named("defendant", visited_children),
        }
        return ("section_docket", result)

    def visit_defendant(self, node, visited_children):
        result = tval(visited_children[5])
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
        result = tval(visited_children[-1])
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

    def visit_originating_docket(self, node, visited_children):
        return ("originating_docket", val_named("docket_id", visited_children))

    def visit_section_status_information(self, node, visited_children):
        result = {"arrest_date": val_named("arrest_date", visited_children)}
        return ("section_status_information", result)

    def visit_arrest_date(self, node, visited_children):
        return ("arrest_date", tval(visited_children[4]))

    def visit_section_defendant_information(self, node, visited_children):
        result = {
            "dob": val_named("dob", visited_children),
            "aliases": val_named("aliases", visited_children),
        }
        return ("section_defendant_information", result)

    def visit_dob(self, node, visited_children):
        return ("dob", tval(visited_children[-1]))

    def visit_aliases(self, node, visited_children):
        result = [tval(x) for x in flatten(visited_children[2]) if tname(x) == "alias"]
        logger.debug("aliases: %s", result)
        return ("aliases", result)

    def visit_alias(self, node, visited_children):
        return ("alias", node.text.strip())

    def visit_section_disposition(self, node, visited_children):
        sequence = [
            x
            for x in flatten(visited_children[1])
            if tname(x) in {"disposition", "disposition_state"}
        ]

        is_final = True
        dispositions = []

        for s in sequence:
            if tname(s) == "disposition_state":
                logger.debug("Disposition sequence state: %s" % tval(s))
                is_final = tval(s) == "Final Disposition"
            elif tname(s) == "disposition":
                d = tval(s)
                logger.debug("Disposition sequence item #%d" % d["sequence"])
                d["is_final"] = is_final
                dispositions.append(d)

        logger.debug("section_disposition found %d dispositions", len(dispositions))

        if len(dispositions) == 0:
            return

        return ("section_disposition", dispositions)

    def visit_disposition_state(self, node, visited_children):
        val = val_named("disposition_state_value", visited_children)
        return ("disposition_state", val)

    def visit_disposition_state_value(self, node, visited_children):
        return ("disposition_state_value", node.text)

    def visit_disposition(self, node, visited_children):
        result = {
            "sequence": tval(visited_children[0]),
            "charge_description": tval(visited_children[4]),
            "offense_disposition": tval(visited_children[6]),
            "grade": val_named("grade", visited_children[8]),
            "statute": tval(visited_children[9]),
            "date": val_named("date", visited_children[11]),
        }

        extra = val_named("charge_description", (visited_children[5]))

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
        return (
            "section_financial_information",
            val_named("grand_totals", visited_children),
        )

    def visit_grand_totals(self, node, visited_children):
        result = {
            "assessment": tval(visited_children[2]),
            "payments": tval(visited_children[6]),
            "adjustments": tval(visited_children[5]),
            "non-monetary": tval(visited_children[4]),
            "total": tval(visited_children[3]),
        }
        return ("grand_totals", result)

    def visit_money(self, node, visited_children):
        if node.text[0] == "$":
            amount = val_named("numeric", visited_children)
        elif node.text[0] == "(":
            amount = val_named("numeric", visited_children) * -1
        else:
            raise ValueError("unexpected money match: %s", node.text)

        logger.debug("money with amount: %s", amount)
        return ("money", amount)

    def visit_numeric(self, node, visited_children):
        t = node.text.strip().replace(",", "")
        number = float(t)
        return ("numeric", number)

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


def text_from_pdf(file_data):
    """Read text from an open PDF"""
    reader = PdfReader(file_data)
    return "\n\n".join([page.extract_text() for page in reader.pages])

def parse_pdf(file_data):
    """
    From an open PDF, produce complete parser result.
    """
    text = text_from_pdf(file_data)

    try:
        tree = docket_decoder.parse(text)
    except ParseError as err:
        logger.error("Unable to parse pdf")
        raise err

    composer = DocketExtractor()
    result = composer.visit(tree)
    return result
