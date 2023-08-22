"""tpt_reports is a report generation Python library and tool.

Usage:
  tpt-reports [--log-level=LEVEL] JSON_FILE_PATH

Options:
  -h --help                         Show this message.
  -l --log-level=LEVEL              If specified, then the log level will be set to
                                    the specified value.  Valid values are "debug", "info",
                                    "warning", "error", and "critical". [default: info]
Arguments:
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
LOGGING_FILE = "report_generator.log"


# Issue #6 - Create Unit Tests
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


def parse_json(data):
    """Parse JSON object for values to report."""
    payloads_list = []
    payloads_meta = {}
    num_payloads = 0
    host_blocked = 0
    host_not_blocked = 0
    border_blocked = 0
    border_not_blocked = 0
    try:
        if data:
            for payload in data["payloads"]:
                num_payloads += 1
                payload_data = {}
                payload_data["Payload"] = payload["payload_description"]
                payload_data["C2 Protocol"] = payload["c2_protocol "]

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

        payloads_meta["num_payloads"] = num_payloads
        payloads_meta["host_blocked"] = host_blocked
        payloads_meta["host_not_blocked"] = host_not_blocked
        payloads_meta["border_blocked"] = border_blocked
        payloads_meta["border_not_blocked"] = border_not_blocked
        payloads_meta["num_blocked"] = num_payloads
        payloads_not_blocked = border_not_blocked + host_not_blocked
        payloads_meta["payloads_not_blocked"] = payloads_not_blocked
        payloads_blocked = border_blocked + host_blocked
        payloads_meta["payloads_blocked"] = payloads_blocked

    except Exception as e:
        LOGGER.exception(str(e))
    return payloads_meta, payloads_list


def generate_reports(
    servicenow_id, election_name, domain_tested, output_directory, json_file_path
):
    """Process steps for generating report data."""
    tpt_info = {}
    tpt_info["servicenow_id"] = servicenow_id
    tpt_info["election_name"] = election_name
    tpt_info["report_date"] = date.today().strftime("%Y-%m-%d")
    tpt_info["domain_tested"] = domain_tested
    tpt_info["output_directory"] = output_directory
    data = get_json_file(json_file_path)
    if data:
        payloads_meta, payloads_list = parse_json(data)
        tpt_info["payloads_meta"] = payloads_meta
        logging.debug(tpt_info)
        logging.debug(payloads_list)
        report_gen(tpt_info, payloads_list)
    return True


# Issue #4 - Add ReportLab code and library
# TODO: Add in the ReportLab code, library, parsing logic and remove this comment.
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

    if load_json_file(json_file_path):
        LOGGER.info("JSON FILE loaded successfully.")

    # Stop logging and clean up
    logging.shutdown()
