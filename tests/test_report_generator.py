#!/usr/bin/env pytest -vs
"""Tests for report_generator."""

# Standard Python Libraries

# Third-Party Libraries
import pytest

# cisagov Libraries
import tpt_reports

test_tpt_info = {
    "assessment_id": "test",
    "domain_tested": "cisa.gov",
    "election_name": "test",
    "output_directory": "./test_output",
    "payloads_meta": {
        "border_blocked": 1,
        "border_not_blocked": 1,
        "host_blocked": 1,
        "host_not_blocked": 1,
        "num_payloads": 4,
        "payloads_blocked": 2,
        "payloads_not_blocked": 2,
    },
}

test_payloads_list = [
    {
        "border_protection": "Blocked",
        "C2_Protocol": "test_protocol",
        "host_protection": "Not blocked",
        "Payload": "test_payload_1",
    },
    {
        "border_protection": "Not blocked",
        "C2_Protocol": "test_protocol",
        "host_protection": "Blocked",
        "Payload": "test_payload_2",
    },
]


def test_generate_reports():
    """Validate report generation."""
    result = tpt_reports.tpt_reports.report_gen(test_tpt_info, test_payloads_list)
    assert isinstance(
        result, tpt_reports.report_generator.MyDocTemplate
    ), "generate_reports did not return an object of type MyDocTemplate"


def test_generate_reports_null_arguments():
    """Test report_generation with null arguments provided."""
    with pytest.raises(TypeError) as excinfo:
        tpt_reports.tpt_reports.report_gen(None, None)
    assert isinstance(
        excinfo.value, TypeError
    ), "report_gen() did not correctly handle a NoneType argument."
