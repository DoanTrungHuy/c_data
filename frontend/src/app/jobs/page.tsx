"use client";

import React, { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRightIcon, HomeIcon } from "@heroicons/react/24/outline";
import SearchBar from "@/components/SearchBar";
import JobsContent from "@/components/JobsContent";
import { getJobs } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import { JobListResponse } from "@/types/job";

function JobsView() {
  const searchParams = useSearchParams();
  const q = searchParams?.get("q") || "";
  const province = searchParams?.get("province") || "";
  const category = searchParams?.get("category") || "";
  const job_type = searchParams?.get("job_type") || "";
  const platform = searchParams?.get("source_platform") || "";
  const salary_min = searchParams?.get("salary_min");
  const salary_max = searchParams?.get("salary_max");
  const page = Number(searchParams?.get("page")) || 1;
  const pageSize = Number(searchParams?.get("page_size")) || 20;
  const isLive = searchParams?.get("live") === "true";
  const isStrictMode = searchParams?.get("strict_mode") === "true";

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

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    getJobs({
      q: q || undefined,
      province: province || undefined,
      category: category || undefined,
      job_type: job_type || undefined,
      salary_min: salary_min ? Number(salary_min) : undefined,
      salary_max: salary_max ? Number(salary_max) : undefined,
      source_platform: platform || undefined,
      live: isLive,
      strict_mode: isStrictMode,
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
  }, [
    q,
    province,
    category,
    job_type,
    platform,
    salary_min,
    salary_max,
    isLive,
    isStrictMode,
    page,
    pageSize,
  ]);

  return (
    <div className="min-h-screen bg-slate-50/60 pb-16">
      {/* Search Header Banner */}
      <div className="bg-gradient-to-b from-blue-50/70 to-slate-50 border-b border-slate-200/80 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-4">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-xs text-slate-500 font-medium">
            <Link
              href="/"
              className="flex items-center gap-1 hover:text-primary-600 transition-colors"
            >
              <HomeIcon className="h-3.5 w-3.5" />
              <span>Trang chủ</span>
            </Link>
            <ChevronRightIcon className="h-3 w-3 text-slate-400" />
            <span className="text-slate-800 font-semibold">Tìm việc làm</span>
            {province && (
              <>
                <ChevronRightIcon className="h-3 w-3 text-slate-400" />
                <span className="text-primary-600 font-semibold">{province}</span>
              </>
            )}
          </nav>

          {/* SearchBar Input */}
          <div className="max-w-4xl">
            <SearchBar
              initialQuery={q}
              initialProvince={province}
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
            <div className="inline-block h-9 w-9 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
            <p className="text-sm text-slate-500 font-medium">
              Đang đối soát dữ liệu và phân tích việc làm...
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
        <div className="min-h-screen bg-slate-50 flex items-center justify-center">
          <div className="text-center space-y-3">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent"></div>
            <p className="text-sm text-slate-500 font-medium">Đang tải việc làm...</p>
          </div>
        </div>
      }
    >
      <JobsView />
    </Suspense>
  );
}
