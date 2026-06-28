"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, DEFAULT_USER_ID } from "@/lib/api";
import { Clock, Loader2, RotateCcw, ArrowRight } from "lucide-react";
import { toast } from "react-hot-toast";

const formatDate = (isoString: string) => {
  if (!isoString) return "Unknown date";
  try {
    return new Date(isoString).toLocaleDateString("en-US", {
      month: "short", day: "numeric", year: "numeric",
    });
  } catch {
    return "Unknown date";
  }
};

export default function HistoryPage() {
  const queryClient = useQueryClient();

  const { data: palateSummary, isPending: p1 } = useQuery({
    queryKey: ["palateSummary"],
    queryFn: () => api.getPalateSummary(DEFAULT_USER_ID),
  });

  const { data: history, isPending: p2 } = useQuery({
    queryKey: ["palateHistory"],
    queryFn: () => api.getPalateHistory(DEFAULT_USER_ID),
  });

  const resetMutation = useMutation({
    mutationFn: () => api.resetPalate(DEFAULT_USER_ID),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["palateSummary"] });
      queryClient.invalidateQueries({ queryKey: ["palateHistory"] });
      toast.success("Palate reset to baseline");
    }
  });

  if (p1 || p2) return <div className="flex justify-center p-12"><Loader2 className="animate-spin text-salt-400" /></div>;

  return (
    <main className="max-w-[500px] w-full mx-auto p-4 flex flex-col gap-6 bg-white min-h-screen">
      <header className="flex items-center gap-2 text-umami-500 py-2">
        <Clock size={28} strokeWidth={2.5} />
        <h1 className="text-2xl font-display font-bold tracking-tight">History</h1>
      </header>

      {/* Palate Profile Status */}
      <section className="bg-umami-50 p-5 rounded-2xl border border-umami-100">
        <h2 className="font-semibold text-salt-900 mb-3">Palate Profile Status</h2>
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-salt-700">Model Status</span>
            <span className={`text-sm font-medium ${palateSummary?.model_trained ? "text-fresh-500" : "text-salt-500"}`}>
              {palateSummary?.model_trained ? "✓ Model trained" : "Not yet trained — submit feedback to begin"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-salt-700">Total Feedback</span>
            <span className="text-sm font-bold text-salt-900">{palateSummary?.total_feedback_count ?? 0}</span>
          </div>
          {palateSummary?.last_updated && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-salt-700">Last Updated</span>
              <span className="text-sm text-salt-700" suppressHydrationWarning>{formatDate(palateSummary.last_updated)}</span>
            </div>
          )}
        </div>

        <button
          onClick={() => {
            if (window.confirm("Are you sure you want to reset your ML palate profile?")) {
              resetMutation.mutate();
            }
          }}
          disabled={resetMutation.isPending}
          className="mt-4 px-4 py-2 bg-white text-red-600 text-sm font-medium rounded-lg border border-red-200 flex items-center gap-2 hover:bg-red-50"
        >
          <RotateCcw size={16} />
          Reset Palate
        </button>
      </section>

      {/* Feedback History */}
      <section>
        <h3 className="font-semibold text-salt-900 mb-4">Feedback History</h3>
        <div className="flex flex-col gap-3">
          {(history ?? []).map((entry: any, i: number) => {
            let emoji = "✅";
            let color = "text-green-700 bg-green-50";
            if (entry.rating === "too_salty") { emoji = "🧂"; color = "text-red-700 bg-red-50"; }
            else if (entry.rating === "needs_more") { emoji = "😶"; color = "text-blue-700 bg-blue-50"; }

            const dateStr = entry.created_at || entry.timestamp;

            return (
              <div key={i} className="p-4 border border-salt-200 rounded-xl flex gap-4 items-center bg-white shadow-sm">
                <div className={`w-12 h-12 flex items-center justify-center rounded-full text-xl ${color}`}>
                  {emoji}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-salt-900">{entry.recipe_title || entry.recommendation_context?.dish_type || "Dish"}</p>
                  <p className="text-xs text-salt-700 mt-0.5" suppressHydrationWarning>{formatDate(dateStr)}</p>

                  <div className="mt-2 text-sm flex items-center justify-between">
                    <span className="text-salt-700">Base: {entry.baseline_grams?.toFixed(1)}g</span>
                    <ArrowRight size={14} className="text-salt-500 mt-0.5" />
                    <span className="font-bold text-umami-600">{entry.personalized_grams?.toFixed(1)}g</span>
                  </div>
                </div>
              </div>
            );
          })}
          {(!history || (history as any[]).length === 0) && (
            <p className="text-sm text-salt-700 text-center py-4">No feedback history yet.</p>
          )}
        </div>
      </section>
    </main>
  );
}
