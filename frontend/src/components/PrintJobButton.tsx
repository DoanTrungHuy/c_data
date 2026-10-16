"use client";

import React from "react";
import { PrinterIcon } from "@heroicons/react/24/outline";

interface PrintJobButtonProps {
  className?: string;
  label?: string;
}

export default function PrintJobButton({
  className = "",
  label = "In / Lưu PDF",
}: PrintJobButtonProps) {
  const handlePrint = () => {
    if (typeof window !== "undefined") {
      window.print();
    }
  };

  return (
    <button
      type="button"
      onClick={handlePrint}
      className={`inline-flex items-center justify-center gap-1.5 rounded-xl border border-neutral-300 bg-white hover:bg-neutral-50 text-neutral-800 font-bold transition-colors shadow-2xs cursor-pointer ${className}`}
      title="In hoặc lưu hồ sơ tuyển dụng này dưới dạng file PDF"
    >
      <PrinterIcon className="h-3.5 w-3.5 text-black" />
      <span>{label}</span>
    </button>
  );
}
