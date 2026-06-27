"use client";
import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] p-6 text-center">
      <Loader2 className="animate-spin text-umami-400 mb-4" size={48} />
      <p className="text-salt-500 font-medium animate-pulse">Warming up the kitchen...</p>
    </div>
  );
}
