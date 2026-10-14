"use client";

import React, { useState } from "react";
import {
  XMarkIcon,
  SparklesIcon,
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
        <div className="flex items-center justify-between gap-3 p-3 sm:p-3.5 bg-slate-900/95 backdrop-blur-md text-white rounded-2xl shadow-2xl border border-slate-700/80">
          {/* Left badge & counter */}
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold text-sm shadow-inner">
              ⚖️
            </span>
            <div>
              <p className="text-xs sm:text-sm font-bold flex items-center gap-1.5">
                <span>So sánh việc làm</span>
                <span className="bg-indigo-500/80 text-white px-2 py-0.2 rounded-full text-[11px] font-extrabold">
                  {count}/4
                </span>
              </p>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Đã chọn các tin tuyển dụng để đối chiếu quyền lợi & đãi ngộ
              </p>
            </div>
          </div>

          {/* Job mini pills */}
          <div className="hidden md:flex items-center gap-1.5 max-w-xs overflow-hidden">
            {comparedJobs.map((j) => (
              <span
                key={j.id}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 text-[11px] text-slate-200 border border-slate-700 max-w-[120px] truncate"
              >
                <span className="truncate">{j.company_name}</span>
                <button
                  type="button"
                  onClick={() => removeJobFromCompare(j.id)}
                  className="hover:text-rose-400"
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
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-xl transition-colors"
              title="Xóa tất cả việc làm khỏi so sánh"
            >
              <TrashIcon className="h-4 w-4" />
            </button>

            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-primary-600 hover:from-indigo-600 hover:to-primary-700 text-white text-xs font-bold shadow-md shadow-indigo-500/20 active:scale-95 transition-all cursor-pointer"
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
