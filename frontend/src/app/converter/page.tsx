"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatSalt } from "@/lib/utils";
import { Beaker, ArrowRight, Loader2 } from "lucide-react";

export default function ConverterPage() {
  const [fromSalt, setFromSalt] = useState("Diamond Crystal Kosher");
  const [toSalt, setToSalt] = useState("Morton Kosher");
  const [amount, setAmount] = useState<number>(5);
  const [unit, setUnit] = useState<"grams" | "tsp">("grams");
  const [showAll, setShowAll] = useState(false);

  const { data: saltTypes, isPending: isLoadingSalts } = useQuery({
    queryKey: ["saltTypes"],
    queryFn: () => api.getSaltTypes(),
  });

  const amountInGrams = unit === "grams" ? amount : amount * (saltTypes?.find(s => s.name === fromSalt)?.density_g_per_ml || 5) * 4.92892;

  const { data: conversion, isPending: isConverting } = useQuery({
    queryKey: ["convert", fromSalt, toSalt, amountInGrams],
    queryFn: () => api.convertSalt(fromSalt, toSalt, amountInGrams),
    enabled: !!saltTypes && amountInGrams > 0,
  });

  return (
    <main className="max-w-[500px] w-full mx-auto p-4 flex flex-col gap-6 bg-white min-h-screen">
      <header className="flex items-center gap-2 text-umami-500 py-2">
        <Beaker size={28} strokeWidth={2.5} />
        <h1 className="text-2xl font-display font-bold tracking-tight">Converter</h1>
      </header>

      {isLoadingSalts ? (
         <div className="flex justify-center p-8"><Loader2 className="animate-spin text-salt-400" /></div>
      ) : (
        <div className="flex flex-col gap-4">
          <div className="flex gap-2">
             <div className="flex flex-col gap-2 flex-1">
                <label className="text-sm font-semibold text-salt-900">Amount</label>
               <input type="number" value={amount} onChange={e => setAmount(Number(e.target.value))} className="px-4 py-3 border border-salt-200 rounded-xl placeholder:text-salt-500 text-salt-900 font-medium" placeholder="e.g. 5" />
             </div>
             <div className="flex flex-col gap-2 flex-1">
               <label className="text-sm font-semibold text-salt-900">Unit</label>
               <select value={unit} onChange={e => setUnit(e.target.value as any)} className="px-4 py-3 border border-salt-200 rounded-xl bg-white">
                 <option value="grams">Grams</option>
                 <option value="tsp">Teaspoons</option>
               </select>
             </div>
          </div>
          
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-salt-900">From Salt</label>
            <select value={fromSalt} onChange={e => setFromSalt(e.target.value)} className="px-4 py-3 border border-salt-200 rounded-xl bg-white text-salt-900 font-medium">
              <option value="" disabled>Select salt type</option>
              {(saltTypes ?? []).map(s => <option key={s.id} value={s.name}>{s.name}</option>)}
            </select>
          </div>

          <div className="flex justify-center text-salt-400 py-1">
            <ArrowRight size={24} className="rotate-90" />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-salt-900">To Salt</label>
            <select value={toSalt} onChange={e => setToSalt(e.target.value)} className="px-4 py-3 border border-salt-200 rounded-xl bg-white text-salt-900 font-medium">
              <option value="" disabled>Select salt type</option>
              {(saltTypes ?? []).map(s => <option key={s.id} value={s.name}>{s.name}</option>)}
            </select>
          </div>

          <div className="mt-2 p-6 bg-salt-50 rounded-2xl border border-salt-200 text-center">
            {isConverting ? (
              <Loader2 className="animate-spin mx-auto text-umami-500" />
            ) : conversion ? (
              <>
                <p className="text-sm text-salt-500 font-medium mb-1 uppercase tracking-wider">Equivalent</p>
                <p className="text-5xl font-bold text-salt-900 mb-2">
                  {conversion.converted_grams.toFixed(1)}g
                </p>
                <p className="text-lg text-salt-600 font-medium">{formatSalt(conversion.converted_grams, toSalt)}</p>
              </>
            ) : null}
          </div>

          <button onClick={() => setShowAll(!showAll)} className="mt-4 text-umami-600 font-medium border border-umami-200 rounded-xl py-3 hover:bg-umami-50 transition-colors">
            {showAll ? "Hide Compare All" : "Compare All"}
          </button>

          {showAll && saltTypes && conversion && (
             <div className="mt-4 rounded-xl border border-salt-200 overflow-hidden text-sm">
                <table className="w-full text-left">
                  <thead className="bg-salt-100 text-salt-600">
                    <tr><th className="p-3 font-medium">Salt Type</th><th className="p-3 font-medium text-right">Grams</th></tr>
                  </thead>
                  <tbody>
                    {(saltTypes ?? []).map(s => (
                       <tr key={s.id} className="border-t border-salt-100">
                          <td className="p-3 font-medium text-salt-900">{s.name}</td>
                          <td className="p-3 text-right">{((amountInGrams / (saltTypes ?? []).find(x => x.name === fromSalt)!.sodium_mg_per_gram) * s.sodium_mg_per_gram).toFixed(1)}g</td>
                       </tr>
                    ))}
                  </tbody>
                </table>
             </div>
          )}
        </div>
      )}
    </main>
  );
}
