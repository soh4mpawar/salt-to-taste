"use client";
import { useState, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { api, DEFAULT_USER_ID } from "@/lib/api";
import { useRecipeStore } from "@/store/recipeStore";
import { toast } from "react-hot-toast";
import { Loader2, ChefHat, UploadCloud, X, FileText } from "lucide-react";

export function RecipeImageInput() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setCurrentRecommendation } = useRecipeStore();

  const mutation = useMutation({
    mutationKey: ['submitRecipe'],
    mutationFn: () => {
      if (!file) throw new Error("No file selected");
      return api.uploadRecipeImage(file, DEFAULT_USER_ID);
    },
    onSuccess: (data) => {
      setCurrentRecommendation(data);
      toast.success("Image analyzed!");
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to analyze image.");
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    
    if (selected.size > 10 * 1024 * 1024) {
      toast.error("File size must be under 10MB");
      return;
    }
    
    setFile(selected);
    if (selected.type.startsWith("image/")) {
      const url = URL.createObjectURL(selected);
      setPreview(url);
    } else {
      setPreview(null);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="flex flex-col gap-3">
      <input
        type="file"
        accept="image/*,.pdf"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
      />
      
      {!file ? (
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed border-salt-200 rounded-xl text-salt-500 hover:border-umami-400 hover:text-umami-400 transition-colors bg-salt-50 min-h-[200px]"
        >
          <UploadCloud size={40} />
          <div className="text-center">
            <p className="font-semibold text-salt-900">Tap to upload or take a photo</p>
            <p className="text-sm mt-1">Accepts JPEG, PNG, WEBP, or PDF (max 10MB)</p>
          </div>
        </button>
      ) : (
        <div className="relative w-full border border-salt-200 rounded-xl overflow-hidden bg-salt-50 p-2 flex flex-col items-center">
          <button 
            onClick={clearFile}
            className="absolute top-2 right-2 bg-white/80 p-1.5 rounded-full text-salt-900 hover:bg-white shadow-sm z-10"
          >
            <X size={16} />
          </button>
          
          {preview ? (
            <img src={preview} alt="Preview" className="w-full h-auto max-h-[300px] object-contain rounded-lg" />
          ) : (
            <div className="p-8 text-center w-full">
              <FileText size={40} className="mx-auto text-salt-400 mb-2" />
              <p className="font-medium text-salt-900 truncate px-4">{file.name}</p>
            </div>
          )}
        </div>
      )}

      <button
        onClick={() => mutation.mutate()}
        disabled={!file || mutation.isPending}
        className="w-full flex items-center justify-center gap-2 py-4 rounded-xl bg-umami-400 text-white font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 transition-all min-h-touch"
      >
        {mutation.isPending ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            Extracting text from image...
          </>
        ) : (
          <>
            <ChefHat size={20} />
            Analyze Cookbook Photo
          </>
        )}
      </button>
      
      {mutation.isPending && (
        <p className="text-center text-sm text-salt-500">
          Vision AI is extracting recipe details — this takes up to 60 seconds
        </p>
      )}
    </div>
  );
}
