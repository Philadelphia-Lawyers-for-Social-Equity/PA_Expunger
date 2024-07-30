import argparse
import logging
import sys
from pathlib import Path

from docket_parser import test_data_path
from .anonymize import anonymize_pdf, anonymize_pdfs
from .parsing import parse_pdf
from .tests import get_anon_replacement_paths, find_anonymization_file


# Command Line


def get_arguments():
    parser = argparse.ArgumentParser("PA court document parser CLI")
    parser.add_argument("file", nargs='+', help="PA court document to process")
    parser.add_argument("--log-level", help="set log level", default=None)
    parser.add_argument('-v', '--verbose', help="set log level to DEBUG", action="store_const", const=True,
                        default=False)
    parser.add_argument('-a', "--anonymization-file", action="append", nargs='?', const=True,
                        help="File with sensitive info and replacements, or 'auto' to look for "
                             "corresponding .anonymize file in tests directory")
    parser.add_argument('-manual', "--manual-anonymization", nargs='?', const=True,
                        help="Anonymize a file without using auto-generated values")
    parser.add_argument('-o', '--output', action="append", help="Path to output file for anonymization", )
    parser.add_argument('--anonymize-all-tests', action="store_true",
                        help="Disregard other arguments except log level, anonymize every pdf for which there is a "
                             ".anonymize file in tests by itself and write the output in output directory.")
    parser.add_argument('-n', '--name', help="Option to input replacement name based on available characters",
                        action="store_const", const=True, default=False)
    return parser.parse_args()


def main():
    args = get_arguments()
    logging.basicConfig(format='%(levelname)s %(filename)s:%(lineno)d %(message)s', level=logging.WARNING)
    logger = logging.getLogger()
    if args.verbose:
        logger.setLevel("DEBUG")
    elif args.log_level:
        logger.setLevel(args.log_level)

    if args.anonymize_all_tests:
        for anon_replacement_path in get_anon_replacement_paths()[0]:
            pdf_path = (anon_replacement_path.parent.parent / "pdfs" / anon_replacement_path.name).with_suffix(".pdf")
            anonymized_pdf = anonymize_pdfs([pdf_path], [anon_replacement_path])[0]
            output_path = pdf_path.parent.parent / "output" / pdf_path.name.replace(".pdf", "_anonymized.pdf")
            with open(output_path, "wb") as output_file:
                output_file.write(anonymized_pdf.getvalue())
        return 0

    pdf_paths = [Path(file) for file in args.file]
    for i, pdf_path in enumerate(pdf_paths):
        # Try to find the file from test pdfs
        if not pdf_path.is_file():
            try:
                pdf_path = pdf_path.with_suffix(".pdf")
                matching_paths = [path for path in test_data_path.rglob("*/" + pdf_path.name) if path.is_file()]
                pdf_path = matching_paths[0]
                pdf_paths[i] = pdf_path
            except IndexError:
                print(f"Error: Could not find file {pdf_path}")
                return

        with pdf_path.open("rb") as f:
            parsed = parse_pdf(f)
        print(parsed)

    if args.anonymization_file:
        replacements_paths = []
        if args.anonymization_file[0] == True:
            # Try to find the replacements files if not provided
            for pdf_path in pdf_paths:
                replacements_paths.append(find_anonymization_file(pdf_path))
        else:
            for anonymization_file in args.anonymization_file:
                replacements_paths.append(Path(anonymization_file))

        output_paths = []
        if not args.output:
            # Create output paths if not provided
            for pdf_path in pdf_paths:
                output_path = pdf_path.parent.parent / "output" / pdf_path.name.replace(".pdf", "_anonymized.pdf")
                output_paths.append(output_path)
        else:
            for output_path in args.output:
                output_paths.append(Path(output_path))

        if not args.manual_anonymization:
            anonymized = anonymize_pdfs(pdf_paths, replacements_paths, args.name)
            for index, anonymized_file in enumerate(anonymized):
                with open(output_paths[index], 'wb') as out_file:
                    out_file.write(anonymized[index].getvalue())
        else:
            anonymized = anonymize_pdf(pdf_paths[0], replacements_paths[0])
            with open(output_paths[0], 'wb') as out_file:
                out_file.write(anonymized.getvalue())


if __name__ == "__main__":
    sys.exit(main())
