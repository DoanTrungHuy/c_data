"use client";

import React, { useState } from "react";
import { BookmarkIcon as BookmarkOutline } from "@heroicons/react/24/outline";
import { BookmarkIcon as BookmarkSolid } from "@heroicons/react/24/solid";
import { useSavedJobs } from "@/lib/savedJobs";

interface SaveJobButtonProps {
  jobId: string | number;
  className?: string;
  showText?: boolean;
}

export default function SaveJobButton({
  jobId,
  className = "",
  showText = false,
}: SaveJobButtonProps) {
  const idStr = String(jobId);
  const { isSaved, toggle } = useSavedJobs();
  const saved = isSaved(idStr);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const nextSaved = toggle(idStr);
    setToastMessage(nextSaved ? "Đã lưu việc làm!" : "Đã bỏ lưu");
    setTimeout(() => setToastMessage(null), 2000);
  };

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={handleToggle}
        className={`inline-flex items-center gap-1.5 p-2 rounded-xl transition-all duration-200 active:scale-90 cursor-pointer ${
          saved
            ? "bg-rose-50 text-rose-600 border border-rose-200 hover:bg-rose-100"
            : "bg-slate-100 text-slate-500 hover:text-slate-800 hover:bg-slate-200"
        } ${className}`}
        title={saved ? "Bỏ lưu việc làm này" : "Lưu vào danh sách quan tâm"}
        aria-label={saved ? "Bỏ lưu" : "Lưu việc làm"}
      >
        {saved ? (
          <BookmarkSolid className="h-5 w-5 text-rose-600 animate-scaleIn" />
        ) : (
          <BookmarkOutline className="h-5 w-5" />
        )}
        {showText && (
          <span className="text-xs font-bold">
            {saved ? "Đã lưu" : "Lưu tin"}
          </span>
        )}
      </button>

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-lg bg-slate-900 text-white text-[11px] font-bold shadow-lg z-30 animate-fadeIn">
          {toastMessage}
        </div>
      )}
    </div>
  );
}
