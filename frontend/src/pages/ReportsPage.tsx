import { useEffect, useState } from "react";
import { downloadReport, getHistory } from "../services/api";

export default function ReportsPage() {
  const [ids, setIds] = useState<number[]>([]);
  const [busy, setBusy] = useState<"pdf" | "csv" | null>(null);

  useEffect(() => {
    getHistory().then((rows) => setIds(rows.map((x: any) => x.id)));
  }, []);

  async function exportFormat(format: "pdf" | "csv") {
    setBusy(format);
    try {
      const blob = await downloadReport(ids, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `sentiment_report.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setBusy(null);
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>توليد التقارير</h1>
        <p>يمكنك تصدير آخر التحليلات كملف PDF أو CSV.</p>
      </div>

      <div className="card">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">عدد التحليلات المتاحة للتصدير</div>
            <div className="stat-value">{ids.length}</div>
          </div>
        </div>

        <div className="report-actions">
          <button
            className="primary"
            onClick={() => exportFormat("pdf")}
            disabled={busy !== null || ids.length === 0}
          >
            {busy === "pdf" && <span className="spinner" />}
            تصدير PDF
          </button>
          <button
            className="btn-ghost"
            onClick={() => exportFormat("csv")}
            disabled={busy !== null || ids.length === 0}
          >
            {busy === "csv" && <span className="spinner" />}
            تصدير CSV
          </button>
        </div>
      </div>
    </>
  );
}
