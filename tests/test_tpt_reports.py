#!/usr/bin/env pytest -vs
"""Tests for tpt-reports."""

# Standard Python Libraries
import logging
import os
import sys
from unittest.mock import patch

# Third-Party Libraries
import pytest

# cisagov Libraries
import tpt_reports

log_levels = (
    "debug",
    "info",
    "warning",
    "error",
    "critical",
)
test_file = "./tests/data/test.json"
bad_file = "./tests/data/bad_file.json"
bad_data = "./tests/data/bad_data.json"

# define sources of version strings
RELEASE_TAG = os.getenv("RELEASE_TAG")
PROJECT_VERSION = tpt_reports.__version__
TEST_JSON_FILE = "tests/data/test.json"


def test_stdout_version(capsys):
    """Verify that version string sent to stdout agrees with the module version."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            tpt_reports.tpt_reports.main()
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


def test_running_as_module(capsys):
    """Verify that the __main__.py file loads correctly."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            # F401 is a "Module imported but unused" warning. This import
            # emulates how this project would be run as a module. The only thing
            # being done by __main__ is importing the main entrypoint of the
            # package and running it, so there is nothing to use from this
            # import. As a result, we can safely ignore this warning.
            # cisagov Libraries
            import tpt_reports.__main__  # noqa: F401
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


@pytest.mark.skipif(
    RELEASE_TAG in [None, ""], reason="this is not a release (RELEASE_TAG not set)"
)
def test_release_version():
    """Verify that release tag version agrees with the module version."""
    assert (
        RELEASE_TAG == f"v{PROJECT_VERSION}"
    ), "RELEASE_TAG does not match the project version"


@pytest.mark.parametrize("level", log_levels)
def test_log_levels(level):
    """Validate commandline log-level arguments."""
    with patch.object(
        sys,
        "argv",
        [
            "bogus",
            f"--log-level={level}",
            "test",
            "test",
            "cisa.gov",
            "test.json",
            "./test_output",
        ],
    ):
        with patch.object(logging.root, "handlers", []):
            assert (
                logging.root.hasHandlers() is False
            ), "root logger should not have handlers yet"
            return_code = None
            try:
                tpt_reports.tpt_reports.main()
            except SystemExit as sys_exit:
                return_code = sys_exit.code
            assert return_code is None, "main() should return success"
            assert (
                logging.root.hasHandlers() is True
            ), "root logger should now have a handler"
            assert (
                logging.getLevelName(logging.root.getEffectiveLevel()) == level.upper()
            ), f"root logger level should be set to {level.upper()}"
            assert return_code is None, "main() should return success"


def test_bad_log_level():
    """Validate bad log-level argument returns error."""
    with patch.object(
        sys,
        "argv",
        ["bogus", "--log-level=emergency", "test", "test", "test", "test", "test"],
    ):
        return_code = None
        try:
            tpt_reports.tpt_reports.main()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
        assert return_code == 1, "main() should exit with error return code 1"


def test_domain_validation():
    """Validate invalid domain arguments."""
    with patch.object(
        sys,
        "argv",
        [
            "bogus",
            "--log-level=debug",
            "test",
            "test",
            "cisa",
            "test.json",
            "./test_output",
        ],
    ):
        return_code = None
        try:
            tpt_reports.tpt_reports.main()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
            assert return_code == 2, "main() should return with error return code 2"


def test_generate_reports():
    """Validate functionality for generate_reports()."""
    return_val = tpt_reports.tpt_reports.generate_reports(
        "test", "test", "cisa.gov", "./test_output", test_file
    )
    assert return_val is True, "generate_reports() failed to generate a report."


def test_generate_reports_bad_filename():
    """Validate that generate_reports returns False when it cannot open the json file."""
    return_val = tpt_reports.tpt_reports.generate_reports(
        "test", "test", "cisa.gov", "./test_output", bad_file
    )
    assert (
        return_val is False
    ), f"generate_reports() tried to open a non-existent file: {bad_file}."


def test_generate_reports_bad_key_values():
    """Validate that generate_reports() will raise KeyError when not receiving an expected key value."""
    with pytest.raises(KeyError) as excinfo:
        return_val = tpt_reports.tpt_reports.generate_reports(
            "test", "test", "cisa.gov", "./test_output", bad_data
        )
        assert (
            return_val is True
        ), f"generate_reports() failed to open data file: {bad_data}."
    assert isinstance(
        excinfo.value, KeyError
    ), "generate_reports() did not raise KeyError due to not receiving an expected key value."


def test_generate_reports_bad_types():
    """Validate that generate_reports() will raise TypeError when receiving NoneType values."""
    with pytest.raises(TypeError) as excinfo:
        tpt_reports.tpt_reports.generate_reports(None, None, None, None, None)
    assert isinstance(
        excinfo.value, TypeError
    ), "generate_reports() did not raise TypeError due to receiving a NoneType value."


def test_load_json_file():
    """Validate file loads correctly."""
    assert tpt_reports.tpt_reports.load_json_file(TEST_JSON_FILE) is not None
    assert (
        tpt_reports.tpt_reports.load_json_file("tests/data/does_not_exist.json") is None
    )


def test_parse_json():
    """Validate parse_json() functionality."""
    payloads_list = []
    payloads_meta = {}
    payload_list_test = [
        {
            "Border Protection": "Not Blocked",
            "C2 Protocol": "c2_1",
            "Host Protection": "Blocked",
            "Payload": "Test payload",
        }
    ]
    data = tpt_reports.tpt_reports.load_json_file(TEST_JSON_FILE)
    payloads_meta, payloads_list = tpt_reports.tpt_reports.parse_json(data)

    assert payloads_list == payload_list_test

    assert payloads_meta["border_blocked"] == 0
    assert payloads_meta["border_not_blocked"] == 1
    assert payloads_meta["host_blocked"] == 1
    assert payloads_meta["host_not_blocked"] == 0
    assert payloads_meta["num_payloads"] == 1
    assert payloads_meta["payloads_blocked"] == 1
    assert payloads_meta["payloads_not_blocked"] == 1
