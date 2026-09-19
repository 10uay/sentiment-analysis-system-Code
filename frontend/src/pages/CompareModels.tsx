import { useState } from "react";
import { analyzeText, AnalyzeResponse } from "../services/api";
import ResultCard from "../components/ResultCard";

export default function CompareModels() {
  const models = ["arabert", "xlmr", "ensemble", "llm"];
  const [text, setText] = useState(
    "The service is excellent but the price is expensive",
  );
  const [results, setResults] = useState<AnalyzeResponse[]>([]);
  const [loading, setLoading] = useState(false);

  async function compare() {
    setLoading(true);
    const out: AnalyzeResponse[] = [];
    for (const m of models) {
      out.push(await analyzeText(text, m, true));
    }
    setResults(out);
    setLoading(false);
  }

  return (
    <>
      <div className="page-head">
        <h1>مقارنة نتائج النماذج</h1>
        <p>قم بتحليل نفس النص عبر جميع النماذج ومقارنة النتائج.</p>
      </div>

      <div className="card">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="اكتب النص للمقارنة..."
        />
        <button className="primary" onClick={compare} disabled={loading}>
          {loading && <span className="spinner" />}
          {loading ? "جاري المقارنة..." : "قارن النماذج"}
        </button>
      </div>

      {results.length > 0 && (
        <div className="grid">
          {results.map((r, i) => (
            <ResultCard key={i} result={r} modelName={models[i]} />
          ))}
        </div>
      )}
    </>
  );
}
