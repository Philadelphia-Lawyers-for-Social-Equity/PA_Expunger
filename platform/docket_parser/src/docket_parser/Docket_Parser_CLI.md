# Docket_Parser CLI

The `docket_parser` includes a command line interface (CLI) that can be used for debugging, viewing the parsed information from test documents, and anonymizing court records so they can be used as test documents. 

To access the CLI:

```sh
# Initialize the docker containers
docker-compose up

# In a new terminal, open a bash terminal
docker-compose exec -it expunger bash

# CLI commands follow the following format:
python -m docket_parser <positional arguments>
```

## Debugging and Viewing Parsed Info

The CLI provides a useful way to view the information that is extracted from a court record and see any errors that may be occuring when a document is parsed.  This can be done by entering a pdf file path or file name into the CLI, along with some optional positional arguments.

```sh
# positional arguments for debugging and viewing parsed info:
  filename              Docket to analyze. If not a valid filename, will try to find matching test pdf
  -h, --help            Show this help message and exit
  --loglevel LOGLEVEL   Set log level
  -v, --verbose         Print logging messages
  -o                    View the complete text output of the parser, rather than the parsed information
```

Here are some examples of how to use the CLI to view parsed information from test documents:
```sh
# To see the parsed information from a test document
python -m docket_parser anon_merge-cp-01

# To see the complete text from the parser
python -m docket_parser anon_merge-cp-01 -t
```

## Creating Test Files

If new test documents are added to `tests/data/court_summaries` or `test/data/dockets`, the CLI can be used to create the corresponding .txt files that are needed for testing.  Tests in `test_parsing.py` are designed to compare the parsing output to .txt files stored in the `/extracted` and `/page_break` test data folders.

To create the necessary .txt files, use the `-e` and `-p` flags.
```sh
# To create the .txt files for the `/extracted` folder
python -m docket_parser -e

# To create the .txt files for the `/page_break` folder
python -m docket_parser -p
```
Each of these commands will create the corresponding .txt file for every pdf in the `tests/data` directory.  The .txt files can then be moved into their appropriate locations.

# Anonymization
Dockets and court summaries obtained from the Unified Judicial System of Pennsylvania's Case Search Web Portal must be anonymized before they are made available for use as samples or test documents.
The defendant's personal identifying information, docket numbers, dates, and other uniquely identifiable information must be replaced with fake or randomly-generated information.
Anonymization of these documents is done through the use of a `.anonymize` file and anonymization tools accessed through the `docket_parser` CLI.

## The .anonymize File
In order to anonymize a court summary or docket, you must first create a .anonymize text file.  The .anonymize file will serve as a dictionary of key value pairs of sensitive info keys and replacement values.

The .anonymize text file should be saved in the /anonymization folder within data/dockets or data/court_summaries.
Its name should match the corresponding docket or court summary.
For example, the .anonymize file for a docket pdf titled `john-doe-mc-docket` would be `john-doe-mc-docket.anonymize`

The following information about the defendant must be included with replacement values in the `.anonymize` file:
- Hair color
- Eye color
- Street address
- City (if not Philadelphia)
- Zip code (which should be replaced with a non-existent zip code like 19100)
- Social Security Number (SSN)
- State Identification Number (SID)

Certain kinds of potentially identifying information can be replaced automatically and are not required to be included in the .anonymize file.
The anonymization function is able to make randomly generated values for:
- Name and aliases
- Offense Tracking Numbers (OTNs)
- Docket Numbers
- Legacy Docket Numbers
- Payment Plan Numbers and Receipt Numbers
- Long numbers such as PA Drivers License Numbers, Legacy Microfilm Numbers, and District Control Numbers (DCNs)
- Dates

As an alternative to providing name replacements in the .anonymize file or automatically generating name replacements, you can choose to create name replacements in the CLI when prompted during the anonymization process.
To do this, include a `-n` or `--name` flag in the CLI command.
You will be shown letters that are available for use in replacment names and prompted to enter replacement values for each name and alias.

The sensitive information in the .anonymize file is treated as regex patterns by the anonymization function.  The function searches the pdf for text that matches the regex patterns of sensitive information and replaces that text with the corresponding replacement values.  If the anonymization function does not completely replace every instance of sensitive information, or replaces text which should not be anonymized, it can often be corrected by using a more detailed regex pattern in the .anonymize file.

- Keys for common names or words that must be replaced may need to include additional regex tokens to specifically identify the desired replacements.
    - If the defendant"***REMOVED***"s hair or eye color can be identified by excluding spaces before or after the word Brown, (?<!\ )Brown(?![ ,]).
    - If a defendant, John Smith, shares a name with a judge on the docket, like Judge Jane Smith, keys for the defendant's name must always include other context so that the judge's name is not replaced as well: 'John Smith' and 'Smith, John', not just 'John' and 'Smith'.
- Any regex special characters that appear in sensitive info you wish to replace must either be preceded by an escaping '\\' to avoid the regex search applying the character's special meaning. For example, periods (`.`) in regex patterns are treated as a catch-all match for any character.  A name like 'John G. Smith' could be entered in the anonymization file as `John G\. Smith`.
- In general, information that should (or should not) be replaced can be added to the .anonymize file with an appropriate replacement value.  Any information/replacement pairs in the .anonymize file will take precenece over auto-generated replacement values.
- Replacements should contain the same number of characters as the info being replaced.  For example, 'John' could be replaced with the word 'Some' but should not be replaced with the word 'Somebody'.

The following code block is a sample of what a .anonymize file might look like.  The text to the left of each semicolon is the information that will be replaced.  The text to the right of each semicolon is the replacement value.  Note that you can comment out a line by adding `#` to the beginning of the line.

```
John G\. Doe;Some P. Any
Doe, John G\.;Any, Some P.
# John;Some
(?<!\ )Brown(?![ ,]);Color
1740 Main Ave;1001 Easy St.
19102;19111
101-11-0101;354-32-2187
651-35-15-0;000-00-00-5
MC-51-CR-0691261-2055;MC-51-CR-1234567-1234;
08/01/2055;05/11/1970
```


## Running the Anonymization CLI
---
After the .anonymize file is prepared, the original pdf can be anonymized through the CLI.

The CLI command accepts three arguments:
1. The pdf name(s) or pdf file path(s) to be anonymized.
    - One or more pdf names or file paths must be provided.
    - This argument can take the form of:
        - a full file path: `/srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/pdfs/john-doe-cp-docket.pdf`
        - a pdf file name that is saved in a /data subfolder: `john-doe-cp-docket`

2. A required `-a` or `--anonymization-file` flag for the anonymization function.
    - This flag can be included on its own, in which case the program will search for the .anonymization file.
    - Alternatively, this flag can be followed by the complete file path for each .anonymization file, eg. `/srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/anonymization/john-doe-cp-docket.anonymize`

3. An optional `-o` or `--output` flag for the output path.
    - If included, this flag must be followed by the complete file paths for each output file, eg. `/srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/output/john-doe-cp-docket_anonymized.pdf`

To run the anonymization function:

```sh
# In the bash terminal, enter the anonymization command
python -m docket_parser <pdf_file_path> -a <anonymization_file_path> -o <output_file_path>
```

Examples of what the CLI command can be for anonymizing one file are:
```sh
python -m docket_parser /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/pdfs/john-doe-cp-docket.pdf -a /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/anonymization/john-doe-cp-docket.anonymize -o /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/output/john-doe-cp-docket_anonymized.pdf
    # OR
python -m docket_parser /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/pdfs/john-doe-cp-docket.pdf -a
    # OR
python -m docket_parser john-doe-cp-docket -a
```

An example of a detailed CLI command for anonymizing multiple files at once is:
```sh
python -m docket_parser /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/pdfs/john-doe-cp-docket.pdf /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/pdfs/john-doe-mc-docket.pdf -a /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/anonymization/john-doe-cp-docket.anonymize -a /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/anonymization/john-doe-mc-docket.anonymize -o /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/output/john-doe-cp-docket_anonymized.pdf -o /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/output/john-doe-mc-docket_anonymized.pdf
```

An example of a CLI command using the `-n` flag, which will allow the user to enter name replacement values in the CLI during the anonymization process:
```sh
python -m docket_parser john-doe-cp-docket -a -n
```

Parsed details from the pdfs, warnings and logger messages will be displayed in the bash terminal.

To include debug logging in the bash terminal, add a `-v` or `--verbose` flag the the command.
```sh
python -m docket_parser /srv/plse/install/docket_parser/src/docket_parser/tests/data/dockets/pdfs/john-doe-cp-docket.pdf -a -v
```

## The Anonymized PDF
---
Anonymized pdfs are colored green to visually distinguish them from the original court documents.  It is important to be aware that successfully creating a green, anonymized pdf does not guarantee that all sensitive information has been removed from the document.

Every pdf produced by the anonymizing function must be manually reviewed to check for any errors or ommissions that caused sensitive or potentially identifying information to remain in the pdf.

If any sensitive or potentially identifying information was not successfully anonymized, the .anonymize file must be amended to address the issue and the file run through the anonymization command again

