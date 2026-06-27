"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { BottomSheet } from "./BottomSheet";
import { Loader2 } from "lucide-react";
import { getSeverityColor } from "@/lib/utils";
import { toast } from "react-hot-toast";

export function RescueSheet({ isOpen, onClose, recommendationId, rescueResult, setRescueResult }: { isOpen: boolean, onClose: () => void, recommendationId: string, rescueResult: any, setRescueResult: (data: any) => void }) {
  const [addedGrams, setAddedGrams] = useState<number>(5);

  const mutation = useMutation({
    mutationFn: () => api.rescue(recommendationId, addedGrams),
    onSuccess: (data) => {
      console.log('rescueResult:', data);
      setRescueResult(data); // keep this
    },
    onError: () => toast.error("Could not get rescue strategies — check the recommendation ID")
  });

  return (
    <BottomSheet isOpen={isOpen} onClose={onClose} title="Rescue Protocol">
      {!rescueResult ? (
        <div className="flex flex-col gap-4">
          <p className="text-sm text-gray-600">
            Oh no! Over-salted your dish? Tell us how much salt you accidentally put in, and we’ll give you culinary strategies to fix it.
          </p>
          <div className="flex flex-col gap-2 mt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-salt-900">Total added</span>
              <span className="text-2xl font-bold text-danger-500">{addedGrams}g</span>
            </div>
            <input 
              type="range" min="0" max="30" step="0.5"
              value={addedGrams} onChange={e => setAddedGrams(Number(e.target.value))}
              className="w-full accent-danger-400 h-2"
            />
          </div>
          <button 
            onClick={() => mutation.mutate()} 
            disabled={mutation.isPending}
            className="w-full py-4 bg-danger-500 text-white font-bold rounded-xl mt-6 disabled:opacity-50 min-h-touch flex justify-center items-center gap-2"
          >
            {mutation.isPending ? <Loader2 className="animate-spin" /> : "Save My Dish"}
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          <div className="p-4 rounded-xl border bg-salt-50 flex flex-col gap-2">
             <div className="flex justify-between items-start">
               <span className="font-bold text-salt-900">Severity</span>
               <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${getSeverityColor(rescueResult.severity)}`}>
                 {rescueResult.severity}
               </span>
             </div>
             {rescueResult.excess_salt_grams != null && (
               <p className="text-sm text-salt-700 font-medium">Excess salt: {rescueResult.excess_salt_grams?.toFixed(1) ?? '0.0'}g</p>
             )}
          </div>
          
          <div className="p-4 bg-danger-50 rounded-xl border border-danger-200">
             <p className="font-bold text-danger-700 mb-1">Primary Recommendation</p>
             <p className="text-sm text-danger-900">{rescueResult.primary_recommendation ?? rescueResult.message ?? 'No action needed'}</p>
          </div>
          
          {rescueResult.severity === 'none' ? (
             <div className="p-4 bg-green-50 border border-green-200 rounded-xl mt-2">
                <p className="text-sm text-green-800 font-medium">{rescueResult.message}</p>
             </div>
          ) : (
             <div className="space-y-3 mt-2">
                {(rescueResult.strategies ?? []).map((strategy: any, i: number) => (
                   <div key={i} className="p-3 border border-salt-200 rounded-xl" style={{ borderLeftWidth: '4px', borderLeftColor: '#c5221f' }}>
                      <div className="flex justify-between items-center mb-1">
                         <span className="font-bold text-salt-900">{strategy.strategy}</span>
                         <span className="text-xs font-medium px-2 py-0.5 bg-salt-100 rounded-md text-salt-600">{strategy.effectiveness}</span>
                      </div>
                      <p className="text-sm text-salt-800 font-medium">{strategy.action}</p>
                      <p className="text-xs text-salt-700 mt-1">{strategy.detail}</p>
                   </div>
                ))}
             </div>
          )}
          
          <button onClick={() => { setRescueResult(null); mutation.reset(); onClose(); }} className="w-full py-4 text-salt-700 font-bold bg-salt-100 rounded-xl mt-2 min-h-touch">
            Done
          </button>
        </div>
      )}
    </BottomSheet>
  );
}
