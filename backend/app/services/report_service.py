import csv
import io
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from app.api.schemas import ModelResult
from app.db.models import Analysis

FONT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"
ARABIC_FONT_PATH = FONT_DIR / "SFArabic.ttf"

# Brand palette
COLOR_PRIMARY = colors.HexColor("#4F46E5")
COLOR_PRIMARY_DARK = colors.HexColor("#3730A3")
COLOR_ACCENT = colors.HexColor("#10B981")
COLOR_BG_LIGHT = colors.HexColor("#F3F4F6")
COLOR_ROW_ALT = colors.HexColor("#F9FAFB")
COLOR_TEXT = colors.HexColor("#1F2937")
COLOR_MUTED = colors.HexColor("#6B7280")
COLOR_BORDER = colors.HexColor("#E5E7EB")

# Sentiment label -> color mapping
LABEL_COLORS = {
    "positive": colors.HexColor("#10B981"),
    "negative": colors.HexColor("#EF4444"),
    "neutral": colors.HexColor("#6366F1"),
    "mixed": colors.HexColor("#F59E0B"),
}

# Arabic translations for common labels / UI strings
LABEL_AR = {
    "positive": "إيجابي",
    "negative": "سلبي",
    "neutral": "محايد",
    "mixed": "مختلط",
}

UI_AR = {
    "title": "تقرير تحليل المشاعر",
    "generated": "تاريخ الإنشاء",
    "summary": "الملخص",
    "total": "إجمالي التحليلات",
    "items": "التفاصيل",
    "id": "#",
    "lang": "اللغة",
    "label": "التصنيف",
    "confidence": "الثقة",
    "text": "النص",
    "distribution": "التوزيع",
    "page": "صفحة",
    "system": "نظام تحليل المشاعر",
}

UI_EN = {
    "title": "Sentiment Analysis Report",
    "generated": "Generated at",
    "summary": "Summary",
    "total": "Total analyses",
    "items": "Details",
    "id": "#",
    "lang": "Lang",
    "label": "Label",
    "confidence": "Conf.",
    "text": "Text",
    "distribution": "Distribution",
    "page": "Page",
    "system": "Sentiment Analysis System",
}

_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")


def _register_fonts() -> None:
    """Register the Arabic-capable TTF font with reportlab (idempotent)."""
    if "Arabic" in pdfmetrics.getRegisteredFontNames():
        return
    if not ARABIC_FONT_PATH.exists():
        raise FileNotFoundError(f"Arabic font not found at {ARABIC_FONT_PATH}")
    pdfmetrics.registerFont(TTFont("Arabic", str(ARABIC_FONT_PATH)))


def _has_arabic(text: str) -> bool:
    return bool(text) and bool(_ARABIC_RE.search(text))


def _shape(text: str) -> str:
    """Reshape Arabic glyphs and apply the BiDi algorithm for correct rendering."""
    if not text:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def _prepare(text: str) -> tuple[str, str]:
    """Return (display_text, font_name) appropriate for the text's script.

    Pure-Latin text uses Helvetica (crisp Latin glyphs); anything containing
    Arabic uses the embedded Arabic font with reshaping + BiDi applied.
    """
    if not text:
        return text, "Helvetica"
    if _has_arabic(text):
        return _shape(text), "Arabic"
    return text, "Helvetica"


def _draw_text(c, x, y, text, font_size, color=None) -> None:
    disp, font = _prepare(text)
    c.setFont(font, font_size)
    if color is not None:
        c.setFillColor(color)
    c.drawString(x, y, disp)


def _draw_right_text(c, x, y, text, font_size, color=None) -> None:
    disp, font = _prepare(text)
    c.setFont(font, font_size)
    if color is not None:
        c.setFillColor(color)
    c.drawRightString(x, y, disp)


def _draw_centered_text(c, x, y, text, font_size, color=None) -> None:
    disp, font = _prepare(text)
    c.setFont(font, font_size)
    if color is not None:
        c.setFillColor(color)
    c.drawCentredString(x, y, disp)


def _label_display(label: str, language: str) -> str:
    if language == "ar" and label in LABEL_AR:
        return LABEL_AR[label]
    return label.capitalize()


def _lang_display(language: str) -> str:
    if language == "ar":
        return "العربية"
    return "EN"


class ReportService:
    def generate_summary(
        self,
        text: str,
        label: str,
        confidence: float,
        language: str,
        model_results: list[ModelResult],
        context: list[str],
    ) -> str:
        models = ", ".join([m.model_name for m in model_results])
        if language == "ar":
            return (
                f"النص تم تصنيفه على أنه {label} بدرجة ثقة {confidence:.2f}. "
                f"النماذج المستخدمة: {models}. "
                f"عدد المقاطع المسترجعة عبر RAG: {len(context)}."
            )
        return (
            f"The text was classified as {label} with confidence {confidence:.2f}. "
            f"Models used: {models}. "
            f"Retrieved RAG contexts: {len(context)}."
        )

    # Generate the Excel report
    def generate_csv(self, rows: list[Analysis]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "text", "language", "label", "confidence", "model_name", "created_at"])
        for r in rows:
            writer.writerow([r.id, r.text, r.language, r.label, r.confidence, r.model_name, r.created_at])
        return output.getvalue()

    # ------------------------------------------------------------------
    # PDF generation
    # ------------------------------------------------------------------
    def generate_pdf(self, rows: list[Analysis], include_charts: bool = True) -> bytes:
        _register_fonts()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 40
        content_w = width - 2 * margin

        page_number = 0

        def new_page() -> float:
            nonlocal page_number
            page_number += 1
            if page_number > 1:
                c.showPage()
            self._draw_header(c, width, height, margin, content_w)
            self._draw_footer(c, width, height, margin, page_number)
            return height - 110  # top of content area

        y = new_page()

        # ---- Summary section ----
        y = self._draw_summary(c, rows, margin, y, content_w)

        # ---- Distribution chart (simple bars) ----
        if include_charts:
            y = self._draw_distribution(c, rows, margin, y, content_w)
            if y < 160:
                y = new_page()

        # ---- Details table ----
        y = self._draw_details(c, rows, margin, y, content_w, width, height, new_page)

        c.save()
        return buffer.getvalue()

    # ------------------------------------------------------------------
    def _draw_header(self, c, width, height, margin, content_w) -> None:
        # Top brand band
        band_h = 70
        c.setFillColor(COLOR_PRIMARY)
        c.rect(0, height - band_h, width, band_h, fill=1, stroke=0)
        # Accent stripe
        c.setFillColor(COLOR_ACCENT)
        c.rect(0, height - band_h - 4, width, 4, fill=1, stroke=0)

        # Title (Arabic, right-aligned)
        _draw_right_text(c, width - margin, height - 38, UI_AR["title"], 22, colors.white)
        # Subtitle (English) on the left
        _draw_text(c, margin, height - 38, UI_EN["title"], 11, colors.HexColor("#E0E7FF"))
        _draw_text(c, margin, height - 54,
                   f"{UI_EN['generated']}: {datetime.utcnow().isoformat()} UTC",
                   9, colors.HexColor("#E0E7FF"))

    def _draw_footer(self, c, width, height, margin, page_number) -> None:
        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(margin, 40, width - margin, 40)
        _draw_text(c, margin, 28, UI_AR["system"], 8, COLOR_MUTED)
        _draw_right_text(c, width - margin, 28,
                         f"{UI_AR['page']} {page_number}", 8, COLOR_MUTED)

    def _draw_summary(self, c, rows, margin, y, content_w) -> float:
        # Section title (English left, Arabic right)
        _draw_text(c, margin, y, UI_EN["summary"], 14, COLOR_PRIMARY_DARK)
        _draw_right_text(c, margin + content_w, y, UI_AR["summary"], 14, COLOR_PRIMARY_DARK)
        y -= 8
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(2)
        c.line(margin, y, margin + content_w, y)
        y -= 24

        # Stat cards: 1 total + one card per label present in the data
        counts = Counter(r.label for r in rows)
        total = len(rows)
        present_labels = [lbl for lbl in ["positive", "negative", "neutral", "mixed"]
                          if counts.get(lbl, 0) > 0]
        n_cards = 1 + len(present_labels)
        card_w = (content_w - (n_cards - 1) * 12) / n_cards
        card_h = 74

        # First card: total
        self._stat_card(c, margin, y, card_w, card_h, UI_EN["total"], UI_AR["total"],
                        str(total), COLOR_PRIMARY)

        # One card per label that actually appears in the data
        for i, label in enumerate(present_labels, start=1):
            count = counts.get(label, 0)
            color = LABEL_COLORS.get(label, COLOR_MUTED)
            label_en = label.capitalize()
            label_ar = LABEL_AR.get(label, label)
            self._stat_card(c, margin + i * (card_w + 12), y, card_w, card_h,
                            label_en, label_ar, str(count), color)

        return y - card_h - 24

    def _stat_card(self, c, x, y, w, h, title_en, title_ar, value, color) -> None:
        # Card background
        c.setFillColor(COLOR_BG_LIGHT)
        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
        # Color tab on the left
        c.setFillColor(color)
        c.roundRect(x, y, 6, h, 6, fill=1, stroke=0)
        c.rect(x + 3, y, 3, h, fill=1, stroke=0)
        # Value (top)
        _draw_text(c, x + 14, y + h - 22, value, 20, COLOR_TEXT)
        # English label (middle)
        _draw_text(c, x + 14, y + 24, title_en, 8, COLOR_MUTED)
        # Arabic label (bottom)
        _draw_text(c, x + 14, y + 10, title_ar, 8, COLOR_MUTED)

    def _draw_distribution(self, c, rows, margin, y, content_w) -> float:
        _draw_text(c, margin, y, UI_EN["distribution"], 14, COLOR_PRIMARY_DARK)
        _draw_right_text(c, margin + content_w, y, UI_AR["distribution"], 14, COLOR_PRIMARY_DARK)
        y -= 8
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(2)
        c.line(margin, y, margin + content_w, y)
        y -= 24

        counts = Counter(r.label for r in rows)
        total = max(len(rows), 1)
        labels = [lbl for lbl in ["positive", "negative", "neutral", "mixed"]
                  if counts.get(lbl, 0) > 0]
        bar_h = 18
        gap = 10
        # Layout: [label 110px] [bar] [count 70px]  — all within content area
        label_w = 110
        count_w = 70
        right_edge = margin + content_w
        bx = margin + label_w + 10
        max_bar_w = right_edge - bx - count_w - 8

        for label in labels:
            count = counts.get(label, 0)
            pct = count / total
            color = LABEL_COLORS.get(label, COLOR_MUTED)

            # Label text (en left, ar right of the label area)
            _draw_text(c, margin, y, label.capitalize(), 10, COLOR_TEXT)
            _draw_right_text(c, margin + label_w, y, LABEL_AR.get(label, label), 10, COLOR_TEXT)

            # Bar background
            c.setFillColor(COLOR_BG_LIGHT)
            c.roundRect(bx, y - 2, max_bar_w, bar_h, 4, fill=1, stroke=0)
            # Filled bar
            c.setFillColor(color)
            if pct > 0:
                c.roundRect(bx, y - 2, max(max_bar_w * pct, 4), bar_h, 4, fill=1, stroke=0)
            # Count + percentage (right-aligned within content area)
            _draw_right_text(c, right_edge, y + 2,
                             f"{count} ({pct*100:.1f}%)", 9, COLOR_TEXT)

            y -= bar_h + gap

        return y - 12

    def _draw_details(self, c, rows, margin, y, content_w, width, height, new_page) -> float:
        # Section title
        _draw_text(c, margin, y, UI_EN["items"], 14, COLOR_PRIMARY_DARK)
        _draw_right_text(c, margin + content_w, y, UI_AR["items"], 14, COLOR_PRIMARY_DARK)
        y -= 8
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(2)
        c.line(margin, y, margin + content_w, y)
        y -= 14

        # Column layout
        col_id_w = 30
        col_lang_w = 40
        col_label_w = 70
        col_conf_w = 50
        col_text_x = margin + col_id_w + col_lang_w + col_label_w + col_conf_w
        col_text_w = width - margin - col_text_x

        def draw_table_header(yy: float) -> float:
            header_h = 22
            c.setFillColor(COLOR_PRIMARY)
            c.rect(margin, yy - header_h, content_w, header_h, fill=1, stroke=0)
            hy = yy - header_h + 7
            _draw_text(c, margin + 6, hy, UI_EN["id"], 9, colors.white)
            _draw_text(c, margin + col_id_w + 6, hy, UI_EN["lang"], 9, colors.white)
            _draw_text(c, margin + col_id_w + col_lang_w + 6, hy, UI_EN["label"], 9, colors.white)
            _draw_text(c, margin + col_id_w + col_lang_w + col_label_w + 6, hy, UI_EN["confidence"], 9, colors.white)
            _draw_text(c, col_text_x + 6, hy, UI_EN["text"], 9, colors.white)
            # Arabic header labels on the right side of each column
            _draw_right_text(c, margin + col_id_w - 2, hy, UI_AR["id"], 9, colors.white)
            _draw_right_text(c, margin + col_id_w + col_lang_w - 2, hy, UI_AR["lang"], 9, colors.white)
            _draw_right_text(c, margin + col_id_w + col_lang_w + col_label_w - 2, hy, UI_AR["label"], 9, colors.white)
            _draw_right_text(c, margin + col_id_w + col_lang_w + col_label_w + col_conf_w - 2, hy, UI_AR["confidence"], 9, colors.white)
            return yy - header_h

        y = draw_table_header(y)

        # Data rows
        row_h = 26
        max_rows = 100
        for idx, r in enumerate(rows[:max_rows]):
            if y < 70:
                y = new_page()
                y = draw_table_header(y)

            # Alternating row background
            if idx % 2 == 1:
                c.setFillColor(COLOR_ROW_ALT)
                c.rect(margin, y - row_h, content_w, row_h, fill=1, stroke=0)

            # Truncate text to fit
            max_chars = 70
            text = r.text if len(r.text) <= max_chars else r.text[:max_chars] + "..."

            # Label pill
            label_color = LABEL_COLORS.get(r.label, COLOR_MUTED)
            pill_x = margin + col_id_w + col_lang_w + 6
            pill_w = col_label_w - 12
            c.setFillColor(label_color)
            c.roundRect(pill_x, y - row_h + 6, pill_w, 14, 7, fill=1, stroke=0)
            _draw_centered_text(c, pill_x + pill_w / 2, y - row_h + 10,
                                 _label_display(r.label, r.language), 8, colors.white)

            # Other cells
            _draw_text(c, margin + 6, y - 16, str(r.id), 9, COLOR_TEXT)
            _draw_text(c, margin + col_id_w + 6, y - 16, _lang_display(r.language), 9, COLOR_TEXT)
            _draw_text(c, margin + col_id_w + col_lang_w + col_label_w + 6, y - 16,
                       f"{r.confidence:.2f}", 9, COLOR_TEXT)
            _draw_text(c, col_text_x + 6, y - 16, text, 8, COLOR_MUTED)

            y -= row_h

        return y
