"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useRecipeStore } from "@/store/recipeStore";
import { toast } from "react-hot-toast";
import { Loader2, ChefHat } from "lucide-react";

export function RecipeUrlInput() {
  const [url, setUrl] = useState("");
  const { setCurrentRecommendation, lowSodiumMode } = useRecipeStore();

  const mutation = useMutation({
    mutationKey: ['submitRecipe'],
    mutationFn: () => api.submitRecipe({
      title: "Imported Recipe",
      source_type: "url",
      raw_content: url,
      low_sodium_mode: lowSodiumMode,
    }),
    onSuccess: (data) => {
      setCurrentRecommendation(data);
      toast.success("Recipe imported and analyzed!");
    },
    onError: () => toast.error("Failed to import recipe. Try again."),
  });

  return (
    <div className="flex flex-col gap-3">
      <input
        type="url"
        placeholder="Paste recipe URL here..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="w-full px-4 py-3 rounded-xl border border-salt-200 text-salt-900 placeholder:text-salt-500 focus:outline-none focus:ring-2 focus:ring-umami-400 min-h-touch"
      />
      <button
        onClick={() => mutation.mutate()}
        disabled={!url.trim() || mutation.isPending}
        className="w-full flex items-center justify-center gap-2 py-4 rounded-xl bg-umami-400 text-white font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 transition-all min-h-touch"
      >
        {mutation.isPending ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            Analyzing recipe...
          </>
        ) : (
          <>
            <ChefHat size={20} />
            Get Salt Measurement
          </>
        )}
      </button>
      {mutation.isPending && (
        <p className="text-center text-sm text-salt-500">
          AI is analyzing your recipe — this takes 30-60 seconds
        </p>
      )}
    </div>
  );
}
