"use client";
import { useRecipeStore } from "@/store/recipeStore";
import { Heart } from "lucide-react";

export function LowSodiumToggle() {
  const { lowSodiumMode, setLowSodiumMode } = useRecipeStore();
  return (
    <button
      onClick={() => setLowSodiumMode(!lowSodiumMode)}
      className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium border transition-all min-h-touch
        ${lowSodiumMode
          ? "border-fresh-400 bg-fresh-400 text-white"
          : "border-salt-200 text-salt-500"
        }`}
    >
      <Heart size={16} fill={lowSodiumMode ? "white" : "none"} />
      Low Sodium Mode
    </button>
  );
}
