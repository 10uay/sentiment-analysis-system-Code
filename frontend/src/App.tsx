import { useState, type ReactNode } from "react";
import AnalyzerPage from "./pages/AnalyzerPage";
import Dashboard from "./pages/Dashboard";
import HistoryPage from "./pages/HistoryPage";
import ReportsPage from "./pages/ReportsPage";
import CompareModels from "./pages/CompareModels";

type Page = "analyzer" | "dashboard" | "history" | "reports" | "compare";

const NAV: { key: Page; label: string; icon: ReactNode }[] = [
  {
    key: "analyzer",
    label: "تحليل نص",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M4 7V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2" />
        <path d="M9 21h6" />
        <path d="M12 17v4" />
        <path d="M8 11l2 2 4-4" />
        <rect x="3" y="7" width="18" height="10" rx="2" />
      </svg>
    ),
  },
  {
    key: "dashboard",
    label: "لوحة التحكم",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
  },
  {
    key: "history",
    label: "السجل",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
        <path d="M3 3v5h5" />
        <path d="M12 7v5l3 2" />
      </svg>
    ),
  },
  {
    key: "reports",
    label: "التقارير",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6" />
        <path d="M9 13h6" />
        <path d="M9 17h6" />
      </svg>
    ),
  },
  {
    key: "compare",
    label: "مقارنة النماذج",
    icon: (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M12 3v18" />
        <path d="M7 8l-4 4 4 4" />
        <path d="M17 8l4 4-4 4" />
      </svg>
    ),
  },
];

export default function App() {
  const [page, setPage] = useState<Page>("analyzer");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2a3 3 0 0 0-3 3v.5A2.5 2.5 0 0 0 7 8a2.5 2.5 0 0 0 0 5 2.5 2.5 0 0 0 3 2.5V16a3 3 0 0 0 6 0v-.5A2.5 2.5 0 0 0 19 13a2.5 2.5 0 0 0 0-5 2.5 2.5 0 0 0-4-2.5V5a3 3 0 0 0-3-3z" />
            </svg>
          </div>
          <div>
            <h2 className="brand-title">تحليل المشاعر</h2>
            <p className="brand-sub">SENTIMENT ANALYSIS</p>
          </div>
        </div>

        {NAV.map((item) => (
          <button
            key={item.key}
            className={`nav-item ${page === item.key ? "active" : ""}`}
            onClick={() => setPage(item.key)}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}

        <div className="sidebar-footer">
          نظام تحليل المشاعر للمهندس لؤي · v1.0
        </div>
      </aside>

      <main className="main-content">
        {page === "analyzer" && <AnalyzerPage />}
        {page === "dashboard" && <Dashboard />}
        {page === "history" && <HistoryPage />}
        {page === "reports" && <ReportsPage />}
        {page === "compare" && <CompareModels />}
      </main>
    </div>
  );
}
