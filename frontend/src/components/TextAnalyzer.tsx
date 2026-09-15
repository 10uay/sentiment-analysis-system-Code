import { useState } from "react";
import { analyzeText } from "../services/api";
import ModelSelector from "./ModelSelector";
import ResultCard from "./ResultCard";
import { useAppStore } from "../store/useAppStore";

export default function TextAnalyzer() {
  const [text, setText] = useState("هذا المنتج رائع ومفيد");
  const [model, setModel] = useState("ensemble");
  const [useRag, setUseRag] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const lastResult = useAppStore((s) => s.lastResult);
  const setLastResult = useAppStore((s) => s.setLastResult);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      const res = await analyzeText(text, model, useRag);
      setLastResult(res);
    } catch (e) {
      setError(
        "حدث خطأ أثناء الاتصال بالواجهة الخلفية. تأكد أن FastAPI يعمل على المنفذ 8000.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>تحليل مشاعر النصوص</h1>
        <p>أدخل النص واختر النموذج لتحليل المشاعر باستخدام الذكاء الاصطناعي.</p>
      </div>

      <div className="card">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="اكتب النص هنا..."
        />
        <div className="grid">
          <ModelSelector value={model} onChange={setModel} />
          <label>
            استخدام RAG
            <select
              value={String(useRag)}
              onChange={(e) => setUseRag(e.target.value === "true")}
            >
              <option value="true">نعم</option>
              <option value="false">لا</option>
            </select>
          </label>
        </div>
        <button className="primary" disabled={loading} onClick={submit}>
          {loading && <span className="spinner" />}
          {loading ? "جاري التحليل..." : "حلل النص"}
        </button>
        {error && <p className="error">{error}</p>}
      </div>

      {lastResult && <ResultCard result={lastResult} />}
    </>
  );
}
