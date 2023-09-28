"""Tests for report_generator."""

# Standard Python Libraries
from datetime import datetime
import json

# Third-Party Libraries
import pandas as pd
import pytest
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Table

# cisagov Libraries
from tpt_reports import report_generator


@pytest.fixture
def test_payloads_dataframe():
    """Define a fixture for the payloads DataFrame."""
    with open("tests/data/test.json", encoding="utf-8") as file:
        data = json.load(file)
        return pd.DataFrame.from_dict(data["payloads"])


@pytest.fixture
def test_dictionary():
    """Define a fixture for the test json dictionary."""
    with open("tests/data/test.json", encoding="utf-8") as file:
        return json.load(file)


def test_format_table(test_payloads_dataframe):
    """Verify that format_table works correctly."""
    # Define test parameters
    header_style = ParagraphStyle(name="test_table", fontSize=12)
    body = ParagraphStyle(name="body", leading=14, fontSize=12)
    column_widths = [inch, inch, inch, inch, inch, inch, inch, inch]
    column_style_list = [body, body, body, body, body, body, body, body]

    # Call the format_table function with test data
    table = report_generator.format_table(
        test_payloads_dataframe, header_style, column_widths, column_style_list
    )

    # Perform assertions to check the table's properties
    assert isinstance(test_payloads_dataframe, pd.DataFrame)
    assert isinstance(table, Table)

    # Validate the number of rows and columns in the table
    # The table value includes the header row so + 1 is needed
    assert table._nrows == len(test_payloads_dataframe) + 1
    assert table._ncols == len(test_payloads_dataframe.columns)

    # Validate the attribute and content of the first row
    assert table._cellvalues[0][0].text == "border_protection"
    assert table._cellvalues[1][0].text == "N"

    # Validate the attribute and content of the last row
    assert table._cellvalues[0][7].text == "payload_description"
    assert table._cellvalues[1][7].text == "Test payload"


def test_report_gen(test_dictionary):
    """Validate report document is generated."""
    result = report_generator.report_gen(
        test_dictionary["tpt_info"], test_dictionary["payloads_clean"]
    )
    todays_date = datetime.today().strftime("%Y-%m-%d")
    file_output = f"./test_output/TPT_Report_{todays_date}_test.pdf"

    # Check that result is an instance of MyDocTemplate
    assert isinstance(result, report_generator.MyDocTemplate)

    # Validate the file name output of result
    assert result.filename == file_output

    # Validate the page size of result
    assert result.pagesize == (612.0, 792.0)
