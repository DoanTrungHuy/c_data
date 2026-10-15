"use client";

import React, { useState } from "react";
import { SparklesIcon } from "@heroicons/react/24/outline";
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
        className={`inline-flex items-center justify-center gap-1.5 rounded-xl bg-black hover:bg-neutral-800 text-white text-xs font-bold shadow-xs active:scale-95 transition-all cursor-pointer ${className}`}
        title="Tự động soạn thư ứng tuyển & email gửi thẳng đến HR công ty"
      >
        <SparklesIcon className="h-4 w-4 text-white" />
        <span>Tạo thư ứng tuyển &amp; Email HR</span>
      </button>

      <CoverLetterModal
        job={job}
        isOpen={open}
        onClose={() => setOpen(false)}
      />
    </>
  );
}
