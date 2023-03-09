# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path
import sys
import json
from core import parse_pdf, text_from_pdf

# Command Line


def get_arguments():
    parser = argparse.ArgumentParser("Debug Docket Parser")
    parser.add_argument("filename",
                        help="Docket to analyze. If not a valid filename, will try to find matching test pdf")
    # -o could have a better argument name and or help text
    parser.add_argument("-o", help="Return the output of the parser, rather than the text being parsed",
                        action='store_true')
    parser.add_argument("--log-level", help="set log level" ,default="INFO")
    return parser.parse_args()


def main():
    args = get_arguments()

    logger = logging.getLogger()
    logger.setLevel(args.log_level.upper())
    handler = logging.StreamHandler(stream=sys.stderr)
    logger.addHandler(handler)
    formatter = logging.Formatter(fmt='{name} <{levelname}>: {message}', style='{')
    handler.setFormatter(formatter)

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
            print(f"{args.filename} not found. Using {pdf_path} instead.", file=sys.stderr)

    with pdf_path.open("rb") as f:
        if args.o:
            parsed = parse_pdf(f)
            out = json.dumps(parsed, indent=4, default=repr)
        else:
            out = text_from_pdf(f)

    print(out)


if __name__ == "__main__":
    sys.exit(main())
