"use client";
import { useEffect } from "react";
import { X } from "lucide-react";

export function BottomSheet({ isOpen, onClose, title, children }: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (isOpen) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  return (
    <div className={`fixed inset-0 z-50 transition-all duration-300 ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none invisible'}`}>
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-salt-900">{title}</h2>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-salt-100">
            <X size={20} />
          </button>
        </div>
        <div className="overflow-y-auto max-h-[80vh] pb-8">
          {children}
        </div>
      </div>
    </div>
  );
}
