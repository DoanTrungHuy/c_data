"use client";

import React, { useState } from "react";
import { SparklesIcon, DocumentTextIcon } from "@heroicons/react/24/outline";
import { Job } from "@/types/job";
import CoverLetterModal from "@/components/CoverLetterModal";

interface CoverLetterButtonProps {
  job: Job;
  className?: string;
}

export default function CoverLetterButton({
  job,
  className = "",
}: CoverLetterButtonProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={`inline-flex items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-xs font-bold shadow-md shadow-emerald-600/20 active:scale-95 transition-all cursor-pointer ${className}`}
        title="Tự động soạn thư ứng tuyển & email gửi thẳng đến HR công ty"
      >
        <SparklesIcon className="h-4 w-4 text-amber-300" />
        <span>Tạo thư ứng tuyển & Email HR</span>
      </button>

      <CoverLetterModal
        job={job}
        isOpen={open}
        onClose={() => setOpen(false)}
      />
    </>
  );
}
