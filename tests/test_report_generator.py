"""Tests for report_generator."""

# Standard Python Libraries
from datetime import datetime
import json
from unittest import TestCase
from unittest.mock import patch

# Third-Party Libraries
import pandas as pd
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Table

# cisagov Libraries
from tpt_reports import report_generator

TEST_JSON_FILE = "tests/data/test.json"


@pytest.fixture
def test_payloads_dataframe():
    """Define a fixture for the payloads DataFrame."""
    with open(TEST_JSON_FILE, encoding="utf-8") as file:
        data = json.load(file)
        return pd.DataFrame.from_dict(data["phishing_assessment"]["payloads"])


@pytest.fixture
def test_dictionary():
    """Define a fixture for the test JSON dictionary."""
    with open(TEST_JSON_FILE, encoding="utf-8") as file:
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
    """Validate that an instance of MyDocTemplate is generated."""
    output_file_path = (
        f"tests/data/TPT_Report_{datetime.today().strftime('%Y-%m-%d')}_test.pdf"
    )
    # Patch the MyDocTemplate class with a MagicMock
    with patch("tpt_reports.report_generator.MyDocTemplate") as MockMyDocTemplate:
        # Create a MagicMock instance and set attributes
        mock_doc_instance = MockMyDocTemplate.return_value
        mock_doc_instance.filename = output_file_path
        mock_doc_instance.pagesize = letter
        # Call the report_gen function, which now uses the mocked MyDocTemplate
        result = report_generator.report_gen(
            test_dictionary["tpt_info"], test_dictionary["payloads_clean"]
        )
        # Check that result is an instance of MyDocTemplate
        MockMyDocTemplate.assert_called_once()
        # Validate the file name output of result
        assert result.filename == output_file_path
        # Validate the page size of result
        assert result.pagesize == (612.0, 792.0)


@patch("tpt_reports.report_generator.utils.ImageReader")
@patch("tpt_reports.report_generator.Image")
class TestGetImage(TestCase):
    """Tests for the get_image function."""

    def test_get_image_invalid_params(self, mock_image, mock_image_reader):
        """Test that get_image raises an exception when given invalid arguments."""
        # Setup test data
        bad_path = 1
        bad_width = "not a number"

        # Assert that a TypeError is raised
        with self.assertRaises(TypeError):
            report_generator.get_image(path=bad_path, width=bad_width)

    def test_get_image_returns_image(self, mock_image, mock_image_reader):
        """Test that the get_image function returns an Image object."""
        # Setup test data
        path = "test_path"
        width = 72.0

        # Mock the getSize method of the ImageReader class (width, height)
        mock_image_reader().getSize.return_value = (50, 100)

        # Expected aspect value is 2.0 based on getSize (height / width)
        # Set the expected height based on (getSize height * aspect value)
        expected_height = 144.0

        # Run the get_image function with test data
        result = report_generator.get_image(path=path, width=width)

        # Confirm Image() called with expected args and height calculated
        mock_image.assert_called_once_with(path, width=width, height=expected_height)

        # Confirm return value is an Image object
        assert result == mock_image.return_value
