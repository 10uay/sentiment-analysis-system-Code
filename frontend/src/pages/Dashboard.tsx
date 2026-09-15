import { useEffect, useState } from "react";
import { getHistory } from "../services/api";
import SentimentChart from "../components/SentimentChart";

const LABELS: Record<string, string> = {
  positive: "إيجابي",
  very_positive: "إيجابي جداً",
  negative: "سلبي",
  very_negative: "سلبي جداً",
  neutral: "حيادي",
};

const COLORS: Record<string, string> = {
  positive: "#22c55e",
  very_positive: "#10b981",
  negative: "#ef4444",
  very_negative: "#dc2626",
  neutral: "#eab308",
};

export default function Dashboard() {
  const [data, setData] = useState<{ name: string; value: number }[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    getHistory().then((rows) => {
      const counts: Record<string, number> = {};
      rows.forEach((r: any) => {
        counts[r.label] = (counts[r.label] || 0) + 1;
      });
      const arr = Object.entries(counts).map(([name, value]) => ({
        name,
        value,
      }));
      setData(arr);
      setTotal(rows.length);
    });
  }, []);

  const top = [...data].sort((a, b) => b.value - a.value)[0];

  return (
    <>
      <div className="page-head">
        <h1>لوحة التحكم</h1>
        <p>توزيع نتائج تحليل المشاعر المخزنة في قاعدة البيانات.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">إجمالي التحليلات</div>
          <div className="stat-value">{total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">الفئات المكتشفة</div>
          <div className="stat-value">{data.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">المشاعر الغالبة</div>
          <div className="stat-value" style={{ fontSize: 22 }}>
            {top ? (
              <>
                <i
                  className="stat-dot"
                  style={{ background: COLORS[top.name] || "#6366f1" }}
                />
                {LABELS[top.name] || top.name}
              </>
            ) : (
              "—"
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <h3>توزيع المشاعر</h3>
        {data.length > 0 ? (
          <SentimentChart data={data} />
        ) : (
          <div className="empty-state">
            <p>لا توجد بيانات لعرضها بعد.</p>
          </div>
        )}
      </div>
    </>
  );
}
