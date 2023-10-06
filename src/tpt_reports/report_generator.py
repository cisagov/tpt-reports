"""Generate a TPT report using a passed data dictionary."""

# Standard Python Libraries
from datetime import datetime
import os
import secrets

# Third-Party Libraries
import numpy as np
import pandas as pd
from reportlab.lib import utils
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.doctemplate import (
    BaseDocTemplate,
    NextPageTemplate,
    PageTemplate,
)
from reportlab.platypus.frames import Frame

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
REPORT_KEY_LENGTH = 17
TODAYS_DATE_FOR_FILE_NAME = datetime.today().strftime("%Y-%m-%d")
TODAYS_DATE_FOR_REPORT_CONTENT = datetime.today().strftime("%m/%d/%Y")

# Set fonts to be used in the PDF
pdfmetrics.registerFont(
    TTFont("Franklin_Gothic_Book", f"{BASE_DIR}/fonts/FranklinGothicBook.ttf")
)

pdfmetrics.registerFont(
    TTFont(
        "Franklin_Gothic_Medium_Regular",
        f"{BASE_DIR}/fonts/FranklinGothicMediumRegular.ttf",
    )
)

# Set page size
defaultPageSize = letter
PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]


class MyDocTemplate(BaseDocTemplate):
    """Extend the BaseDocTemplate to adjust Template."""

    def __init__(self, filename, report_key, **kw):
        """Initialize MyDocTemplate."""
        # Set report_key as an environment variable
        os.environ["TPT_REPORT_KEY"] = report_key
        # allowSplitting must be set prior to BaseDocTemplate per docs
        self.allowSplitting = 0
        # Initialize document
        BaseDocTemplate.__init__(self, filename, **kw)
        # encrypt must be called after initialization per docs
        self.encrypt = report_key
        self.pagesize = defaultPageSize


class ConditionalSpacer(Spacer):
    """Create a Conditional Spacer class."""

    def wrap(self, availWidth, availHeight):
        """Create a spacer if there is space on the page to do so."""
        height = min(self.height, availHeight - 1e-8)
        return (availWidth, height)


def get_image(path, width=1 * inch):
    """Read in an image and scale it based on the width argument."""
    # Validate arguments
    if not isinstance(path, str) or not isinstance(width, (int, float)):
        # Raise TypeError if arguments are not the expected type
        raise TypeError(
            f"'get_image' expects path=(str) and width=(int/float). \
            Got path={type(path)}, width={type(width)}."
        )

    # Read in image and get dimensions
    img = utils.ImageReader(path)
    img_width, img_height = img.getSize()

    # Calculate aspect ratio
    aspect = img_height / float(img_width)

    # Return an Image object with the calculated height
    return Image(path, width=width, height=(width * aspect))


def format_table(df, header_style, column_widths, column_style_list):
    """Read in a dataframe and convert it to a table and format it with a provided style list."""
    header_row = [
        [Paragraph(str(cell), header_style) for cell in row] for row in [df.columns]
    ]
    data = []
    for row in np.array(df).tolist():
        current_cell = 0
        current_row = []
        for cell in row:
            if column_style_list[current_cell] is not None:
                # Remove emojis from content because the report generator can't display them
                cell = Paragraph(str(cell), column_style_list[current_cell])

            current_row.append(cell)
            current_cell += 1
        data.append(current_row)

    data = header_row + data

    table = Table(
        data,
        colWidths=column_widths,
        rowHeights=None,
        style=None,
        splitByRow=1,
        repeatRows=1,
        repeatCols=0,
        rowSplitRange=(2, -1),
        spaceBefore=None,
        spaceAfter=None,
        cornerRadii=None,
    )

    style = TableStyle(
        [
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
            ("INNERGRID", (0, 0), (-1, -1), 1, "white"),
            ("TEXTFONT", (0, 1), (-1, -1), "Franklin_Gothic_Book"),
            ("FONTSIZE", (0, 1), (-1, -1), 12),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [HexColor("#FFFFFF"), HexColor("#DEEBF7")],
            ),
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1d5288")),
            ("LINEBELOW", (0, -1), (-1, -1), 1.5, HexColor("#1d5288")),
        ]
    )
    for (
        row,
        values,
    ) in enumerate(data):
        for column, value in enumerate(values):
            if value == "Not Blocked":
                style.add("TEXTCOLOR", (column, row), (column, row), "red")
            if value == "Blocked":
                style.add("TEXTCOLOR", (column, row), (column, row), "green")
    table.setStyle(style)

    if len(df) == 0:
        label = Paragraph(
            "No Data to Report",
            ParagraphStyle(
                name="centered",
                fontName="Franklin_Gothic_Medium_Regular",
                textColor=HexColor("#a7a7a6"),
                fontSize=16,
                leading=16,
                alignment=1,
                spaceAfter=10,
                spaceBefore=10,
            ),
        )
        table = KeepTogether([table, label])
    return table


# Issue #26 - test report_gen()
# TODO: Add unit tests for following logic and remove this comment.
def report_gen(tpt_info, payloads_list):
    """Generate a TPT report with data passed in the data dictionary."""

    def title_page(canvas, doc):
        """Build static elements of the cover page."""
        canvas.saveState()
        canvas.drawInlineImage(
            f"{BASE_DIR}/assets/cisa.png", 45, 705, width=65, height=65
        )
        canvas.setStrokeColor(HexColor("#003e67"))
        canvas.setLineWidth(1.5)
        canvas.line(77.5, 2 * inch, PAGE_WIDTH - 1.075 * inch, 2 * inch)
        canvas.setFillColor(HexColor("#003e67"))
        canvas.setFont("Franklin_Gothic_Medium_Regular", 16)
        canvas.drawString(
            1.08 * inch,
            1.5 * inch,
            f"""Publication: {TODAYS_DATE_FOR_REPORT_CONTENT}""",
        )
        canvas.drawString(
            1.08 * inch,
            1.2 * inch,
            "Cybersecurity and Infrastructure Security Agency",
        )
        canvas.restoreState()

    def content_page(canvas, doc):
        """Build static elements of the summary page."""
        canvas.saveState()
        canvas.setFont("Franklin_Gothic_Book", 13)
        canvas.restoreState()
        # Add footer
        canvas.setFillColor("#005288")
        canvas.drawString(
            inch,
            0.75 * inch,
            f"CISA | DEFEND TODAY, SECURE TOMORROW {doc.page}",
        )

    # Generate report key for encryption
    report_key = secrets.token_hex(REPORT_KEY_LENGTH)[:REPORT_KEY_LENGTH]

    # Load the doc and create the frames for page structures to be dynamically filled
    tpt_report_filename = (
        f"TPT_Report_{TODAYS_DATE_FOR_FILE_NAME}_{tpt_info['assessment_id']}.pdf"
    )
    doc = MyDocTemplate(
        f"{tpt_info['output_directory']}/{tpt_report_filename}", report_key
    )

    # frame: x, y, width, height
    title_frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        PAGE_WIDTH - (2 * inch),
        PAGE_HEIGHT - (2.4 * inch),
        id="normal",
        showBoundary=0,
    )
    content_frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        PAGE_WIDTH - (2 * inch),
        PAGE_HEIGHT - (2 * inch),
        id="normal",
        showBoundary=0,
    )
    # Add different Page templates for dynamic filling
    doc.addPageTemplates(
        [
            PageTemplate(id="title_page", frames=title_frame, onPage=title_page),
            PageTemplate(id="content_page", frames=content_frame, onPage=content_page),
        ]
    )
    # Generate the list to fill all the dynamic content streamed through the report
    Story = []
    paragraph_style = ParagraphStyle
    image_text = paragraph_style(
        name="image_text",
        fontName="Franklin_Gothic_Medium_Regular",
        fontSize=8,
        leading=16,
        alignment=1,
        spaceAfter=10,
        spaceBefore=10,
        textColor=HexColor("#003e67"),
    )
    cover_heading = paragraph_style(
        fontName="Franklin_Gothic_Medium_Regular",
        name="Heading1",
        fontSize=28,
        leading=48,
        spaceBefore=10,
        textColor=HexColor("#003e67"),
    )
    h2 = paragraph_style(
        name="Heading2",
        fontName="Franklin_Gothic_Medium_Regular",
        fontSize=14,
        leading=10,
        textColor=HexColor("#003e67"),
        spaceAfter=12,
    )
    body = paragraph_style(
        name="body",
        leading=14,
        fontName="Franklin_Gothic_Book",
        fontSize=12,
    )
    table = paragraph_style(
        name="table",
        fontName="Franklin_Gothic_Medium_Regular",
        fontSize=18,
        alignment=1,
        spaceAfter=14,
    )
    table_header = paragraph_style(
        name="table_header",
        fontName="Franklin_Gothic_Medium_Regular",
        fontSize=12,
        leading=20,
        alignment=1,
        spaceAfter=30,
        textColor=HexColor("#FFFFFF"),
    )

    # Create dynamic content; repeated and random elements used in the report
    point12_spacer = ConditionalSpacer(1, 12)
    point24_spacer = ConditionalSpacer(1, 24)
    point30_spacer = Spacer(1, 30)

    # Appends sequentially with the frames created above i.e. title_page then content_page
    Story.append(get_image(f"{BASE_DIR}/assets/TitlePage.png", width=9 * inch))
    Story.append(point24_spacer)
    Story.append(
        Paragraph(
            f"""Technical Phishing Test (TPT) Report - {tpt_info["election_name"]}""",
            cover_heading,
        )
    )
    Story.append(point24_spacer)
    Story.append(NextPageTemplate("content_page"))
    Story.append(PageBreak())
    Story.append(Paragraph("TPT Report", table))
    Story.append(
        format_table(
            pd.DataFrame.from_dict(
                {
                    "Report Date": TODAYS_DATE_FOR_REPORT_CONTENT,
                    "Stakeholder Name": [tpt_info["election_name"]],
                    "Domain Tested": [tpt_info["domain_tested"]],
                    "Assessment ID": [tpt_info["assessment_id"]],
                }
            ),
            table_header,
            [1.2 * inch, 2.2 * inch, 1.6 * inch, 1.3 * inch],
            [None, body, body, body],
        )
    )
    Story.append(point30_spacer)
    Story.append(
        format_table(
            pd.DataFrame.from_dict(
                {
                    "Security Reference (FCRM, NIST, ETC.)": [
                        "NIST 800 - 61 - Revision 2 - Computer Incident Security Handling"
                    ],
                    "Release Date": ["06/30/2023"],
                }
            ),
            table_header,
            [5 * inch, 1.3 * inch],
            [body, None],
        )
    )
    Story.append(point30_spacer)
    Story.append(Paragraph("DESCRIPTION", h2))
    Story.append(
        Paragraph(
            """For a phishing attack (Figure 1) to be successful, a malicious
            email must pass through the network border, evade host-based intrusion
            detection tools, and trick the recipient into taking action. Most
            common phishing attacks can be rebuffed by good border and host-level
            automated protections. Inadequate border and host-level automated
            protections increase the susceptibility of organizations and networks
            to the execution of malicious payloads.""",
            body,
        )
    )
    Story.append(point12_spacer)
    Story.append(get_image(f"{BASE_DIR}/assets/Picture2.png", width=4 * inch))
    Story.append(
        Paragraph("Figure 1: Layered Defense Model for Email Security ", image_text)
    )
    Story.append(point12_spacer)
    Story.append(Paragraph("PHISHING CONTROLS ASSESSMENT", h2))
    Story.append(
        Paragraph(
            """With the cooperation of a complicit user, a simulated phishing
            attack scenario was performed, in which the CISA team attempted to
            execute a variety of simulated malicious payloads on the user's
            workstation. This simulated attack scenario evaluated technical
            security controls in their ability to identify, alert, and prevent
            such attack vectors.""",
            body,
        )
    )
    Story.append(point12_spacer)
    Story.append(
        Paragraph(
            f"""The initial email containing a link to the malicious payloads was
            able to circumvent border protections and reach the complicit user's
            inbox (in spam). Of the {tpt_info["payloads_meta"]["num_payloads"]} different
            payloads tested, {tpt_info["payloads_meta"]["payloads_not_blocked"]}
            payloads executed and connected to the CISA team's
            command-and-control C2 server (Not Blocked).""",
            body,
        )
    )
    Story.append(PageBreak())

    # Generate a table using a tabframe passed to my format_table function
    Story.append(
        format_table(
            pd.DataFrame.from_records(payloads_list),
            table_header,
            [3.2 * inch, 0.9 * inch, 1.1 * inch, 1.1 * inch],
            [body, None, None, None],
        )
    )
    Story.append(Paragraph("Figure 2: Payload testing results", image_text))
    Story.append(point12_spacer)
    Story.append(Paragraph("CONCLUSION / RECOMMENDED MITIGATION", h2))
    Story.append(
        Paragraph(
            """Regularly analyze border and host-level protections, including
            spam-filtering capabilities, to ensure their continued effectiveness
            in blocking the delivery and execution of malware. These tools must
            be kept up-to-date.""",
            body,
        )
    )

    doc.multiBuild(Story)
    print(f"REPORT KEY: {os.environ.get('TPT_REPORT_KEY')}")
    return doc
