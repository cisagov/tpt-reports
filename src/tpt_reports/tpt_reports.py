"""tpt_reports is a report generation Python library and tool.

Usage:
  tpt-reports SERVICENOW_ID ELECTION_NAME DOMAIN_TESTED JSON_FILE_PATH OUTPUT_DIRECTORY [--log-level=LEVEL]

Options:
  -h --help                         Show this message.
  JSON_FILE_PATH                    Path to the JSON file to act as a data source.
  -l --log-level=LEVEL              If specified, then the log level will be set to
                                    the specified value.  Valid values are "debug", "info",
                                    "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import json
import logging

# import os
import sys
from typing import Any, Dict

# Third-Party Libraries
import docopt

# import pandas as pd
from schema import And, Schema, SchemaError, Use

from ._version import __version__

# from xhtml2pdf import pisa


# from reportlab_generator import report_gen

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGING_FILE = "phish_report_generator.log"


# Issue #6 - Create Unit Tests
# TODO: Add unit tests for following logic and remove this comment.
def get_json_file(phish_result_json):
    """Open JSON file and load data."""
    try:
        json_file = open(phish_result_json)
        LOGGER.info("Loading JSON data from %s", phish_result_json)
        data = json.load(json_file)
        json_file.close()
        return data
    except Exception as error:
        LOGGER.error("Failure to open JSON file: %s", str(error))


def main():
    """Generate PDF reports."""
    args: Dict[str, str] = docopt.docopt(__doc__)
    # Validate and convert arguments as needed
    schema: Schema = Schema(
        {
            "--log-level": And(
                str,
                Use(str.lower),
                lambda n: n in ("debug", "info", "warning", "error", "critical"),
                error="Possible values for --log-level are "
                + "debug, info, warning, error, and critical.",
            ),
            str: object,  # Don't care about other keys, if any
        }
    )

    try:
        validated_args: Dict[str, Any] = schema.validate(args)
    except SchemaError as err:
        # Exit because one or more of the arguments were invalid
        print(err, file=sys.stderr)
        sys.exit(1)

    # Assign validated arguments to variables
    log_level: str = validated_args["--log-level"]

    # Setup logging to central file
    logging.basicConfig(
        filename=LOGGING_FILE,
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S",
        level=log_level.upper(),
    )

    LOGGER.info("Loading TPT Phish Report, Version : %s", __version__)

    LOGGER.info("JSON file path: %s", validated_args["JSON_FILE_PATH"])
    success = get_json_file(validated_args["JSON_FILE_PATH"])

    if success:
        LOGGER.info("JSON FILE loaded successfully.")

    # Stop logging and clean up
    logging.shutdown()


if __name__ == "__main__":
    main()
