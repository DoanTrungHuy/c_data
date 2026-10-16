"use client";

import React, { Suspense, useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { ChevronRightIcon, HomeIcon, BoltIcon } from "@heroicons/react/24/outline";
import SearchBar from "@/components/SearchBar";
import JobsContent from "@/components/JobsContent";
import { getJobs } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import { JobListResponse } from "@/types/job";

function JobsView() {
  const searchParams = useSearchParams();
  const urlQ = searchParams?.get("q") || "";
  const urlProvince = searchParams?.get("province") || "";
  const category = searchParams?.get("category") || "";
  const job_type = searchParams?.get("job_type") || "";
  const platform = searchParams?.get("source_platform") || "";
  const salary_min = searchParams?.get("salary_min");
  const salary_max = searchParams?.get("salary_max");
  const page = Number(searchParams?.get("page")) || 1;
  const pageSize = Number(searchParams?.get("page_size")) || 20;
  const isLive = searchParams?.get("live") === "true";
  const isStrictMode = searchParams?.get("strict_mode") === "true";
  const isSavedOnly = searchParams?.get("saved") === "true";

  const [data, setData] = useState<JobListResponse>({
    items: [],
    total: 0,
    page: 1,
    page_size: pageSize,
    total_pages: 1,
    related_keywords: [],
    matched_industries: [],
  });
  const [loading, setLoading] = useState(true);

  // Tải danh sách việc làm theo đúng tham số trên thanh địa chỉ URL (chỉ kích hoạt khi bấm tìm kiếm hoặc đổi trang/bộ lọc)
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    getJobs({
      q: urlQ || undefined,
      province: urlProvince || undefined,
      category: category || undefined,
      job_type: job_type || undefined,
      salary_min: salary_min ? Number(salary_min) : undefined,
      salary_max: salary_max ? Number(salary_max) : undefined,
      source_platform: platform || undefined,
      live: isLive,
      strict_mode: isStrictMode,
      saved: isSavedOnly,
      page,
      page_size: pageSize,
    })
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [urlQ, urlProvince, category, job_type, platform, salary_min, salary_max, isLive, isStrictMode, isSavedOnly, page, pageSize]);

  return (
    <div className="min-h-screen bg-white pb-16">
      {/* Search Header Banner */}
      <div className="bg-neutral-50 border-b border-neutral-200 py-6 sm:py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-4">
          {/* Breadcrumb & Status Indicator */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <nav className="flex items-center gap-2 text-xs text-neutral-500 font-medium">
              <Link
                href="/"
                className="flex items-center gap-1 hover:text-black transition-colors"
              >
                <HomeIcon className="h-3.5 w-3.5" />
                <span>Trang chủ</span>
              </Link>
              <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
              <Link href="/jobs" className="text-neutral-700 hover:text-black font-semibold">
                Tìm việc làm
              </Link>
              {isSavedOnly && (
                <>
                  <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
                  <span className="text-black font-bold">❤️ Việc làm đã lưu</span>
                </>
              )}
              {urlProvince && !isSavedOnly && (
                <>
                  <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
                  <span className="text-black font-semibold">
                    {urlProvince}
                  </span>
                </>
              )}
              {urlQ && !isSavedOnly && (
                <>
                  <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
                  <span className="text-neutral-900 font-bold truncate max-w-[150px]">
                    "{urlQ}"
                  </span>
                </>
              )}
            </nav>

            {/* Status Indicator Badge */}
            {isSavedOnly ? (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-100 text-black border border-neutral-300 text-xs font-bold shadow-2xs">
                <span>📌 Chế độ xem việc làm đã lưu</span>
              </div>
            ) : (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-100 text-black border border-neutral-300 text-xs font-bold shadow-2xs">
                <span className="h-2 w-2 rounded-full bg-black"></span>
                <span>Dữ liệu xác thực Zero-404</span>
              </div>
            )}
          </div>

          {/* SearchBar Input */}
          <div className="max-w-4xl">
            <SearchBar
              initialQuery={urlQ}
              initialProvince={urlProvince}
              initialLive={isLive}
              initialStrictMode={isStrictMode}
              compact
            />
          </div>
        </div>
      </div>

      {/* Main Content & Sidebar */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-8">
        {loading ? (
          <div className="py-24 text-center space-y-4">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-black border-r-transparent"></div>
            <p className="text-sm text-neutral-500 font-medium">
              Đang tìm kiếm và lọc việc làm thời gian thực...
            </p>
          </div>
        ) : (
          <JobsContent initialData={data} />
        )}
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-white flex items-center justify-center">
          <div className="text-center space-y-3">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-black border-r-transparent"></div>
            <p className="text-sm text-neutral-500 font-medium">Đang tải việc làm...</p>
          </div>
        </div>
      }
    >
      <JobsView />
    </Suspense>
  );
}
