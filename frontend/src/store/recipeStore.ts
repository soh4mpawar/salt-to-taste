"use client";
import { create } from "zustand";
import type { RecommendationRead, ScaleResult } from "@/lib/api";

interface RecipeStore {
  // Current recommendation from the pipeline
  currentRecommendation: RecommendationRead | null;
  setCurrentRecommendation: (rec: RecommendationRead | null) => void;

  // Scaling state
  targetServings: number;
  setTargetServings: (n: number) => void;
  scaleResult: ScaleResult | null;
  setScaleResult: (r: ScaleResult | null) => void;

  // Input mode
  inputMode: "text" | "url" | "image";
  setInputMode: (m: "text" | "url" | "image") => void;

  // Low sodium preference
  lowSodiumMode: boolean;
  setLowSodiumMode: (v: boolean) => void;

  // Clear everything
  reset: () => void;
}

export const useRecipeStore = create<RecipeStore>((set) => ({
  currentRecommendation: null,
  setCurrentRecommendation: (rec) => set({ currentRecommendation: rec }),
  targetServings: 4,
  setTargetServings: (n) => set({ targetServings: n }),
  scaleResult: null,
  setScaleResult: (r) => set({ scaleResult: r }),
  inputMode: "text",
  setInputMode: (m) => set({ inputMode: m }),
  lowSodiumMode: false,
  setLowSodiumMode: (v) => set({ lowSodiumMode: v }),
  reset: () => set({
    currentRecommendation: null,
    scaleResult: null,
    targetServings: 4,
  }),
}));
