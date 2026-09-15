import { create } from "zustand";
import type { AnalyzeResponse } from "../services/api";

type AppState = {
  lastResult?: AnalyzeResponse;
  setLastResult: (result: AnalyzeResponse) => void;
};

export const useAppStore = create<AppState>((set) => ({
  lastResult: undefined,
  setLastResult: (result) => set({ lastResult: result })
}));
