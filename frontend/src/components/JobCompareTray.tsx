"use client";

import React, { useState } from "react";
import {
  XMarkIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { useCompareJobs } from "@/lib/compareJobs";
import JobCompareModal from "@/components/JobCompareModal";

export default function JobCompareTray() {
  const { comparedJobs, count, clearCompareJobs, removeJobFromCompare } = useCompareJobs();
  const [modalOpen, setModalOpen] = useState(false);

  if (count === 0) return null;

  return (
    <>
      <div className="fixed bottom-5 left-1/2 -translate-x-1/2 z-40 w-[95%] max-w-2xl animate-in slide-in-from-bottom-4 duration-200">
        <div className="flex items-center justify-between gap-3 p-3 sm:p-3.5 bg-neutral-950 text-white rounded-2xl shadow-2xl border border-neutral-800">
          {/* Left badge & counter */}
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-neutral-800 text-white font-bold text-sm border border-neutral-700">
              ⚖️
            </span>
            <div>
              <p className="text-xs sm:text-sm font-bold flex items-center gap-1.5">
                <span>So sánh việc làm</span>
                <span className="bg-neutral-800 text-white px-2 py-0.5 rounded-full text-[11px] font-extrabold border border-neutral-700">
                  {count}/4
                </span>
              </p>
              <p className="text-[11px] text-neutral-400 hidden sm:block">
                Đã chọn các tin tuyển dụng để đối chiếu
              </p>
            </div>
          </div>

          {/* Job mini pills */}
          <div className="hidden md:flex items-center gap-1.5 max-w-xs overflow-hidden">
            {comparedJobs.map((j) => (
              <span
                key={j.id}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-neutral-900 text-[11px] text-neutral-200 border border-neutral-800 max-w-[120px] truncate"
              >
                <span className="truncate">{j.company_name}</span>
                <button
                  type="button"
                  onClick={() => removeJobFromCompare(j.id)}
                  className="hover:text-white"
                >
                  <XMarkIcon className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={clearCompareJobs}
              className="p-2 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-xl transition-colors"
              title="Xóa tất cả việc làm khỏi so sánh"
            >
              <TrashIcon className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white hover:bg-neutral-200 text-black text-xs font-bold active:scale-95 transition-all cursor-pointer"
            >
              <span>Xem bảng đối chiếu</span>
              <span className="text-[10px]">→</span>
            </button>
          </div>
        </div>
      </div>

      <JobCompareModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </>
  );
}
