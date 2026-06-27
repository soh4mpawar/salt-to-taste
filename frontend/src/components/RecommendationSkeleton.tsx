"use client";
export function RecommendationSkeleton() {
  return (
    <div className="flex flex-col gap-6 p-4 bg-white rounded-2xl shadow-sm border border-salt-200 mt-6 animate-pulse">
      <div className="text-center py-8 bg-salt-100 rounded-2xl border border-salt-200 h-48" />
      <div className="flex flex-wrap items-center justify-center gap-2">
        <div className="w-20 h-6 bg-salt-100 rounded-full" />
        <div className="w-24 h-6 bg-salt-100 rounded-full" />
      </div>
      <div className="mt-2">
        <div className="w-24 h-4 bg-salt-200 mx-auto mb-4 rounded" />
        <div className="grid grid-cols-3 gap-2 h-24">
           <div className="bg-salt-100 rounded-xl" />
           <div className="bg-salt-100 rounded-xl" />
           <div className="bg-salt-100 rounded-xl" />
        </div>
      </div>
      <div className="border-t border-salt-200 pt-5 mt-2 flex flex-col gap-2">
         <div className="w-24 h-4 bg-salt-200 mb-2 rounded" />
         <div className="h-12 bg-salt-100 rounded-xl" />
         <div className="h-12 bg-salt-100 rounded-xl" />
         <div className="h-12 bg-salt-100 rounded-xl" />
      </div>
    </div>
  );
}
