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

# define sources of version strings
RELEASE_TAG = os.getenv("RELEASE_TAG")
PROJECT_VERSION = tpt_reports.__version__
TEST_JSON_FILE = "tests/data/test.json"
TEST_BAD_JSON_FILE = "tests/data/bad_file.json"
DEFAULT_OUTPUT_DIRECTORY = "~/"


@patch("tpt_reports.tpt_reports.generate_reports")
def test_stdout_version(mock_generate_reports, capsys):
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
@patch("tpt_reports.tpt_reports.generate_reports")
def test_log_levels(mock_generate_reports, level):
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
            TEST_JSON_FILE,
            "--output-dir=./test_output",
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


@patch("tpt_reports.tpt_reports.generate_reports")
def test_bad_log_level(mock_generate_reports):
    """Validate bad log-level argument returns error."""
    with patch.object(
        sys,
        "argv",
        ["bogus", "--log-level=emergency", "test", "test", "test", TEST_JSON_FILE],
    ):
        return_code = None
        try:
            tpt_reports.tpt_reports.main()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
        assert return_code == 1, "main() should exit with error return code 1"


@patch("tpt_reports.tpt_reports.generate_reports")
def test_domain_validation(mock_generate_reports):
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
            TEST_JSON_FILE,
            "--output-dir=./test_output",
        ],
    ):
        return_code = None
        try:
            tpt_reports.tpt_reports.main()
        except SystemExit as sys_exit:
            return_code = sys_exit.code
            assert return_code == 2, "main() should return with error return code 2"


@patch("tpt_reports.tpt_reports.report_gen")
def test_generate_reports(mock_report_gen):
    """Validate functionality for generate_reports()."""
    mock_report_gen.return_value = True
    return_val = tpt_reports.tpt_reports.generate_reports(
        "test", "test", "cisa.gov", "./test_output", TEST_JSON_FILE
    )
    assert return_val is True, "generate_reports() failed to generate a report."


@patch("tpt_reports.tpt_reports.report_gen")
def test_generate_reports_bad_file_name(mock_report_gen):
    """Validate functionality of generate_reports() when a bad filename is provided."""
    mock_report_gen.return_value = False
    return_val = tpt_reports.tpt_reports.generate_reports(
        "test", "test", "cisa.gov", "./test_output", "nonexistent_file.json"
    )
    assert (
        return_val is False
    ), "generate_reports() returned a boolean True when a bad filename was provided."


@patch("tpt_reports.tpt_reports.report_gen")
def test_generate_reports_bad_file_data(mock_report_gen):
    """Validate functionality of generate_reports() when a bad data is loaded from file."""
    mock_report_gen.return_value = False
    return_val = tpt_reports.tpt_reports.generate_reports(
        "test", "test", "cisa.gov", "./test_output", TEST_BAD_JSON_FILE
    )
    assert (
        return_val is False
    ), "generate_reports() returned a boolean True when a bad data was provided."


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


@patch("tpt_reports.tpt_reports.generate_reports")
def test_no_output_directory(mock_generate_reports):
    """Validate that no output directory argument uses default."""
    patched_args = [
        "bogus",
        "--log-level=info",
        "test",
        "test",
        "test",
        TEST_JSON_FILE,
    ]

    # Patch usage arguments
    with patch.object(sys, "argv", patched_args):
        # Set mock return value
        mock_generate_reports.return_value = True

        # Call tpt_reports.main entry point function
        result = tpt_reports.tpt_reports.main()
        assert result is None

        # Confirm generate_reports was called once with expected arguments
        expected_call_args = (
            "test",
            "test",
            "test",
            DEFAULT_OUTPUT_DIRECTORY,
            TEST_JSON_FILE,
        )
        assert mock_generate_reports.call_count == 1
        assert mock_generate_reports.call_args[0] == expected_call_args


@patch("tpt_reports.tpt_reports.generate_reports")
def test_with_output_directory(mock_generate_reports):
    """Validate that when output directory is passed it overrides default."""
    patched_args = [
        "bogus",
        "--log-level=info",
        "test",
        "test",
        "test",
        TEST_JSON_FILE,
        "--output-dir=./",
    ]

    # Patch usage arguments
    with patch.object(sys, "argv", patched_args):
        # Set mock return value
        mock_generate_reports.return_value = True

        # Call tpt_reports.main entry poifunction
        result = tpt_reports.tpt_reports.main()
        assert result is None

        # Confirm generate_reports was called with expected parameters
        expected_call_args = ("test", "test", "test", "./", TEST_JSON_FILE)
        assert mock_generate_reports.call_count == 1
        assert mock_generate_reports.call_args[0] == expected_call_args
