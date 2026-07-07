"""
pdf_generator.py — Generate clean, invoice-style audit PDF reports using ReportLab.
"""

import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from config import PDF_DIR, SENDER_NAME, SENDER_EMAIL, SENDER_TITLE
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import io

logger = logging.getLogger(__name__)

# ── Invoice Color Palette ────────────────────────────────────────────────────
BLACK = colors.HexColor("#000000")
WHITE = colors.HexColor("#FFFFFF")
TEAL = colors.HexColor("#00A3A8")      # Main accent color (from image)
LIGHT_TEAL = colors.HexColor("#EAF5F5") # Table header background
GRAY_TEXT = colors.HexColor("#555555")
LIGHT_GRAY_LINE = colors.HexColor("#E0E0E0")

W, H = A4  # 595.27 x 841.89 points
MARGIN = 15 * mm


def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")


# ── Custom Styles ────────────────────────────────────────────────────────────
def get_styles():
    return {
        "invoice_title": ParagraphStyle("title", fontName="Helvetica", fontSize=32, textColor=TEAL, alignment=TA_LEFT, letterSpacing=2),
        "header_box_label": ParagraphStyle("h_box_l", fontName="Helvetica", fontSize=8, textColor=GRAY_TEXT, alignment=TA_LEFT),
        "header_box_value": ParagraphStyle("h_box_v", fontName="Helvetica-Bold", fontSize=8, textColor=BLACK, alignment=TA_LEFT),
        "details_heading": ParagraphStyle("d_head", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK, alignment=TA_LEFT),
        "details_body": ParagraphStyle("d_body", fontName="Helvetica", fontSize=8, leading=12, textColor=GRAY_TEXT, alignment=TA_LEFT),
        "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=9, textColor=BLACK, alignment=TA_CENTER),
        "th_left": ParagraphStyle("th_l", fontName="Helvetica-Bold", fontSize=9, textColor=BLACK, alignment=TA_LEFT),
        "td_num": ParagraphStyle("td_num", fontName="Helvetica-Bold", fontSize=9, textColor=BLACK, alignment=TA_CENTER),
        "td_main": ParagraphStyle("td_main", fontName="Helvetica", fontSize=9, leading=13, textColor=BLACK, alignment=TA_LEFT),
        "td_sub": ParagraphStyle("td_sub", fontName="Helvetica", fontSize=8, leading=11, textColor=GRAY_TEXT, alignment=TA_LEFT, spaceBefore=4),
        "td_center": ParagraphStyle("td_center", fontName="Helvetica", fontSize=9, textColor=BLACK, alignment=TA_CENTER),
        "note_head": ParagraphStyle("note_h", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK, alignment=TA_CENTER),
        "note_body": ParagraphStyle("note_b", fontName="Helvetica-Oblique", fontSize=8, textColor=GRAY_TEXT, alignment=TA_LEFT, leading=10),
    }

mk = lambda txt, style: Paragraph(txt, style)


# ── Top Header Section ───────────────────────────────────────────────────────
def build_header(story: list, audit: dict, styles: dict):
    # Left side: "CRO AUDIT" (Instead of INVOICE)
    title = mk("CRO AUDIT", styles["invoice_title"])

    # Right side: Box with Date, URL, Score
    date_str = datetime.now().strftime("%d/%m/%Y")
    score_str = f"{audit.get('overall_score', 0)}/100"
    
    right_box_data = [
        [mk("Date:", styles["header_box_label"]), mk(date_str, styles["header_box_value"])],
        [mk("Store:", styles["header_box_label"]), mk(sanitize_filename(audit.get("store_name", "Store")), styles["header_box_value"])],
        [mk("Score:", styles["header_box_label"]), mk(score_str, styles["header_box_value"])]
    ]
    
    box_table = Table(right_box_data, colWidths=[15*mm, 35*mm], rowHeights=[6*mm, 6*mm, 6*mm])
    box_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, BLACK),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2*mm),
    ]))

    # Main layout table for Header
    header_table = Table(
        [[title, box_table]], 
        colWidths=[W - 2*MARGIN - 60*mm, 60*mm]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 15*mm))


# ── Client Details Section ───────────────────────────────────────────────────
def build_client_details(story: list, audit: dict, styles: dict):
    from_details = f"""
    {SENDER_NAME.upper()}<br/>
    {SENDER_TITLE.upper()}<br/>
    {SENDER_EMAIL}
    """
    
    to_details = f"""
    {audit.get("store_name", "E-COMMERCE FOUNDER").upper()}<br/>
    {audit.get("store_url", "").replace('https://', '').upper()}<br/>
    """

    data = [
        [
            mk("PREPARED BY", styles["details_heading"]),
            mk("PREPARED FOR", styles["details_heading"])
        ],
        [
            mk(from_details.strip(), styles["details_body"]),
            mk(to_details.strip(), styles["details_body"])
        ]
    ]

    details_table = Table(data, colWidths=[(W - 2*MARGIN)/2.0]*2)
    details_table.setStyle(TableStyle([
        # Add light teal background just behind the "FROM/TO" column headers to match the image
        ("BACKGROUND", (0, 0), (0, 0), LIGHT_TEAL),
        ("BACKGROUND", (1, 0), (1, 0), LIGHT_TEAL),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2*mm),
        ("TOPPADDING", (0, 0), (-1, 0), 2*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10*mm),
    ]))

    story.append(details_table)
    story.append(Spacer(1, 5*mm))


# ── Inline Cropped Screenshot ────────────────────────────────────────────────
CROP_ZONES = {
    "top": (0.0, 0.35),
    "middle": (0.30, 0.65),
    "bottom": (0.60, 1.0),
}

def get_screenshot_path(store_dir: str, source: str) -> str | None:
    """Resolve homepage or product screenshot path from the store's screenshot folder."""
    candidates = {
        "homepage": ["homepage.png"],
        "product": ["product_page.png", "homepage.png"],  # fallback to homepage if no product shot
    }
    for fname in candidates.get(source, ["homepage.png"]):
        path = os.path.join(store_dir, fname)
        if os.path.exists(path):
            return path
    return None


def crop_screenshot(img_path: str, region: str, max_width_pt: float) -> Image | None:
    """Crop a region of a screenshot and return a ReportLab Image object."""
    try:
        top_pct, bot_pct = CROP_ZONES.get(region, (0.0, 0.35))
        pil_img = PILImage.open(img_path)
        w_px, h_px = pil_img.size
        top_crop = int(h_px * top_pct)
        bot_crop = int(h_px * bot_pct)
        cropped = pil_img.crop((0, top_crop, w_px, bot_crop))

        # Scale to fit max PDF width while preserving aspect ratio
        crop_w, crop_h = cropped.size
        scale = max_width_pt / crop_w
        display_w = max_width_pt
        display_h = crop_h * scale

        # Cap height at ~80mm so it doesn't overwhelm the page
        max_h = 80 * mm
        if display_h > max_h:
            scale = max_h / display_h
            display_w = display_w * scale
            display_h = max_h

        buf = io.BytesIO()
        cropped.save(buf, format="PNG")
        buf.seek(0)
        return Image(buf, width=display_w, height=display_h)
    except Exception as e:
        logger.warning(f"Failed to crop screenshot {img_path}: {e}")
        return None


# ── The Main Audit Table ─────────────────────────────────────────────────────
def build_audit_table(story: list, audit: dict, styles: dict, screenshot_paths: list[str]):
    issues = audit.get("all_issues", [])
    if not issues:
        story.append(mk("No major audit findings recorded.", styles["td_main"]))
        return

    # Build a mapping: source -> screenshot file path
    store_name = audit.get("store_name", "Store")
    safe_name = sanitize_filename(store_name)
    store_dir = os.path.join(PDF_DIR, safe_name)

    shot_map: dict[str, str | None] = {}
    for shot in screenshot_paths:
        fname = os.path.basename(shot).lower()
        if "product" in fname:
            shot_map["product"] = shot
        elif "homepage" in fname or "home" in fname:
            shot_map["homepage"] = shot
    # also scan the store dir directly for any screenshots
    if os.path.isdir(store_dir):
        for fname in os.listdir(store_dir):
            if fname.endswith(".png"):
                src = "product" if "product" in fname.lower() else "homepage"
                if src not in shot_map:
                    shot_map[src] = os.path.join(store_dir, fname)

    col_widths = [12*mm, 88*mm, 30*mm, 30*mm]
    usable_w = sum(col_widths)
    desc_col_w = col_widths[1] - 4*mm  # inner content width for the screenshot

    # Table Header (separate table, repeated at top only)
    header_data = [[
        mk("No.", styles["th"]),
        mk("Audit Finding & Strategic Fix", styles["th_left"]),
        mk("Impact Metric", styles["th"]),
        mk("Est. Revenue Impact", styles["th"])
    ]]
    header_table = Table(header_data, colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_TEAL),
        ("BOX", (0, 0), (-1, 0), 0.5, BLACK),
        ("INNERGRID", (0, 0), (-1, 0), 0.5, BLACK),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 3*mm),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 2*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    story.append(header_table)

    # Emit each finding as: [row table] then [cropped screenshot]
    for idx, issue in enumerate(issues, start=1):
        num_cell = mk(str(idx), styles["td_num"])
        main_text = f"<b>Problem:</b> {issue.get('problem', '')}<br/>"
        sub_text = f"<b>Fix:</b> {issue.get('fix', '')}"
        desc_cell = [
            mk(main_text, styles["td_main"]),
            mk(sub_text, styles["td_sub"])
        ]
        metric_str = f"{issue.get('impact_level', 'Medium').upper()}<br/><br/>{issue.get('impacted_metric', '')}"
        metric_cell = mk(metric_str, styles["td_center"])
        rev_cell = mk(issue.get("revenue_impact", ""), styles["td_center"])

        row_table = Table([[num_cell, desc_cell, metric_cell, rev_cell]], colWidths=col_widths)
        row_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, BLACK),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BLACK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3*mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3*mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 2*mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2*mm),
        ]))
        story.append(row_table)

        # Inline cropped screenshot
        hint = issue.get("screenshot_hint")
        if hint:
            source = hint.get("source", "homepage")
            region = hint.get("region", "top")
            img_path = shot_map.get(source) or shot_map.get("homepage")
            if img_path and os.path.exists(img_path):
                cropped_img = crop_screenshot(img_path, region, usable_w)
                if cropped_img:
                    # Wrap in a thin-bordered box to visually tie it to the row above
                    img_table = Table([[cropped_img]], colWidths=[usable_w])
                    img_table.setStyle(TableStyle([
                        ("BOX", (0, 0), (-1, -1), 0.5, LIGHT_GRAY_LINE),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("TOPPADDING", (0, 0), (-1, -1), 1*mm),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1*mm),
                    ]))
                    caption = f"Screenshot: {source.title()} — {region} section"
                    story.append(img_table)
                    story.append(mk(caption, ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=7, textColor=GRAY_TEXT)))

        story.append(Spacer(1, 3*mm))

    story.append(Spacer(1, 8*mm))


# ── Bottom Note Section ──────────────────────────────────────────────────────
def build_footer_note(story: list, styles: dict):
    note_title = mk("Note", styles["note_head"])
    note_text = mk("This audit prioritizes high-ROI fixes. Implementing the top 3 recommendations typically yields a 15-30% lift in conversion rate within 30 days. Let's discuss execution.", styles["note_body"])
    
    note_table = Table([[note_title], [note_text]], colWidths=[W - 2*MARGIN])
    note_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_TEAL),
        ("BOX", (0, 0), (-1, -1), 0.5, BLACK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3*mm),
    ]))
    story.append(note_table)


# ── Visual Evidence (Screenshots) ────────────────────────────────────────────
def scale_image_to_fit(img_path: str, max_width: float, max_height: float):
    img_reader = ImageReader(img_path)
    img_w, img_h = img_reader.getSize()
    
    ratio = min(max_width / img_w, max_height / img_h)
    return img_w * ratio, img_h * ratio

def build_visual_evidence(story: list, screenshots: list[str], styles: dict):
    if not screenshots:
        return
        
    story.append(PageBreak())
    story.append(mk("VISUAL EVIDENCE", styles["invoice_title"]))
    story.append(Spacer(1, 10*mm))
    
    max_w = W - 2*MARGIN
    max_h = H - 2*MARGIN - 40*mm
    
    # Filter for desktop screenshots only (ignore anything with 'mobile' in the name)
    desktop_shots = [s for s in screenshots if "mobile" not in s.lower()]
    
    for shot in desktop_shots:
        if os.path.exists(shot):
            shot_w, shot_h = scale_image_to_fit(shot, max_w, max_h)
            img = Image(shot, width=shot_w, height=shot_h)
            
            # Put image in a clean box
            img_table = Table([[img]], colWidths=[max_w])
            img_table.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 0.5, LIGHT_GRAY_LINE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2*mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
            ]))
            
            label_text = os.path.basename(shot).replace(".png", "").replace("_", " ").title()
            story.append(mk(label_text, styles["details_heading"]))
            story.append(Spacer(1, 2*mm))
            story.append(img_table)
            story.append(Spacer(1, 10*mm))


# ── Main Orchestrator ────────────────────────────────────────────────────────
def generate_pdf(audit: dict, screenshot_paths: list[str] | None = None) -> str | None:
    if screenshot_paths is None:
        screenshot_paths = []

    store_name = audit.get("store_name", "Store").strip()
    if not store_name:
        store_name = "Store"
        
    safe_name = sanitize_filename(store_name)
    pdf_filename = f"{safe_name}_CRO_Audit.pdf"
    
    store_dir = os.path.join(PDF_DIR, safe_name)
    os.makedirs(store_dir, exist_ok=True)
    out_path = os.path.join(store_dir, pdf_filename)

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        rightMargin=MARGIN, leftMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN
    )

    styles = get_styles()
    story = []

    # Page 1: Main Invoice Report
    build_header(story, audit, styles)
    build_client_details(story, audit, styles)
    build_audit_table(story, audit, styles, screenshot_paths)
    build_footer_note(story, styles)
    
    # Optional Page 2+: Images
    build_visual_evidence(story, screenshot_paths, styles)

    try:
        doc.build(story) # Removed header footer to keep it ultra minimal
        logger.info(f"Generated invoice-style PDF: {out_path}")
        return out_path
    except Exception as e:
        logger.error(f"Failed to build PDF {out_path}: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dummy = {
        "store_name": "Test Store",
        "store_url": "https://test.com",
        "overall_score": 62,
        "all_issues": [
            {
                "problem": "No clear hero/banner section detected above the fold",
                "impacted_metric": "Bounce Rate",
                "impact_level": "High",
                "fix": "Add a compelling above-the-fold hero with clear value proposition",
                "type": "Quick Win",
                "revenue_impact": "Header clarity that optimizes conversion rate by 10-20%"
            },
            {
                "problem": "ATC (Add to Cart) button is not easily identifiable",
                "impacted_metric": "Conversion Rate",
                "impact_level": "High",
                "fix": "Make ATC button sticky on mobile and use a high-contrast color",
                "type": "Quick Win",
                "revenue_impact": "Sticky CTA implementation that increases mobile CVR by 10-25%"
            }
        ]
    }
    generate_pdf(dummy)
