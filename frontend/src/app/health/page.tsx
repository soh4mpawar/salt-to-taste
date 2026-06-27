"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, DEFAULT_USER_ID } from "@/lib/api";
import { Heart, Loader2 } from "lucide-react";
import { toast } from "react-hot-toast";

export default function HealthPage() {
  const queryClient = useQueryClient();
  const [editLimit, setEditLimit] = useState(false);
  const [limitVal, setLimitVal] = useState("");

  const { data: report, isPending, error } = useQuery({
    queryKey: ["healthReport"],
    queryFn: () => api.getSodiumReport(DEFAULT_USER_ID),
  });

  const mutation = useMutation({
    mutationFn: (newLimit: number) => api.updateSodiumLimit(DEFAULT_USER_ID, newLimit),
    onSuccess: () => {
       queryClient.invalidateQueries({ queryKey: ["healthReport"] });
       setEditLimit(false);
       toast.success("Limit updated");
    }
  });

  if (isPending) {
    return (
      <main className="max-w-[500px] w-full mx-auto p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-salt-100 rounded-xl w-48" />
          <div className="h-32 bg-salt-100 rounded-xl" />
          <div className="h-48 bg-salt-100 rounded-xl" />
        </div>
      </main>
    );
  }

  if (error || !report) {
    return (
      <main className="max-w-[500px] w-full mx-auto p-4">
        <p className="text-danger-400">Could not load health data.</p>
      </main>
    );
  }

  const todaySodium = report?.today?.total_sodium_mg ?? 0;
  const remaining = report?.today?.remaining_mg ?? report?.sodium_limit_mg ?? 2300;
  const percentUsed = report?.today?.percent_used ?? 0;
  const withinLimit = report?.today?.within_limit ?? true;
  const limitMg = report?.sodium_limit_mg ?? 2300;
  const weekly = report?.weekly_summary?.days ?? [];
  const weeklySummary = report?.weekly_summary;

  const barColor = percentUsed < 50 ? "bg-green-500" : percentUsed < 75 ? "bg-yellow-500" : "bg-red-500";
  
  // Find max day for relative scaling of the weekly chart
  const maxWeekly = Math.max(...weekly.map((d: any) => d.total_mg ?? 0), 1); // min 1 to avoid divide by zero

  return (
    <main className="max-w-[500px] w-full mx-auto p-4 flex flex-col gap-6 bg-white min-h-screen">
      <header className="flex items-center gap-2 text-umami-500 py-2">
        <Heart size={28} strokeWidth={2.5} />
        <h1 className="text-2xl font-display font-bold tracking-tight">Health Dashboard</h1>
      </header>

      {/* Today */}
      <section className="bg-salt-50 p-5 rounded-2xl border border-salt-200">
         <div className="flex justify-between items-end mb-2">
            <div>
               <h2 className="font-semibold text-salt-900">Today's Intake</h2>
               <p className="text-3xl font-bold mt-1 text-salt-900">{todaySodium.toFixed(0)} <span className="text-base font-normal text-salt-500">mg</span></p>
            </div>
            <div className="text-right">
               {editLimit ? (
                  <div className="flex gap-2">
                     <input type="number" value={limitVal} onChange={e => setLimitVal(e.target.value)} className="w-20 p-1 rounded border" placeholder={String(limitMg)} />
                     <button onClick={() => mutation.mutate(Number(limitVal))} className="text-umami-600 font-medium">Save</button>
                  </div>
               ) : (
                  <button onClick={() => { setLimitVal(String(limitMg)); setEditLimit(true); }} className="text-sm text-salt-500 underline decoration-dotted">
                     Limit: {limitMg}mg
                  </button>
               )}
            </div>
         </div>
         <div className="h-4 bg-salt-200 rounded-full overflow-hidden mt-3 relative">
            <div className={`h-full ${barColor} transition-all duration-1000`} style={{ width: `${Math.min(percentUsed, 100)}%` }} />
         </div>
         <p className="text-xs text-salt-500 mt-2 text-right">{Math.max(0, remaining).toFixed(0)}mg remaining</p>
      </section>

      {/* Weekly Chart */}
      <section>
         <h3 className="font-semibold text-salt-900 mb-4">Weekly Summary</h3>
         <div className="flex items-end justify-between h-40 bg-white border-b border-salt-200 pb-2 gap-2 relative">
            {/* Limit Line */}
            <div className="absolute w-full border-t-2 border-dashed border-salt-300" style={{ bottom: `${(limitMg / maxWeekly) * 100}%` }} />
            {(weekly ?? []).map((day: any) => {
               const dayPct = (day.total_mg / maxWeekly) * 100;
               const isOver = day.total_mg > limitMg;
               return (
                  <div key={day.date} className="flex flex-col items-center flex-1 gap-2 z-10 group relative">
                  <div className="w-full max-w-[32px] rounded-t-sm" style={{ height: `${Math.max(4, Math.min(100, ((day.total_mg ?? 0) / maxWeekly) * 100))}%`, backgroundColor: day.within_limit ? "#34a853" : "#ea4335" }} />
                     <span className="text-[10px] text-salt-500 font-medium uppercase" suppressHydrationWarning>{new Date(day.date).toLocaleDateString('en-US', {weekday: 'short'})}</span>
                     
                     <div className="absolute -top-8 bg-salt-900 text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {day.total_mg.toFixed(0)} mg
                     </div>
                  </div>
               );
            })}
         </div>

         {/* Weekly stats row */}
         {weeklySummary && (
           <div className="flex gap-4 mt-4 text-sm">
             <div className="flex-1 bg-salt-50 rounded-xl p-3 text-center border border-salt-200">
               <p className="text-xs text-salt-500 mb-1">Daily Average</p>
               <p className="font-bold text-salt-900">{weeklySummary.average_daily_mg?.toFixed(0) ?? "—"}<span className="text-xs font-normal text-salt-500"> mg</span></p>
             </div>
             <div className="flex-1 bg-fresh-400/10 rounded-xl p-3 text-center border border-fresh-400/20">
               <p className="text-xs text-salt-500 mb-1">Days Within Limit</p>
               <p className="font-bold text-fresh-500">{weeklySummary.days_within_limit ?? "—"}<span className="text-xs font-normal text-salt-500"> / 7</span></p>
             </div>
           </div>
         )}
      </section>

      {/* Recent Recipes */}
      <section>
        <div className="bg-white rounded-2xl border border-salt-200 p-4 space-y-3">
          <h3 className="font-semibold text-salt-900 mb-3">Recent Recipes</h3>
          <div className="flex justify-between items-center">
            <span className="text-salt-700">Recipes analyzed</span>
            <span className="font-bold text-salt-900">{report?.recent_recipes?.count ?? 0}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-salt-700">Avg sodium per serving</span>
            <span className="font-bold text-salt-900">
              {(report?.recent_recipes?.average_sodium_per_serving_mg ?? 0).toFixed(0)}mg
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-salt-700">Trend</span>
            <span className={`font-medium px-2 py-1 rounded-full text-sm ${
              report?.recent_recipes?.trending === "high"
                ? "bg-danger-400 text-white"
                : "bg-fresh-400 text-white"
            }`}>
              {report?.recent_recipes?.trending ?? "normal"}
            </span>
          </div>
          {(report?.recommendations ?? []).map((rec: string, i: number) => (
            <p key={i} className="text-sm text-salt-700 bg-salt-50 p-3 rounded-xl border border-salt-200">
              {rec}
            </p>
          ))}
        </div>
      </section>
    </main>
  );
}
