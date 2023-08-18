"""tpt_reports is a report generation Python library and tool.

Usage:
  tpt-reports [--log-level=LEVEL] [JSON_FILE_PATH]

Options:
  -h --help                         Show this message.
  -l --log-level=LEVEL              If specified, then the log level will be set to
                                    the specified value.  Valid values are "debug", "info",
                                    "warning", "error", and "critical". [default: info]
  JSON_FILE_PATH                    Path to the JSON file to act as a data source.
"""

# Standard Python Libraries
import json
import logging

# import os
import sys
from typing import Any, Dict

# Third-Party Libraries
import docopt
from schema import And, Schema, SchemaError, Use

from ._version import __version__

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGING_FILE = "phish_report_generator.log"


# Issue #6 - Create Unit Tests
# TODO: Add unit tests for following logic and remove this comment.
def get_json_file(file_path):
    """Open JSON file and load data."""
    try:
        with open(file_path, encoding="utf-8") as file:
            LOGGER.debug("Loading JSON data from %s", file_path)
            data = json.load(file)
            return data
    except FileNotFoundError as error:
        LOGGER.error("Failure to open JSON file: %s", str(error))
        return None


def main() -> None:
    """Generate PDF reports."""
    args: Dict[str, str] = docopt.docopt(__doc__, version=__version__)
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
            "JSON_FILE_PATH": Use(str, error="JSON_FILE_PATH must be an string."),
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
    json_file_path: str = validated_args["JSON_FILE_PATH"]

    # Set up logging
    logging.basicConfig(
        format="%(asctime)-15s %(levelname)s %(message)s", level=log_level.upper()
    )

    success = get_json_file(json_file_path)

    if success:
        LOGGER.info("JSON FILE loaded successfully.")

    # Stop logging and clean up
    logging.shutdown()
