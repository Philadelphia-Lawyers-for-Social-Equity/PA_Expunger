# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path
from core import parse_pdf, logger, text_from_pdf
import sys
import json

# Command Line


def get_arguments():
    parser = argparse.ArgumentParser("Debug Docket Parser")
    parser.add_argument("filename",
                        help="Docket to analyze. If not a valid filename, will try to find matching test pdf")
    # -o could have a better argument name and or help text
    parser.add_argument("-o", help="Return the output of the parser, rather than the text being parsed",
                        action='store_true')
    parser.add_argument("--loglevel", help="set log level", default="INFO")
    parser.add_argument(
        "--verbose", help="print logging messages", action="store_const",
        const=True, default=False)
    return parser.parse_args()


def main():
    args = get_arguments()

    logger.setLevel(args.loglevel)

    if args.verbose:
        handler = logging.StreamHandler()
        logger.addHandler(handler)

    pdf_path = Path(args.filename)
    if not pdf_path.is_file():
        found_matching_test = False
        test_pdf_paths = Path(__file__).parent.parent.joinpath("tests/data").glob('*.pdf')
        for test_pdf_path in test_pdf_paths:
            if args.filename in test_pdf_path.name:
                pdf_path = test_pdf_path
                found_matching_test = True
                break
        if found_matching_test:
            print(f"{args.filename} not found. Using {pdf_path} instead.")

    with pdf_path.open("rb") as f:
        if args.o:
            parsed = parse_pdf(f)
            out = json.dumps(parsed, indent=4, default=repr)
        else:
            out = text_from_pdf(f)

    print(out)


if __name__ == "__main__":
    sys.exit(main())
