import os
from html import escape

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import LOGO_FILE, PDF_DIR


FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
for font_path in [
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
]:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("EWUFont", font_path))
            FONT = "EWUFont"
            FONT_BOLD = "EWUFont"
            break
        except Exception:
            pass


def _p(value, style):
    return Paragraph(escape(str(value or "")), style)


def _image(path, width, height):
    if path and os.path.exists(path):
        try:
            return RLImage(path, width=width, height=height)
        except Exception:
            return None
    return None


def _styles():
    base = getSampleStyleSheet()
    body = ParagraphStyle("EWUBody", parent=base["BodyText"], fontName=FONT, fontSize=9, leading=12)
    title = ParagraphStyle("EWUTitle", parent=base["Title"], fontName=FONT_BOLD, fontSize=20, leading=24, textColor=colors.HexColor("#102E46"))
    small = ParagraphStyle("EWUSmall", parent=body, fontSize=8, textColor=colors.HexColor("#4B5563"))
    return body, title, small


def _table(rows, body):
    prepared = [[_p(left, body), _p(right, body)] for left, right in rows]
    table = Table(prepared, colWidths=[5.0 * cm, 11.3 * cm], repeatRows=0)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#102E46")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D7E3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), FONT),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _header(story, title_text, eid, title, body):
    logo = _image(LOGO_FILE, 2.0 * cm, 2.0 * cm)
    if logo:
        story.append(logo)
    story.append(Paragraph(title_text, title))
    story.append(Paragraph(f"<b>EWU ID:</b> {escape(eid)}", body))
    story.append(Spacer(1, 8))


def _qr(eid):
    os.makedirs(PDF_DIR, exist_ok=True)
    path = os.path.join(PDF_DIR, f"{eid}_qr.png")
    qrcode.make(eid).save(path)
    return path


def make_candidate_pdf(data, photo_path=None):
    os.makedirs(PDF_DIR, exist_ok=True)
    eid = data.get("EWU_ID", "EWU")
    path = os.path.join(PDF_DIR, f"{eid}_candidate.pdf")
    body, title, small = _styles()
    story = []
    _header(story, "European Welders Union - Candidate Card", eid, title, body)

    photo = _image(photo_path or data.get("Photo"), 4.0 * cm, 4.0 * cm)
    qr = _image(_qr(eid), 2.0 * cm, 2.0 * cm)
    media = [x for x in [photo, qr] if x]
    if media:
        story.append(Table([media], hAlign="LEFT"))
        story.append(Spacer(1, 8))

    full_name = data.get("Full_Name") or " ".join([data.get("First_Name", ""), data.get("Last_Name", "")]).strip()
    rows = [
        ["Full name", full_name],
        ["Date of birth", data.get("Date_of_birth", "")],
        ["Nationality", data.get("Nationality", "")],
        ["Current location", f"{data.get('Current_country', '')} {data.get('Current_city', '')}".strip()],
        ["Profession", data.get("Profession", "")],
        ["Experience", data.get("Experience", "")],
        ["Welding methods", data.get("Welding_methods", "")],
        ["Foreign experience", data.get("Foreign_experience", "")],
        ["Countries worked in", data.get("Countries_worked_in", "")],
        ["Languages", data.get("Language_skills", "")],
        ["Certificates", data.get("Certificates", "")],
        ["Certificate validity", data.get("Certificate_validity", "")],
        ["Documents", data.get("Documents", "")],
        ["Relocation readiness", data.get("Relocation_readiness", "")],
        ["Preferred countries", data.get("Preferred_countries", "")],
        ["Driving licence", data.get("Driving_Licence", "")],
        ["Driving categories", data.get("Driving_Categories", "")],
        ["Own vehicle", data.get("Own_Vehicle", "")],
        ["Contacts", " / ".join([x for x in [data.get("Phone", ""), data.get("WhatsApp", ""), data.get("Telegram", "")] if x])],
        ["AI Summary", data.get("AI_Summary", "")],
    ]
    story.append(_table(rows, body))
    story.append(Spacer(1, 10))
    story.append(Paragraph("EWU - professional community, coordination and worker support across Europe.", small))
    SimpleDocTemplate(path, pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm).build(story)
    return path


def make_vacancy_pdf(data, production_photos=None, accommodation_photos=None):
    os.makedirs(PDF_DIR, exist_ok=True)
    eid = data.get("EWU_ID", "EWU_EMP")
    path = os.path.join(PDF_DIR, f"{eid}_vacancy.pdf")
    body, title, small = _styles()
    story = []
    _header(story, "European Welders Union - Vacancy Card", eid, title, body)

    rows = [
        ["Company", data.get("Company", "")],
        ["Contact person", data.get("Contact_person", "")],
        ["Country", data.get("Country", "")],
        ["City", data.get("City", "")],
        ["Profession required", data.get("Vacancy", "")],
        ["Number of workers", data.get("Quantity", "")],
        ["Project description", data.get("Project_description", "")],
        ["Contract type", data.get("Contract_type", "")],
        ["Salary", data.get("Salary", "")],
        ["Working hours", data.get("Working_hours", "")],
        ["Shifts", data.get("Shifts", "")],
        ["Accommodation", data.get("Accommodation", "")],
        ["Transport", data.get("Transport", "")],
        ["Work clothing", data.get("Work_clothing", "")],
        ["Meals", data.get("Meals", "")],
        ["Starting date", data.get("Starting_date", "")],
        ["EWU contact", data.get("Phone", "")],
    ]
    story.append(_table(rows, body))
    photos = []
    for photo_path in (production_photos or [])[:3] + (accommodation_photos or [])[:3]:
        img = _image(photo_path, 4.2 * cm, 3.2 * cm)
        if img:
            photos.append(img)
    if photos:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Production and accommodation photos", body))
        story.append(Table([photos[i:i + 3] for i in range(0, len(photos), 3)], hAlign="LEFT"))
    story.append(Spacer(1, 10))
    story.append(Paragraph("EWU - recruitment, coordination and industrial specialist support across Europe.", small))
    SimpleDocTemplate(path, pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm).build(story)
    return path


def make_pdf(data, photo_path=None):
    return make_candidate_pdf(data, photo_path)
