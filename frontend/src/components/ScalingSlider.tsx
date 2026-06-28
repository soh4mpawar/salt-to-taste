"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useRecipeStore } from "@/store/recipeStore";
import { formatSalt } from "@/lib/utils";
import { Users } from "lucide-react";

export function ScalingSlider({ recipeId, originalServings }: {
  recipeId: string;
  originalServings: number;
}) {
  const { targetServings, setTargetServings } = useRecipeStore();
  const [sliderValue, setSliderValue] = useState(originalServings);

  const { data, isFetching } = useQuery({
    queryKey: ["scale", recipeId, targetServings],
    queryFn: () => api.scaleRecipe(recipeId, targetServings),
    enabled: targetServings !== originalServings,
  });

  return (
    <div className="p-4 bg-salt-50 rounded-2xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users size={18} className="text-umami-500" />
          <span className="font-semibold text-salt-900">Servings</span>
        </div>
        <span className="text-2xl font-bold text-umami-500">{sliderValue}</span>
      </div>

      <input
        type="range"
        min={1}
        max={24}
        value={sliderValue}
        onChange={(e) => {
          const val = Number(e.target.value);
          setSliderValue(val);
          // Debounce: update store value after 500ms
          setTimeout(() => setTargetServings(val), 500);
        }}
        className="w-full accent-umami-400 h-2"
      />

      <div className="flex justify-between text-xs text-salt-700 font-medium">
        <span>1</span>
        <span>6</span>
        <span>12</span>
        <span>18</span>
        <span>24</span>
      </div>

      {isFetching && (
        <p className="text-center text-sm text-umami-500 animate-pulse">
          Recalculating...
        </p>
      )}

      {data && !isFetching && (
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-white rounded-xl">
            <span className="text-sm text-salt-700 font-medium">Salt needed</span>
            <span className="font-bold text-salt-900">
              {formatSalt(data.scaled_salt_grams, data.salt_type)}
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white rounded-xl">
            <span className="text-sm text-salt-700 font-medium">Sodium per serving</span>
            <span className="font-bold text-salt-900">
              {data.sodium_info.sodium_mg_per_serving.toFixed(0)}mg
            </span>
          </div>
          {data.salt_saved_grams > 0.1 && (
            <p className="text-xs text-center text-fresh-500">
              Sub-linear scaling saves {data.salt_saved_grams.toFixed(1)}g vs
              naively multiplying
            </p>
          )}
          {data.scaled_ingredients.length > 0 && (
            <details className="text-sm">
              <summary className="text-salt-700 font-medium cursor-pointer">
                All ingredients scaled
              </summary>
              <ul className="mt-2 space-y-1">
                {data.scaled_ingredients.map((ing, i) => (
                  <li key={i} className="flex justify-between py-1 border-b border-salt-100">
                    <span className="text-salt-700">{ing.name}</span>
                    <span className="font-medium text-salt-900">{ing.amount} {ing.unit}</span>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </div>
  );
}
