import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
});

export type ModelResult = {
  model_name: string;
  label: string;
  score: number;
  probabilities: Record<string, number>;
  explanation?: string;
};

export type AnalyzeResponse = {
  id?: number;
  original_text: string;
  cleaned_text: string;
  language: string;
  final_label: string;
  confidence: number;
  model_results: ModelResult[];
  rag_context: string[];
  report_summary?: string;
  created_at: string;
};

export async function analyzeText(text: string, model_name: string, use_rag: boolean) {
  const res = await api.post<AnalyzeResponse>("/analyze", { text, model_name, use_rag });
  return res.data;
}

export async function getHistory() {
  const res = await api.get("/history");
  return res.data;
}

export async function getModels() {
  const res = await api.get("/models");
  return res.data;
}

export async function downloadReport(ids: number[], format: "pdf" | "csv" | "json" = "pdf") {
  const res = await api.post(
    "/report",
    { analysis_ids: ids, export_format: format, include_charts: true },
    { responseType: format === "json" ? "json" : "blob" }
  );
  return res.data;
}
