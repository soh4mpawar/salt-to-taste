"use client";
import { useRecipeStore } from "@/store/recipeStore";
import { FileText, Link, Camera } from "lucide-react";

const modes = [
  { id: "text", label: "Text", icon: FileText },
  { id: "url", label: "URL", icon: Link },
  { id: "image", label: "Photo", icon: Camera },
] as const;

export function InputModeToggle() {
  const { inputMode, setInputMode } = useRecipeStore();
  return (
    <div className="flex bg-salt-100 rounded-xl p-1 gap-1">
      {modes.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => setInputMode(id)}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all min-h-touch
            ${inputMode === id
              ? "bg-white text-umami-500 shadow-sm"
              : "text-salt-500 hover:text-salt-900"
            }`}
        >
          <Icon size={16} />
          {label}
        </button>
      ))}
    </div>
  );
}
