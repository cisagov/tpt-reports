"""cisagov/tpt-reports: A tool for creating Technical Phishing Test (TPT) reports.

Usage:
  tpt-reports ELECTION_NAME DOMAIN_TESTED JSON_FILE_PATH [--log-level=LEVEL] [--output-dir=OUTPUT_DIRECTORY]

Options:
  -h --help                         Show this message.
  -l --log-level=LEVEL              If specified, then the log level will be set to
                                    the specified value.  Valid values are "debug", "info",
                                    "warning", "error", and "critical". [default: info]
  -o --output-dir=OUTPUT_DIRECTORY  The directory where the final PDF reports
                                    should be saved. [default: ~/]

Arguments:
  ELECTION_NAME                     The name of the election being reported on.
  DOMAIN_TESTED                     The email domain used in the testing.
  JSON_FILE_PATH                    Path to the JSON file to act as a data source.

"""


# Standard Python Libraries
import json
import logging
import os
import sys
from typing import Any, Dict

# Third-Party Libraries
import docopt
from schema import And, Schema, SchemaError, Use
from validator_collection import validators

from ._version import __version__
from .report_generator import report_gen

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGING_FILE = "tpt-reports.log"


# Issue #20 - test load_json_file()
# TODO: Add unit tests for following logic and remove this comment.
def load_json_file(file_path):
    """Open JSON file and load data."""
    try:
        with open(file_path, encoding="utf-8") as file:
            LOGGER.debug("Loading JSON data from %s", file_path)
            data = json.load(file)
            return data
    except FileNotFoundError as error:
        LOGGER.error("Failure to open JSON file: %s", str(error))
        return None


# Issue #21 - test parse_json()
# TODO: Add unit tests for following logic and remove this comment.
def parse_json(data):
    """Parse JSON object for values to report."""
    border_blocked = 0
    border_not_blocked = 0
    host_blocked = 0
    host_not_blocked = 0
    num_payloads = 0
    payloads_list = []
    payloads_meta = {}
    try:
        if data:
            assessment_id = data["id"]
            for payload in data["phishing_assessment"]["payloads"]:
                num_payloads += 1
                payload_data = {}
                payload_data["Payload"] = payload["payload_description"]
                payload_data["C2 Protocol"] = payload["c2_protocol"]

                if payload["border_protection"] == "N":
                    payload_data["Border Protection"] = "Not Blocked"
                    border_not_blocked += 1
                elif payload["border_protection"] == "B":
                    payload_data["Border Protection"] = "Blocked"
                    border_blocked += 1
                else:
                    raise ValueError("border_protection value must be either B or N")

                if payload["host_protection"] == "N":
                    payload_data["Host Protection"] = "Not Blocked"
                    host_not_blocked += 1
                elif payload["host_protection"] == "B":
                    payload_data["Host Protection"] = "Blocked"
                    host_blocked += 1
                else:
                    raise ValueError("host_protection value must be either B or N")

                payloads_list.append(payload_data)

        payloads_meta["border_blocked"] = border_blocked
        payloads_meta["border_not_blocked"] = border_not_blocked
        payloads_meta["host_blocked"] = host_blocked
        payloads_meta["host_not_blocked"] = host_not_blocked
        payloads_meta["num_payloads"] = num_payloads
        payloads_meta["payloads_blocked"] = border_blocked + host_blocked
        payloads_meta["payloads_not_blocked"] = border_not_blocked + host_not_blocked

    except Exception as e:
        LOGGER.exception(str(e))
    return assessment_id, payloads_meta, payloads_list


def generate_reports(election_name, domain_tested, output_directory, json_file_path):
    """Process steps for generating report data."""
    tpt_info = {}
    tpt_info["domain_tested"] = domain_tested
    tpt_info["election_name"] = election_name
    tpt_info["output_directory"] = output_directory

    data = load_json_file(json_file_path)
    report_status = False
    if data:
        assessment_id, tpt_info["payloads_meta"], payloads_list = parse_json(data)
        if (
            bool(tpt_info["payloads_meta"]) is not False
            and bool(payloads_list) is not False
        ):
            tpt_info["assessment_id"] = assessment_id
            logging.debug(tpt_info)
            logging.debug(payloads_list)
            report_gen(tpt_info, payloads_list)
            report_status = True

    return report_status


def main() -> None:
    """Load JSON File from supplied argument."""
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
            "--output-dir": Use(str, error="--output-dir must be a string."),
            # Issue #36 - Validate DOMAIN_TESTED argument inputs
            # TODO: Provide input validation for DOMAIN_TESTED.
            "DOMAIN_TESTED": Use(str, error="DOMAIN_TESTED must be a string."),
            "ELECTION_NAME": Use(str, error="ELECTION_NAME must be a string."),
            "JSON_FILE_PATH": Use(str, error="JSON_FILE_PATH must be a string."),
        }
    )

    try:
        validated_args: Dict[str, Any] = schema.validate(args)
        validators.domain(validated_args["DOMAIN_TESTED"])

    except SchemaError as err:
        # Exit because one or more of the arguments were invalid
        print(err, file=sys.stderr)
        sys.exit(1)
    except ValueError as err:
        # Exit due to invalid value supplied
        print(err, file=sys.stderr)
        sys.exit(2)

    # Assign validated arguments to variables
    domain_tested: str = validated_args["DOMAIN_TESTED"]
    election_name: str = validated_args["ELECTION_NAME"]
    json_file_path: str = validated_args["JSON_FILE_PATH"]
    log_level: str = validated_args["--log-level"]
    output_directory: str = validated_args["--output-dir"]

    # Set up logging
    logging.basicConfig(
        datefmt="%m/%d/%Y %I:%M:%S",
        filemode="a",
        filename=LOGGING_FILE,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=log_level.upper(),
    )

    LOGGER.info("Loading TPT Report, Version : %s", __version__)

    # Check if output directory exists and create if needed
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    if generate_reports(election_name, domain_tested, output_directory, json_file_path):
        LOGGER.info(
            "TPT report for %s - %s was generated successfully in %s.",
            election_name,
            domain_tested,
            output_directory,
        )

    # Stop logging and clean up
    logging.shutdown()
