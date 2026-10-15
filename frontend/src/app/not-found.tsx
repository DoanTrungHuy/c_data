import React from "react";
import Link from "next/link";
import { ArrowLeftIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center px-4 py-16 text-center bg-white">
      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-neutral-100 text-black border border-neutral-300 mb-6">
        <MagnifyingGlassIcon className="h-10 w-10" />
      </div>
      <h1 className="text-4xl font-black text-black tracking-tight sm:text-5xl">
        404 - Không tìm thấy trang
      </h1>
      <p className="mt-4 text-base text-neutral-600 max-w-md leading-relaxed">
        Trang hoặc tin tuyển dụng bạn đang tìm kiếm có thể đã hết hạn, đã bị gỡ hoặc đường dẫn không chính xác.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-200 px-5 py-3 text-sm font-semibold text-neutral-800 transition-colors"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          <span>Về trang chủ</span>
        </Link>
        <Link
          href="/jobs"
          className="inline-flex items-center gap-2 rounded-xl bg-black px-5 py-3 text-sm font-semibold text-white hover:bg-neutral-800 transition-colors shadow-xs"
        >
          <span>Khám phá việc làm khác</span>
        </Link>
      </div>
    </div>
  );
}
