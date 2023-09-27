"""Tests for report_generator."""

# Standard Python Libraries
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
def test_dataframe():
    """Define a fixture for a sample DataFrame."""
    with open("tests/data/test.json", encoding="utf-8") as file:
        data = json.load(file)
        return pd.DataFrame.from_dict(data["payloads"])


def test_format_table(test_dataframe):
    """Verify that format_table works correctly."""
    # Define test parameters
    header_style = ParagraphStyle(name="test_table", fontSize=12)
    body = ParagraphStyle(name="body", leading=14, fontSize=12)
    column_widths = [inch, inch, inch, inch, inch, inch, inch, inch]
    column_style_list = [body, body, body, body, body, body, body, body]

    # Call the format_table function with test data
    table = report_generator.format_table(
        test_dataframe, header_style, column_widths, column_style_list
    )

    # Perform assertions to check the table's properties
    assert isinstance(test_dataframe, pd.DataFrame)
    assert isinstance(table, Table)

    # Validate the number of rows and columns in the table
    # The table value includes the header row so + 1 is needed
    assert table._nrows == len(test_dataframe) + 1
    assert table._ncols == len(test_dataframe.columns)

    # Validate the attribute and content of the first row
    assert table._cellvalues[0][0].text == "border_protection"
    assert table._cellvalues[1][0].text == "N"

    # Validate the attribute and content of the last row
    assert table._cellvalues[0][7].text == "payload_description"
    assert table._cellvalues[1][7].text == "Test payload"
