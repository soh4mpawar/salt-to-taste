"use client";
import { useState, useEffect, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useRecipeStore } from "@/store/recipeStore";
import { formatSalt } from "@/lib/utils";
import { toast } from "react-hot-toast";
import { AlertTriangle, Info, PlusCircle, Scale, LifeBuoy, RotateCcw } from "lucide-react";
import { ScalingSlider } from "@/components/ScalingSlider";
import { SaltySwapSheet } from "@/components/SaltySwapSheet";
import { RescueSheet } from "@/components/RescueSheet";


export function RecommendationCard() {
  const { currentRecommendation: recommendation, reset } = useRecipeStore();
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [showScaling, setShowScaling] = useState(false);
  const [showSwap, setShowSwap] = useState(false);
  const [showRescue, setShowRescue] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (recommendation && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [recommendation]);

  const feedbackMutation = useMutation({
    mutationFn: (rating: "perfect" | "too_salty" | "needs_more") => 
      api.submitFeedback(recommendation!.id, rating),
    onSuccess: () => {
      setFeedbackSent(true);
      toast.success("Thanks! Your palate profile is updating...");
    },
    onError: () => toast.error("Failed to submit feedback"),
  });

  if (!recommendation) return null;

  const context = recommendation.recommendation_context;

  return (
    <div ref={cardRef} className="flex flex-col gap-6 p-4 bg-white rounded-2xl shadow-sm border border-salt-200 mt-6">
      
      {/* Section A — The Number */}
      <div className="text-center py-8 bg-gradient-to-b from-umami-50 to-white rounded-2xl border border-umami-100">
        <p className="text-sm font-medium text-umami-500 uppercase tracking-widest mb-2">
          Add to your dish
        </p>
        <p className="text-6xl font-bold text-salt-900">
          {formatSalt(recommendation.personalized_grams, recommendation.salt_type_name)}
        </p>
        <p className="text-lg text-salt-500 mt-1">
          {recommendation.salt_type_name}
        </p>
        <p className="text-sm text-salt-500 mt-2">
          {recommendation.sodium_mg_per_serving.toFixed(0)}mg sodium per serving
        </p>
      </div>

      {/* Section B — Dish Context Badge */}
      <div className="flex flex-wrap items-center justify-center gap-2">
        {context?.dish_type && (
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-salt-200 text-salt-900">
            {context.dish_type}
          </span>
        )}
        {context?.cooking_method && (
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-salt-200 text-salt-900">
            {context.cooking_method}
          </span>
        )}
      </div>

      {/* Section C — Hidden Sodium Alert */}
      {context?.hidden_sodium_mg > 100 && (
        <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-xl border border-amber-200">
          <AlertTriangle size={18} className="text-amber-500 mt-0.5 shrink-0" />
          <p className="text-sm text-amber-800">
            Hidden sodium detected from salty ingredients ({context.hidden_sodium_mg.toFixed(0)}mg).
            Raw salt recommendation already reduced.
          </p>
        </div>
      )}

      {/* Section D — Low Sodium Warning */}
      {recommendation.low_sodium_warning && (
        <div className="flex items-start gap-3 p-3 bg-fresh-50 rounded-xl border border-fresh-200">
          <Info size={18} className="text-fresh-500 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm text-fresh-800 mb-2">
              {recommendation.low_sodium_warning}
            </p>
            {recommendation.herb_suggestions && recommendation.herb_suggestions.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1">
                {recommendation.herb_suggestions.map((herb, i) => (
                  <span key={i} className="px-2 py-0.5 bg-white text-fresh-600 rounded text-xs border border-fresh-200">
                    {herb}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Section E — Feedback Buttons */}
      <div className="mt-2">
        <h3 className="text-sm font-semibold text-salt-900 mb-3 text-center">How was it?</h3>
        {feedbackSent ? (
          <div className="text-center py-4">
            <p className="text-fresh-600 font-semibold text-lg">✓ Feedback recorded</p>
            <p className="text-salt-700 text-sm mt-1">Your palate profile has been updated</p>
            <button
              onClick={() => { setFeedbackSent(false); reset(); }}
              className="w-full mt-4 py-3 flex items-center justify-center gap-2 bg-salt-100 text-salt-700 rounded-xl font-medium min-h-touch"
            >
              <RotateCcw size={18} /> New Recipe
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-2">
            {[
              { rating: "too_salty" as const, label: "Too Salty", emoji: "🧂", color: "border-red-200 text-red-600 hover:bg-red-50" },
              { rating: "perfect" as const, label: "Perfect", emoji: "✅", color: "border-green-200 text-green-600 hover:bg-green-50" },
              { rating: "needs_more" as const, label: "Needs More", emoji: "😶", color: "border-blue-200 text-blue-600 hover:bg-blue-50" },
            ].map(({ rating, label, emoji, color }) => (
              <button
                key={rating}
                onClick={() => feedbackMutation.mutate(rating)}
                disabled={feedbackMutation.isPending}
                className={`flex flex-col items-center gap-1 py-3 rounded-xl border-2 font-medium text-sm transition-all min-h-touch ${color} disabled:opacity-40`}
              >
                <span className="text-xl">{emoji}</span>
                {label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="border-t border-salt-200 pt-5 mt-2">
        <h3 className="text-sm font-semibold text-salt-900 mb-3">Quick Actions</h3>
        <div className="flex flex-col gap-2">
          <button 
            onClick={() => setShowScaling(!showScaling)}
            className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-salt-300 bg-salt-50 text-salt-900 font-medium min-h-touch hover:bg-salt-100 transition-colors"
          >
            <span className="flex items-center gap-3"><Scale size={18} /> Scale Recipe</span>
          </button>

          {showScaling && (
            <ScalingSlider 
              recipeId={recommendation.recipe_id} 
              originalServings={4} 
            />
          )}

          <button 
            onClick={() => setShowSwap(true)}
            className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-salt-300 bg-salt-50 text-salt-900 font-medium min-h-touch hover:bg-salt-100 transition-colors"
          >
            <span className="flex items-center gap-3"><PlusCircle size={18} /> Salty Swap</span>
          </button>
          <button 
            onClick={() => setShowRescue(true)}
            className="w-full py-3 px-4 flex items-center justify-between text-left text-danger-500 bg-white border border-danger-200 hover:bg-danger-50 rounded-xl transition-colors font-medium min-h-touch"
          >
            <span className="flex items-center gap-2"><LifeBuoy size={18} /> Help! Too Salty!</span>
          </button>
        </div>
      </div>

      <SaltySwapSheet 
        isOpen={showSwap} 
        onClose={() => setShowSwap(false)} 
        recipeId={recommendation.recipe_id} 
        recommendationId={recommendation.id} 
      />
      <RescueSheet
        isOpen={showRescue}
        onClose={() => setShowRescue(false)}
        recommendationId={recommendation.id}
      />
    </div>
  );
}
