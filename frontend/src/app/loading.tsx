import React from "react";

export default function Loading() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-8">
      <div className="relative flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        <div className="absolute w-8 h-8 bg-accent-500 rounded-full opacity-20 animate-ping" />
      </div>
      <p className="mt-4 text-sm font-semibold text-slate-600 animate-pulse">
        Đang tải dữ liệu việc làm C_Data...
      </p>
    </div>
  );
}
