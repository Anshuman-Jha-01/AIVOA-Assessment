from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

doc = SimpleDocTemplate("Zenith_Life_Sciences_Complaint_CC-2026-00154.pdf", pagesize=letter,
                         topMargin=0.7*inch, bottomMargin=0.7*inch)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Zenith Life Sciences Pvt. Ltd.", styles["Title"]))
story.append(Paragraph("Customer Complaint Report", styles["Heading2"]))
story.append(Spacer(1, 10))
story.append(Paragraph("Complaint Reference: CC-2026-00154", styles["Normal"]))
story.append(Paragraph("Date Reported: 27 June 2026", styles["Normal"]))
story.append(Paragraph("Reported By: ABC Formulations Ltd. (Quality Department)", styles["Normal"]))
story.append(Spacer(1, 16))

data = [
    ["Field", "Details"],
    ["Product Name", "Metformin Hydrochloride API"],
    ["Product Strength/Grade", "IP/BP"],
    ["Batch / Lot Number", "MFH260712A"],
    ["Affected Quantity", "25 kg (1 HDPE Drum)"],
    ["Manufacturing Date", "25 June 2026"],
    ["Expiry Date", "Not Provided"],
    ["Originating Site Block", "Manufacturing"],
    ["Impacted Non-Product Material", "HDPE Drum"],
]
table = Table(data, colWidths=[2.3*inch, 3.7*inch])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5b4cf5")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7fb")]),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story.append(table)
story.append(Spacer(1, 18))

story.append(Paragraph("Issue Description", styles["Heading3"]))
story.append(Paragraph(
    "During incoming quality inspection at our facility, ABC Formulations Ltd. reported multiple "
    "dark foreign particles inside one sealed HDPE drum of Metformin Hydrochloride API. The drum "
    "had no visible external damage. Material has been quarantined pending investigation. Given "
    "this is an API input material, this is considered a high-priority issue requiring urgent review.",
    styles["Normal"]))
story.append(Spacer(1, 14))

story.append(Paragraph("Requested Action", styles["Heading3"]))
story.append(Paragraph(
    "Investigation into root cause of contamination, confirmation of quarantine status, and "
    "corrective action plan to prevent recurrence.",
    styles["Normal"]))

doc.build(story)
print("PDF created")
