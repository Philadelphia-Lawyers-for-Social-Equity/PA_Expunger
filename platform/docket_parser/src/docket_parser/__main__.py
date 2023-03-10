# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path
from .core import parse_pdf, logger
import sys

# Command Line


def get_arguments():
    parser = argparse.ArgumentParser("Test Docket Parser")
    parser.add_argument("file", help="Docket to parse")
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

    pdf_path = Path(args.file)

    with pdf_path.open("rb") as f:
        parsed = parse_pdf(f)

    print(parsed)


if __name__ == "__main__":
    sys.exit(main())
