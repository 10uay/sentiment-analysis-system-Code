import type { AnalyzeResponse } from "../services/api";

function labelArabic(label: string) {
  const map: Record<string, string> = {
    positive: "إيجابي",
    negative: "سلبي",
    neutral: "حيادي",
    very_positive: "إيجابي جداً",
    very_negative: "سلبي جداً",
  };
  return map[label] || label;
}

export default function ResultCard({
  result,
  modelName,
}: {
  result: AnalyzeResponse;
  modelName?: string;
}) {
  const conf = Math.round(result.confidence * 100);

  return (
    <div className="card">
      {modelName && (
        <h2
          className="model-title"
          style={{
            fontSize: "1.6rem",
            fontWeight: 800,
            textAlign: "center",
            textTransform: "uppercase",
          }}
        >
          {modelName}
        </h2>
      )}
      <div className="badge">اللغة: {result.language}</div>
      <p className={`result-label sent-${result.final_label}`}>
        {labelArabic(result.final_label)}
      </p>

      <div className="confidence">
        <div className="confidence-row">
          <span>درجة الثقة</span>
          <span>{conf}%</span>
        </div>
        <div className="confidence-track">
          <div className="confidence-fill" style={{ width: `${conf}%` }} />
        </div>
      </div>

      {result.report_summary && <p>{result.report_summary}</p>}

      <h3>نتائج النماذج</h3>
      <div className="grid">
        {result.model_results
          .filter((m) => (modelName ? m.model_name === modelName : true))
          .map((m) => {
            const score = Math.round(m.score * 100);
            return (
              <div className="model-card" key={m.model_name}>
                <strong>{m.model_name}</strong>
                <p
                  className={`sent-${m.label}`}
                  style={{ margin: "0 0 8px", fontWeight: 700 }}
                >
                  {labelArabic(m.label)} — {score}%
                </p>
                <div className="confidence-track">
                  <div
                    className="confidence-fill"
                    style={{ width: `${score}%` }}
                  />
                </div>
                {m.explanation && <small>{m.explanation}</small>}
              </div>
            );
          })}
      </div>

      {result.rag_context.length > 0 && (
        <>
          <h3>سياق RAG المسترجع</h3>
          <ul className="rag-list">
            {result.rag_context.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
