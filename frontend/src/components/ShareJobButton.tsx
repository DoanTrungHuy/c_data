"use client";

import React, { useState } from "react";
import { ShareIcon, CheckIcon } from "@heroicons/react/24/outline";

interface ShareJobButtonProps {
  title: string;
  className?: string;
  showText?: boolean;
}

export default function ShareJobButton({
  title,
  className = "",
  showText = false,
}: ShareJobButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleShare = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const currentUrl = typeof window !== "undefined" ? window.location.href : "";

    if (navigator.share) {
      try {
        await navigator.share({
          title: `${title} | C_Data Tuyển Dụng`,
          text: `Xem tin tuyển dụng "${title}" trên C_Data:`,
          url: currentUrl,
        });
        return;
      } catch (err) {
        // Fallback to clipboard
      }
    }

    try {
      await navigator.clipboard.writeText(currentUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback
    }
  };

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={handleShare}
        className={`inline-flex items-center gap-1.5 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 transition-all active:scale-95 cursor-pointer ${className}`}
        title="Chia sẻ tin tuyển dụng này"
        aria-label="Chia sẻ"
      >
        {copied ? (
          <CheckIcon className="h-5 w-5 text-emerald-600" />
        ) : (
          <ShareIcon className="h-5 w-5" />
        )}
        {showText && (
          <span className="text-xs font-bold">
            {copied ? "Đã copy link!" : "Chia sẻ"}
          </span>
        )}
      </button>

      {copied && (
        <div className="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-lg bg-emerald-700 text-white text-[11px] font-bold shadow-lg z-30 animate-fadeIn">
          Đã sao chép liên kết!
        </div>
      )}
    </div>
  );
}
