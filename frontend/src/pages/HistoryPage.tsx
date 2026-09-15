import { useEffect, useState } from "react";
import { getHistory } from "../services/api";
import HistoryTable, { HistoryItem } from "../components/HistoryTable";

const PAGE_SIZE = 10;

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    getHistory().then(setItems);
  }, []);

  const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const start = (safePage - 1) * PAGE_SIZE;
  const pageItems = items.slice(start, start + PAGE_SIZE);

  function go(p: number) {
    setPage(Math.max(1, Math.min(p, totalPages)));
  }

  return (
    <>
      <div className="page-head">
        <h1>سجل التحليلات السابقة</h1>
        <p>عرض جميع تحليلات المشاعر التي تم إجراؤها.</p>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <HistoryTable items={pageItems} />
      </div>

      {items.length > PAGE_SIZE && (
        <div className="pagination">
          <button
            className="page-btn"
            onClick={() => go(safePage - 1)}
            disabled={safePage <= 1}
            aria-label="الصفحة السابقة"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m9 18 6-6-6-6" />
            </svg>
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              className={`page-btn ${p === safePage ? "active" : ""}`}
              onClick={() => go(p)}
            >
              {p}
            </button>
          ))}

          <button
            className="page-btn"
            onClick={() => go(safePage + 1)}
            disabled={safePage >= totalPages}
            aria-label="الصفحة التالية"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m15 18-6-6 6-6" />
            </svg>
          </button>

          <span className="page-info">
            {start + 1}–{Math.min(start + PAGE_SIZE, items.length)} من{" "}
            {items.length}
          </span>
        </div>
      )}
    </>
  );
}
