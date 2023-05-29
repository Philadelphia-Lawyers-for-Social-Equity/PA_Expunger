import argparse
import logging
import sys
from pathlib import Path

from .parsing import parse_pdf
from .anonymize import anonymize_pdf, load_replacements


# Command Line


def get_arguments():
    parser = argparse.ArgumentParser("PA court document parser CLI")
    parser.add_argument("file", help="PA court document to process")
    parser.add_argument("--log-level", help="set log level", default="INFO")
    parser.add_argument(
        "--verbose", help="print logging messages", action="store_const",
        const=True, default=False)
    parser.add_argument('-a', "--anonymization-file", help="File with sensitive info and replacements")
    parser.add_argument('-o', '--output', help="Path to output file for anonymization")
    return parser.parse_args()


def main():
    args = get_arguments()
    logger = logging.getLogger()
    logger.setLevel(0)

    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    pdf_path = Path(args.file)

    with pdf_path.open("rb") as f:
        parsed = parse_pdf(f)

    print(parsed)

    if args.anonymization_file:
        replacements_file = Path(args.anonymization_file)
        replacements_dict = load_replacements(replacements_file)
        output_path = args.output or Path("output.pdf")
        anonymized = anonymize_pdf(pdf_path, replacements_dict)
        with open(output_path, 'wb') as out_file:
            out_file.write(anonymized.getvalue())


if __name__ == "__main__":
    sys.exit(main())
