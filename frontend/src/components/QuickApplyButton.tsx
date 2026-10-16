"use client";

import React, { useState } from "react";
import { Job } from "@/types/job";
import { BoltIcon } from "@heroicons/react/24/outline";
import QuickApplyModal from "@/components/QuickApplyModal";

interface QuickApplyButtonProps {
  job: Job;
  className?: string;
}

export default function QuickApplyButton({
  job,
  className = "",
}: QuickApplyButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className={`inline-flex items-center justify-center gap-2 rounded-xl sm:rounded-2xl bg-black hover:bg-neutral-800 text-white font-bold transition-all shadow-xs active:scale-95 cursor-pointer ${className}`}
        title="Tự động tạo email và tin nhắn Zalo gửi trực tiếp cho nhà tuyển dụng"
      >
        <BoltIcon className="h-4 w-4" />
        <span>Ứng Tuyển 1-Chạm & Soạn Thư</span>
      </button>

      <QuickApplyModal
        job={job}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  );
}
