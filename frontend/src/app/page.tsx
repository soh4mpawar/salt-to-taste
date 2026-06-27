"use client";
import { InputModeToggle } from "@/components/InputModeToggle";
import { RecipeTextInput } from "@/components/RecipeTextInput";
import { RecipeUrlInput } from "@/components/RecipeUrlInput";
import { RecipeImageInput } from "@/components/RecipeImageInput";
import { LowSodiumToggle } from "@/components/LowSodiumToggle";
import { RecommendationCard } from "@/components/RecommendationCard";
import { RecommendationSkeleton } from "@/components/RecommendationSkeleton";
import { useRecipeStore } from "@/store/recipeStore";
import { Utensils } from "lucide-react";
import { useIsMutating } from "@tanstack/react-query";

export default function Home() {
  const { inputMode, currentRecommendation, lowSodiumMode } = useRecipeStore();
  const isMutating = useIsMutating();

  return (
    <main className="max-w-[500px] w-full mx-auto p-4 flex flex-col gap-6 bg-white min-h-screen">
      {/* Header */}
      <header className="flex items-center justify-between py-2">
        <div className="flex items-center gap-2 text-umami-500">
          <Utensils size={28} strokeWidth={2.5} />
          <h1 className="text-2xl font-display font-bold tracking-tight">Salt to Taste</h1>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-col gap-5">
        <InputModeToggle />
        
        {inputMode === "text" && <RecipeTextInput />}
        {inputMode === "url" && <RecipeUrlInput />}
        {inputMode === "image" && <RecipeImageInput />}

        <div className="flex flex-col items-center gap-2 mt-2">
          <LowSodiumToggle />
          {lowSodiumMode && (
            <p className="text-xs text-fresh-500 text-center">
              Low Sodium Mode active — applies to your next recipe submission
            </p>
          )}
        </div>
      </div>

      {/* Output */}
      {isMutating > 0 ? (
        <div className="mt-4 pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <RecommendationSkeleton />
        </div>
      ) : currentRecommendation ? (
        <div className="mt-4 pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <RecommendationCard />
        </div>
      ) : null}
    </main>
  );
}
