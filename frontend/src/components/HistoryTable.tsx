export type HistoryItem = {
  id: number;
  text: string;
  language: string;
  label: string;
  confidence: number;
  model_name: string;
  created_at: string;
};

const LABELS: Record<string, string> = {
  positive: "إيجابي",
  very_positive: "إيجابي جداً",
  negative: "سلبي",
  very_negative: "سلبي جداً",
  neutral: "حيادي",
};

export default function HistoryTable({ items }: { items: HistoryItem[] }) {
  if (items.length === 0) {
    return (
      <div className="empty-state">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M3 3v18h18" />
          <path d="M7 14l3-3 3 3 4-5" />
        </svg>
        <p>لا توجد تحليلات بعد. ابدأ بتحليل نص من صفحة «تحليل نص».</p>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>الرقم</th>
            <th>النص</th>
            <th>اللغة</th>
            <th>المشاعر</th>
            <th>الثقة</th>
            <th>النموذج</th>
            <th>التاريخ</th>
          </tr>
        </thead>
        <tbody>
          {items.map((x) => (
            <tr key={x.id}>
              <td>{x.id}</td>
              <td className="ltr">{x.text.slice(0, 80)}</td>
              <td>{x.language}</td>
              <td>
                <span className={`pill ${x.label}`}>
                  {LABELS[x.label] || x.label}
                </span>
              </td>
              <td>{(x.confidence * 100).toFixed(1)}%</td>
              <td>{x.model_name}</td>
              <td>{new Date(x.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
