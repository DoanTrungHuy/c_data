import React from "react";

export default function Loading() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-8 bg-white">
      <div className="relative flex items-center justify-center">
        <div className="w-14 h-14 border-4 border-neutral-200 border-t-black rounded-full animate-spin" />
        <div className="absolute w-6 h-6 bg-black rounded-full opacity-10 animate-ping" />
      </div>
      <p className="mt-4 text-sm font-semibold text-neutral-700 animate-pulse">
        Đang tải dữ liệu việc làm VịnhViệc...
      </p>
    </div>
  );
}
