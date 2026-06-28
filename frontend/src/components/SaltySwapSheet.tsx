"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { BottomSheet } from "./BottomSheet";
import { Loader2 } from "lucide-react";
import { formatSalt } from "@/lib/utils";
import { useRecipeStore } from "@/store/recipeStore";

export function SaltySwapSheet({ isOpen, onClose, recipeId, recommendationId }: { isOpen: boolean, onClose: () => void, recipeId: string, recommendationId: string }) {
  const [ingredient, setIngredient] = useState("");
  const [amount, setAmount] = useState("");
  const [unit, setUnit] = useState("tbsp");
  const [swapResult, setSwapResult] = useState<any>(null);
  const { currentRecommendation } = useRecipeStore();

  const mutation = useMutation({
    mutationFn: () => api.saltySwap(recommendationId, ingredient, Number(amount), unit),
    onSuccess: (data) => {
      setSwapResult(data);
    }
  });

  return (
    <BottomSheet isOpen={isOpen} onClose={onClose} title="Salty Swap">
      {!mutation.data ? (
        <div className="flex flex-col gap-4">
          <p className="text-sm text-salt-700">
            Added something salty to the pot mid-cook? Tell us what you added and we’ll recalculate your final salt.
          </p>
          <div className="flex flex-col gap-3">
            <input 
              type="text" 
              placeholder="e.g. Soy Sauce, Parmesan, Miso" 
              value={ingredient} 
              onChange={e => setIngredient(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-salt-200 text-gray-900 placeholder:text-gray-700"
            />
            <div className="flex gap-2 text-gray-900">
              <input 
                type="number" 
                placeholder="Amount" 
                value={amount} 
                onChange={e => setAmount(e.target.value)}
                className="w-1/2 px-4 py-3 rounded-xl border border-salt-200 placeholder:text-gray-700"
              />
              <select 
                value={unit} 
                onChange={e => setUnit(e.target.value)}
                className="w-1/2 px-4 py-3 rounded-xl border border-salt-200 bg-white text-gray-900 placeholder:text-gray-500"
              >
                <option className="text-gray-900 bg-white" value="g">Grams (g)</option>
                <option className="text-gray-900 bg-white" value="ml">mL</option>
                <option className="text-gray-900 bg-white" value="tsp">Teaspoons (tsp)</option>
                <option className="text-gray-900 bg-white" value="tbsp">Tablespoons (tbsp)</option>
                <option className="text-gray-900 bg-white" value="cup">Cups</option>
              </select>
            </div>
            <button 
              onClick={() => mutation.mutate()} 
              disabled={!ingredient || !amount || mutation.isPending}
              className="w-full py-4 bg-umami-400 text-white font-bold rounded-xl mt-2 disabled:opacity-50 min-h-touch flex justify-center items-center gap-2"
            >
              {mutation.isPending ? <Loader2 className="animate-spin" /> : "Adjust Salt"}
            </button>
            {swapResult && (
              <div className="p-4 bg-fresh-50 rounded-xl border border-fresh-400 mt-3">
                <p className="text-sm text-fresh-600 font-medium mb-1">Updated salt amount</p>
                <p className="text-3xl font-bold text-salt-900">
                  {formatSalt(swapResult.adjusted_grams ?? 0, currentRecommendation?.salt_type_name || "Diamond Crystal Kosher")}
                </p>
                <p className="text-sm text-salt-700 mt-2">{swapResult.recommendation}</p>
                {swapResult.warning && (
                  <p className="text-xs text-amber-600 mt-1">{swapResult.warning}</p>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          <div className="text-center p-6 bg-fresh-50 rounded-2xl border border-fresh-200">
            <p className="text-sm text-fresh-600 font-medium mb-1">NEW SALT AMOUNT</p>
            <p className="text-5xl font-bold text-salt-900">
              {formatSalt(mutation.data.adjusted_grams, currentRecommendation?.salt_type_name || "Diamond Crystal Kosher")}
            </p>
            <div className="flex items-center justify-center gap-2 mt-4 text-salt-700 line-through">
               <span>Original: {formatSalt(mutation.data.original_recommendation_grams, currentRecommendation?.salt_type_name)}</span>
            </div>
          </div>
          <p className="text-sm text-salt-700 p-3 bg-salt-50 rounded-lg">
            {mutation.data.recommendation}
          </p>
          <button onClick={() => { mutation.reset(); onClose(); }} className="w-full py-4 text-salt-700 font-bold bg-salt-100 rounded-xl mt-2 min-h-touch">
            Done
          </button>
        </div>
      )}
    </BottomSheet>
  );
}
