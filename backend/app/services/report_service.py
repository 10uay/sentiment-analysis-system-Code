import csv
import io
from collections import Counter
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.api.schemas import ModelResult
from app.db.models import Analysis


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

    def generate_csv(self, rows: list[Analysis]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "text", "language", "label", "confidence", "model_name", "created_at"])
        for r in rows:
            writer.writerow([r.id, r.text, r.language, r.label, r.confidence, r.model_name, r.created_at])
        return output.getvalue()

    def generate_pdf(self, rows: list[Analysis], include_charts: bool = True) -> bytes:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Sentiment Analysis Report")
        y -= 25

        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Generated at: {datetime.utcnow().isoformat()} UTC")
        y -= 25

        counts = Counter(r.label for r in rows)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Summary")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Total analyses: {len(rows)}")
        y -= 15

        for label, count in counts.items():
            c.drawString(60, y, f"{label}: {count}")
            y -= 15

        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Items")
        y -= 18
        c.setFont("Helvetica", 9)

        for r in rows[:50]:
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)
            text = (r.text[:90] + "...") if len(r.text) > 90 else r.text
            safe_text = text.encode("latin-1", "replace").decode("latin-1")
            c.drawString(50, y, f"#{r.id} [{r.language}] {r.label} ({r.confidence:.2f}) - {safe_text}")
            y -= 14

        c.save()
        return buffer.getvalue()
