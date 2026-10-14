import React from "react";
import Link from "next/link";
import { ChevronRightIcon, HomeIcon } from "@heroicons/react/24/outline";
import SearchBar from "@/components/SearchBar";
import JobsContent from "@/components/JobsContent";
import { getJobs } from "@/lib/api";

interface JobsPageProps {
  searchParams: {
    q?: string;
    province?: string;
    category?: string;
    job_type?: string;
    salary_min?: string;
    salary_max?: string;
    source_platform?: string;
    page?: string;
    page_size?: string;
    live?: string;
    strict_mode?: string;
  };
}

export const dynamic = "force-dynamic";

export default async function JobsPage({ searchParams }: JobsPageProps) {
  const page = Number(searchParams.page) || 1;
  const pageSize = Number(searchParams.page_size) || 20;
  const isLive = searchParams.live === "true" || searchParams.live === "1";
  const isStrictMode = searchParams.strict_mode === "true" || searchParams.strict_mode === "1";

  const data = await getJobs({
    q: searchParams.q,
    province: searchParams.province,
    category: searchParams.category,
    job_type: searchParams.job_type,
    salary_min: searchParams.salary_min ? Number(searchParams.salary_min) : undefined,
    salary_max: searchParams.salary_max ? Number(searchParams.salary_max) : undefined,
    source_platform: searchParams.source_platform,
    live: isLive,
    strict_mode: isStrictMode,
    page,
    page_size: pageSize,
  });

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
            {searchParams.province && (
              <>
                <ChevronRightIcon className="h-3 w-3 text-slate-400" />
                <span className="text-primary-600 font-semibold">
                  {searchParams.province}
                </span>
              </>
            )}
          </nav>

          {/* SearchBar Input */}
          <div className="max-w-4xl">
            <SearchBar
              initialQuery={searchParams.q || ""}
              initialProvince={searchParams.province || ""}
              initialLive={isLive}
              initialStrictMode={isStrictMode}
              compact
            />
          </div>
        </div>
      </div>

      {/* Main Content & Sidebar */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-8">
        <JobsContent initialData={data} />
      </div>
    </div>
  );
}
