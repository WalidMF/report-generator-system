import os
from datetime import datetime
import logging
from typing import List, Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit, ImageReader
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات عامة
TEMPLATE_PATH = 'template.pdf'   # القالب الأساسي (اختياري)
# Set preferred Arabic font file (place the TTF in the project folder or give full path)
FONT_PATH = 'f1.ttf'  # expected font file in project root
FONT_NAME = 'CustomArabicFont'

OUTPUT_DIR = 'reports'
FONT_SIZE = 17
TEXT_COLOR = HexColor("#000000")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Try to register the requested font; fall back to Arial if not available
if os.path.exists(FONT_PATH):
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    except Exception as e:
        logging.warning(f"Could not register {FONT_PATH}: {e}")
        if os.path.exists('arial.ttf'):
            FONT_NAME = 'ArialFallback'
            pdfmetrics.registerFont(TTFont(FONT_NAME, 'arial.ttf'))
        else:
            logging.warning("No TTF font found; Arabic rendering may be degraded.")
else:
    if os.path.exists('arial.ttf'):
        FONT_NAME = 'ArialFallback'
        pdfmetrics.registerFont(TTFont(FONT_NAME, 'arial.ttf'))
    else:
        logging.warning("No TTF font found; Arabic rendering may be degraded.")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def _reshape_ar(text: str) -> str:
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def generate_report_pdf(activity_name: str,
                        execution_date: str,
                        executor_name: str,
                        place: str,
                        target_group: str,
                        evidence_paths: List[str],
                        output_path: Optional[str] = None) -> str:
    """
    Generate a PDF report from provided fields and up to 4 evidence image paths.

    :returns: path to generated PDF file
    """
    # Validate images
    if not isinstance(evidence_paths, (list, tuple)):
        evidence_paths = [evidence_paths] if evidence_paths else []

    # require exactly 4 images
    if len(evidence_paths) != 4:
        raise ValueError("Exactly 4 evidence image paths are required")

    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, f"{activity_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    # Create an overlay PDF with the text and images
    overlay_path = os.path.join(OUTPUT_DIR, "_temp_overlay.pdf")
    c = canvas.Canvas(overlay_path, pagesize=A4)
    width, height = A4
    c.setFont(FONT_NAME, FONT_SIZE)
    c.setFillColor(TEXT_COLOR)

    # helper to draw right-aligned wrapped Arabic text
    def draw_wrapped_right(canvas_obj, x_right, y_start, text, max_width, line_height=None, max_lines=3):
        t = _reshape_ar(text)
        lines = simpleSplit(t, FONT_NAME, FONT_SIZE, max_width)
        if line_height is None:
            line_height = FONT_SIZE
        if max_lines is not None and len(lines) > max_lines:
            lines = lines[:max_lines]
        y = y_start
        for line in lines:
            try:
                canvas_obj.drawRightString(x_right, y, line)
            except Exception:
                canvas_obj.drawString(x_right - max_width, y, line)
            y -= line_height

    # layout positions (these coordinates can be tuned to match template)
    left_margin = 40
    right_x_main = 555
    mid_x = 270
    max_width_main = max(50, right_x_main - left_margin)
    max_width_mid = max(50, mid_x - left_margin)

    draw_wrapped_right(c, right_x_main, 657, activity_name, max_width_main, max_lines=3)
    draw_wrapped_right(c, right_x_main, 592, execution_date, max_width_main, max_lines=1)
    draw_wrapped_right(c, mid_x, 595, target_group, max_width_mid, max_lines=2)
    draw_wrapped_right(c, right_x_main, 532, place, max_width_main, max_lines=2)
    draw_wrapped_right(c, mid_x, 532, executor_name, max_width_mid, max_lines=2)

    # draw four images into fixed boxes
    img_box_w = 255
    img_box_h = 180
    # positions are (x, y) measured from bottom-left of page
    positions = [
        (305, 290),  # top-right area (example)
        (35, 290),   # top-left area
        (305, 95),   # bottom-right
        (35, 95)     # bottom-left
    ]

    for i, img_path in enumerate(evidence_paths[:4]):
        try:
            if not os.path.exists(img_path):
                logging.warning(f"Evidence image not found: {img_path}")
                continue

            img = Image.open(img_path)
            img = img.convert('RGB')
            # Resize/crop image to exact box size so all images have identical dimensions
            target_size = (img_box_w, img_box_h)
            try:
                img_fitted = ImageOps.fit(img, target_size, Image.LANCZOS)
            except Exception:
                # fallback to simple resize if fit fails
                img_fitted = img.resize(target_size, Image.LANCZOS)

            # Use ImageReader to draw PIL image object directly
            img_reader = ImageReader(img_fitted)

            x, y = positions[i]
            # Draw image with exact box width/height
            c.drawImage(img_reader, x, y, width=img_box_w, height=img_box_h)
        except Exception as e:
            logging.exception(f"Error drawing image {img_path}: {e}")

    c.save()

    # Merge with template if exists, otherwise use overlay as final
    output_pdf = PdfWriter()
    if os.path.exists(TEMPLATE_PATH):
        try:
            base_pdf = PdfReader(TEMPLATE_PATH)
            overlay_pdf = PdfReader(overlay_path)
            page = base_pdf.pages[0]
            page.merge_page(overlay_pdf.pages[0])
            output_pdf.add_page(page)
        except Exception:
            logging.exception("Failed to merge with template; using overlay only")
            overlay_pdf = PdfReader(overlay_path)
            output_pdf.add_page(overlay_pdf.pages[0])
    else:
        overlay_pdf = PdfReader(overlay_path)
        output_pdf.add_page(overlay_pdf.pages[0])

    # write the final PDF
    os.makedirs(os.path.dirname(output_path) or OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'wb') as f_out:
        output_pdf.write(f_out)

    try:
        os.remove(overlay_path)
    except Exception:
        pass

    logging.info(f"Generated PDF: {output_path}")
    return output_path
    
