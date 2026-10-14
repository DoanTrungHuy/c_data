import React from "react";
import Link from "next/link";
import { ArrowLeftIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center px-4 py-16 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-amber-50 text-amber-600 border border-amber-200 mb-6">
        <MagnifyingGlassIcon className="h-10 w-10" />
      </div>
      <h1 className="text-4xl font-black text-slate-900 tracking-tight sm:text-5xl">
        404 - Không tìm thấy trang
      </h1>
      <p className="mt-4 text-base text-slate-600 max-w-md leading-relaxed">
        Trang hoặc tin tuyển dụng bạn đang tìm kiếm có thể đã hết hạn, đã bị gỡ hoặc đường dẫn không chính xác.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-200 transition-colors"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          <span>Về trang chủ</span>
        </Link>
        <Link
          href="/jobs"
          className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-5 py-3 text-sm font-semibold text-white hover:bg-primary-700 transition-colors shadow-sm"
        >
          <span>Khám phá việc làm khác</span>
        </Link>
      </div>
    </div>
  );
}
