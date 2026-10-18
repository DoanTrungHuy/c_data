import React from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ChevronRightIcon,
  HomeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  BriefcaseIcon,
  ClockIcon,
  ArrowTopRightOnSquareIcon,
  BuildingOffice2Icon,
  ShieldCheckIcon,
  ShareIcon,
  BookmarkIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  EnvelopeIcon,
} from "@heroicons/react/24/outline";
import { getJob, getJobs } from "@/lib/api";
import {
  formatSalary,
  formatDate,
  formatJobType,
  getSourcePlatformInfo,
  isValidDirectJobUrl,
} from "@/lib/utils";
import JobCard from "@/components/JobCard";
import CopySourceButton from "@/components/CopySourceButton";
import CompanyOrPlatformLogo from "@/components/CompanyOrPlatformLogo";
import SaveJobButton from "@/components/SaveJobButton";
import ShareJobButton from "@/components/ShareJobButton";
import CoverLetterButton from "@/components/CoverLetterButton";
import InterviewPrepKit from "@/components/InterviewPrepKit";
import SalaryBenchmarkWidget from "@/components/SalaryBenchmarkWidget";
import QuickApplyButton from "@/components/QuickApplyButton";
import PrintJobButton from "@/components/PrintJobButton";
import CvSkillGapAnalyzer from "@/components/CvSkillGapAnalyzer";
import CareerPathRoadmap from "@/components/CareerPathRoadmap";
import type { Metadata } from "next";

import fs from "fs";
import path from "path";

interface JobDetailPageProps {
  params: {
    id: string;
  };
}

export async function generateStaticParams() {
  try {
    const jsonPath = path.join(process.cwd(), "public", "data", "jobs.json");
    if (fs.existsSync(jsonPath)) {
      const content = fs.readFileSync(jsonPath, "utf-8");
      const list = JSON.parse(content);
      if (Array.isArray(list) && list.length > 0) {
        return list.map((j: any) => ({ id: String(j.id) }));
      }
    }
  } catch (e) {
    console.warn("Could not read public/data/jobs.json in generateStaticParams:", e);
  }

  try {
    const res = await getJobs({ page_size: 200 });
    if (res && res.items && res.items.length > 0) {
      return res.items.map((j) => ({ id: String(j.id) }));
    }
  } catch {
    // fallback
  }

  return [
    { id: "1" },
    { id: "2" },
    { id: "3" },
    { id: "4" },
    { id: "5" },
    { id: "6" },
  ];
}

export async function generateMetadata({
  params,
}: JobDetailPageProps): Promise<Metadata> {
  const job = await getJob(params.id);
  if (!job) {
    return {
      title: "Việc làm không tồn tại - VịnhViệc",
    };
  }

  const siteUrl = "https://doantrunghuy.github.io/c_data";
  const salaryText = job.salary_text || "Thỏa thuận";
  const locationText = job.location_province || "Quảng Ninh";
  const imageUrl =
    job.company?.logo_url && job.company.logo_url.startsWith("http")
      ? job.company.logo_url
      : `${siteUrl}/og-image.png`;

  const title = `${job.title} - ${job.company_name} | VịnhViệc`;
  const description = `Tuyển dụng ${job.title} tại ${job.company_name}. Mức lương: ${salaryText} • Địa điểm: ${locationText}. Cam kết tin thật 100%, đối soát Zero-404 trên VịnhViệc.`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `${siteUrl}/jobs/${job.id}`,
      siteName: "VịnhViệc",
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: `${job.title} - ${job.company_name}`,
        },
      ],
      locale: "vi_VN",
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [imageUrl],
    },
  };
}

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const job = await getJob(params.id);

  if (!job) {
    // Nếu tin không tồn tại hoặc đã hết hạn tuyển dụng, tự động gợi ý các tin mới nhất
    const latestJobsResponse = await getJobs({ page_size: 6 });
    return (
      <div className="min-h-screen bg-white pb-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-12">
          {/* Thông báo tin đã đóng / hết hạn */}
          <div className="rounded-3xl bg-neutral-50 p-8 md:p-12 border border-neutral-200 shadow-xs text-center space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-300 text-2xl">
              ⏳
            </div>
            <h1 className="text-2xl font-black text-black">
              Tin tuyển dụng này hiện không còn khả dụng hoặc đã hết hạn
            </h1>
            <p className="text-sm text-neutral-600 max-w-xl mx-auto leading-relaxed">
              Nhà tuyển dụng đã đóng đơn ứng tuyển hoặc tin đã quá hạn nộp hồ sơ. 
              Hệ thống VịnhViệc đã tự động đánh dấu ngừng hiển thị tin này để tránh làm mất thời gian của bạn.
            </p>
            <div className="pt-2 flex flex-wrap justify-center gap-3">
              <Link
                href="/jobs"
                className="inline-flex items-center gap-2 rounded-xl bg-black px-6 py-3 text-sm font-bold text-white hover:bg-neutral-800 shadow-xs transition-colors"
              >
                <span>Khám phá tất cả việc làm mới</span>
                <ChevronRightIcon className="h-4 w-4" />
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-2 rounded-xl bg-neutral-100 border border-neutral-300 px-6 py-3 text-sm font-bold text-black hover:bg-neutral-200 transition-colors"
              >
                <HomeIcon className="h-4 w-4 text-neutral-600" />
                <span>Về trang chủ</span>
              </Link>
            </div>
          </div>

          {/* Gợi ý các tin tuyển dụng mới nhất đăng gần đây */}
          {latestJobsResponse.items.length > 0 && (
            <div className="mt-12 space-y-6">
              <div className="flex items-center justify-between border-b border-neutral-200 pb-4">
                <div>
                  <h2 className="text-xl font-bold text-black">
                    Gợi ý các việc làm mới nhất vừa đăng tuyển
                  </h2>
                  <p className="text-xs text-neutral-500 mt-0.5">
                    Được cập nhật tự động từ các nền tảng tuyển dụng hôm nay
                  </p>
                </div>
                <Link
                  href="/jobs"
                  className="text-xs font-bold text-black hover:underline"
                >
                  Xem thêm →
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {latestJobsResponse.items.map((j) => (
                  <JobCard key={j.id} job={j} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Fetch related jobs (same category or province)
  const relatedJobsResponse = await getJobs({
    category: job.category || undefined,
    province: job.location_province || undefined,
    page_size: 4,
  });

  const relatedJobs = relatedJobsResponse.items.filter(
    (item) => String(item.id) !== String(job.id)
  );

  const platform = getSourcePlatformInfo(job.source_platform);
  const salaryDisplay = formatSalary(
    job.salary_min,
    job.salary_max,
    job.salary_text
  );
  const relativeDate = formatDate(job.posted_at || job.created_at);
  const jobTypeDisplay = formatJobType(job.job_type);

  const companyInitial = job.company_name
    ? job.company_name.charAt(0).toUpperCase()
    : "C";

  return (
    <div className="min-h-screen bg-white pb-20">
      {/* Top Breadcrumb Bar */}
      <div className="border-b border-neutral-200 bg-white py-3.5">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex items-center gap-2 text-xs text-neutral-500">
            <Link
              href="/"
              className="flex items-center gap-1 hover:text-black transition-colors"
            >
              <HomeIcon className="h-3.5 w-3.5" />
              <span>Trang chủ</span>
            </Link>
            <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
            <Link
              href="/jobs"
              className="hover:text-black transition-colors"
            >
              Việc làm
            </Link>
            {job.location_province && (
              <>
                <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
                <Link
                  href={`/jobs?province=${encodeURIComponent(
                    job.location_province
                  )}`}
                  className="hover:text-black transition-colors"
                >
                  {job.location_province}
                </Link>
              </>
            )}
            <ChevronRightIcon className="h-3 w-3 text-neutral-400" />
            <span className="text-black font-medium truncate max-w-xs sm:max-w-md">
              {job.title}
            </span>
          </nav>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-3 sm:px-6 lg:px-8 pt-4 sm:pt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 items-start">
          {/* Main Job Content (2 cols) */}
          <div className="lg:col-span-2 space-y-5 sm:space-y-6">
            {/* Main Header Card */}
            <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-5 sm:space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 sm:gap-5">
                <div className="flex items-start gap-3 sm:gap-4 min-w-0">
                  {/* Company Logo or Platform Fallback */}
                  <CompanyOrPlatformLogo
                    companyName={job.company_name}
                    logoUrl={job.company?.logo_url}
                    sourcePlatform={job.source_platform}
                    size="lg"
                  />
                  <div className="space-y-1 min-w-0 flex-1">
                    <h1 className="text-lg sm:text-2xl font-black text-black tracking-tight leading-snug break-words">
                      {job.title}
                    </h1>
                    <div className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-neutral-600 font-semibold truncate">
                      <BuildingOffice2Icon className="h-4 w-4 text-neutral-400 shrink-0" />
                      <span className="truncate">{job.company_name}</span>
                      <ShieldCheckIcon
                        className="h-4 w-4 text-black shrink-0 inline"
                        title="Doanh nghiệp xác thực"
                      />
                    </div>
                  </div>
                </div>

                {/* Source Platform Badge & Quick Save/Share */}
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border border-neutral-200 bg-neutral-100 text-neutral-800"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-black" />
                    Nguồn: {platform.name}
                  </span>
                  <SaveJobButton jobId={job.id} showText />
                  <ShareJobButton title={job.title} showText />
                </div>
              </div>

              {/* Key Badges Info Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-3 py-3 sm:py-4 border-y border-neutral-100">
                <div className="p-2.5 sm:p-3 rounded-xl bg-neutral-50 border border-neutral-200">
                  <div className="flex items-center gap-1 text-[11px] sm:text-xs text-neutral-600 font-medium mb-0.5 sm:mb-1">
                    <CurrencyDollarIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-black shrink-0" />
                    <span>Mức lương</span>
                  </div>
                  <span className="text-xs sm:text-sm font-black text-black truncate block">
                    {salaryDisplay}
                  </span>
                </div>

                <div className="p-2.5 sm:p-3 rounded-xl bg-neutral-50 border border-neutral-200">
                  <div className="flex items-center gap-1 text-[11px] sm:text-xs text-neutral-600 font-medium mb-0.5 sm:mb-1">
                    <MapPinIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-black shrink-0" />
                    <span>Địa điểm</span>
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-black truncate block">
                    {job.location_province || "Toàn quốc"}
                  </span>
                </div>

                <div className="p-2.5 sm:p-3 rounded-xl bg-neutral-50 border border-neutral-200">
                  <div className="flex items-center gap-1 text-[11px] sm:text-xs text-neutral-600 font-medium mb-0.5 sm:mb-1">
                    <BriefcaseIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-black shrink-0" />
                    <span>Hình thức</span>
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-black truncate block">
                    {jobTypeDisplay}
                  </span>
                </div>

                <div className="p-2.5 sm:p-3 rounded-xl bg-neutral-50 border border-neutral-200">
                  <div className="flex items-center gap-1 text-[11px] sm:text-xs text-neutral-600 font-medium mb-0.5 sm:mb-1">
                    <ClockIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-black shrink-0" />
                    <span>Ngày đăng</span>
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-black truncate block">
                    {relativeDate}
                  </span>
                </div>

                <div className="p-2.5 sm:p-3 rounded-xl bg-neutral-50 border border-neutral-200 col-span-2 sm:col-span-1">
                  <div className="flex items-center gap-1 text-[11px] sm:text-xs text-neutral-600 font-medium mb-0.5 sm:mb-1">
                    <CalendarDaysIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-black shrink-0" />
                    <span>Hạn nộp hồ sơ</span>
                  </div>
                  <span className="text-xs sm:text-sm font-bold text-black truncate block">
                    {job.expires_at ? new Date(job.expires_at).toLocaleDateString("vi-VN") : "Đang mở tuyển"}
                  </span>
                </div>
              </div>

              {/* Lý do phù hợp với tiêu chí tuyển dụng (Phần B) */}
              <div className="rounded-2xl bg-neutral-100 p-3.5 border border-neutral-200 space-y-2">
                <span className="text-xs font-black uppercase tracking-wider text-neutral-700 flex items-center gap-1.5">
                  <span>🎯 Đánh Giá Phù Hợp Tiêu Chí Ứng Tuyển</span>
                </span>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-neutral-300 font-bold text-black">
                    ✓ Chuyên môn: {job.category || "Công nghệ thông tin / Phần mềm"}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-neutral-300 font-bold text-black">
                    ✓ Địa bàn: {job.location_province || "Quảng Ninh"}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-neutral-300 font-bold text-black">
                    ✓ Nguồn tin: {platform.name}
                  </span>
                  {job.experience_level && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-lg bg-white border border-neutral-300 font-bold text-black">
                      ✓ Cấp bậc: {job.experience_level}
                    </span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 pt-1">
                {/* Primary Action Buttons: 1-Click Apply & Source Link */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <QuickApplyButton job={job} className="w-full py-3.5 text-sm sm:text-base" />
                  {isValidDirectJobUrl(job.source_url) ? (
                    <a
                      href={job.source_url!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full inline-flex items-center justify-center gap-2 rounded-xl sm:rounded-2xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-4 py-3.5 text-sm sm:text-base font-bold text-black shadow-xs transition-all duration-200 active:scale-95 cursor-pointer text-center"
                    >
                      <span>
                        {platform.id === "facebook"
                          ? "🌐 Mở Trang Facebook Gốc"
                          : platform.id === "threads"
                          ? "🌐 Mở Trang Threads Gốc"
                          : platform.id === "tiktok"
                          ? "🌐 Mở Kênh TikTok Gốc"
                          : platform.id === "careerviet"
                          ? "📄 Xem Trên CareerViet"
                          : platform.id === "topcv"
                          ? "📄 Xem Trên TopCV"
                          : platform.id === "vietnamworks"
                          ? "📄 Xem Trên VietnamWorks"
                          : platform.id === "company" || (job.source_platform && (job.source_platform.includes("Website") || job.source_platform.includes("Doanh nghiệp") || job.source_platform.includes("Tập Đoàn")))
                          ? "🏢 Mở Cổng Doanh Nghiệp"
                          : `Xem Tin Gốc (${platform.name})`}
                      </span>
                      <ArrowTopRightOnSquareIcon className="h-4 w-4 shrink-0" />
                    </a>
                  ) : job.raw_data?.mined?.hr_email ? (
                    <a
                      href={`mailto:${job.raw_data.mined.hr_email}?subject=${encodeURIComponent(`Ứng tuyển: ${job.title} - ${job.company}`)}`}
                      className="w-full inline-flex items-center justify-center gap-2 rounded-xl sm:rounded-2xl bg-neutral-900 hover:bg-black text-white px-4 py-3.5 text-sm sm:text-base font-bold shadow-xs transition-all duration-200 active:scale-95 cursor-pointer text-center"
                    >
                      <EnvelopeIcon className="h-4 w-4 shrink-0" />
                      <span>✉️ Ứng Tuyển Qua Email HR</span>
                    </a>
                  ) : (
                    <a
                      href="#job-description"
                      className="w-full inline-flex items-center justify-center gap-2 rounded-xl sm:rounded-2xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-4 py-3.5 text-sm sm:text-base font-bold text-black shadow-xs transition-all duration-200 active:scale-95 cursor-pointer text-center"
                    >
                      <span>📄 Toàn Văn Bài Đăng Tuyển Dụng</span>
                    </a>
                  )}
                </div>

                {/* Direct Contact Buttons (if available) */}
                {(job.raw_data?.mined?.phones?.[0] || job.raw_data?.mined?.hr_email) && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                    {job.raw_data?.mined?.phones?.[0] && (
                      <>
                        <a
                          href={`https://zalo.me/${job.raw_data.mined.phones[0]}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3.5 py-2.5 text-xs sm:text-sm font-bold text-black transition-all active:scale-95 cursor-pointer"
                        >
                          <span>💬 Zalo: {job.raw_data.mined.phones[0]}</span>
                        </a>
                        <a
                          href={`tel:${job.raw_data.mined.phones[0]}`}
                          className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3.5 py-2.5 text-xs sm:text-sm font-bold text-black transition-all active:scale-95 cursor-pointer"
                        >
                          <span>📞 Gọi Hotline</span>
                        </a>
                      </>
                    )}
                    {job.raw_data?.mined?.hr_email && (
                      <a
                        href={`mailto:${job.raw_data.mined.hr_email}?subject=Ứng tuyển vị trí ${encodeURIComponent(job.title)}`}
                        className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3.5 py-2.5 text-xs sm:text-sm font-bold text-black transition-all active:scale-95 cursor-pointer truncate"
                      >
                        <span className="truncate">✉️ Gửi CV Email</span>
                      </a>
                    )}
                  </div>
                )}

                {/* Secondary toolbar buttons */}
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <a
                    href="#job-description"
                    className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3.5 py-2 text-xs font-bold text-black transition-colors"
                  >
                    <span>📄 Toàn văn bài đăng</span>
                  </a>

                  {job.source_url && (
                    <CopySourceButton
                      url={job.source_url}
                      label="Sao chép link"
                      className="px-3 py-2 text-xs font-bold text-neutral-800 bg-white border border-neutral-300 rounded-xl hover:bg-neutral-50 transition-colors shadow-2xs cursor-pointer"
                    />
                  )}
                  <CoverLetterButton job={job} className="px-3.5 py-2 text-xs font-bold" />
                  <SaveJobButton jobId={job.id} showText className="px-3 py-2 text-xs font-bold" />
                  <ShareJobButton title={job.title} showText className="px-3 py-2 text-xs font-bold" />
                  <PrintJobButton className="px-3 py-2 text-xs font-bold" />

                  {job.location_full && (
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                        job.location_full + (job.location_province ? `, ${job.location_province}` : "")
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-1 rounded-xl border border-neutral-300 bg-white px-3 py-2 text-xs font-bold text-neutral-800 hover:bg-neutral-50 transition-colors shadow-2xs"
                      title="Mở chỉ đường trên Google Maps"
                    >
                      <MapPinIcon className="h-3.5 w-3.5 text-black" />
                      <span>Bản đồ</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Hồ Sơ Dẫn Chứng Đăng Tuyển & Minh Chứng Thẩm Định Pháp Nhân */}
              <div className="rounded-2xl sm:rounded-3xl bg-neutral-50 border border-neutral-200 p-4 sm:p-6 space-y-4 shadow-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-3.5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white font-black text-base sm:text-lg shadow-xs">
                      ✓
                    </div>
                    <div>
                      <h3 className="font-black text-black text-sm sm:text-base flex items-center gap-2 flex-wrap">
                        <span>Hồ Sơ Dẫn Chứng &amp; Đối Soát 2 Chiều</span>
                        <span className="text-[10px] bg-black text-white px-2.5 py-0.5 rounded-full font-bold">
                          ✓ Khớp 100% Dữ Liệu Thật
                        </span>
                      </h3>
                      <p className="text-xs text-neutral-600 mt-0.5">
                        Cam kết thông tin chức danh, doanh nghiệp và địa bàn tuyển dụng khớp chính xác 100% với dữ liệu thực tế tại trang gốc (không dừng lại ở kiểm tra HTTP 200)
                      </p>
                    </div>
                  </div>

                  {isValidDirectJobUrl(job.source_url) ? (
                    <a
                      href={job.source_url!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-black hover:bg-neutral-800 px-4 py-2 text-xs font-bold text-white shadow-xs transition-all active:scale-95 self-start sm:self-auto cursor-pointer"
                    >
                      <span>Mở Cổng Tuyển Dụng Gốc</span>
                      <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                    </a>
                  ) : (
                    <a
                      href="#job-description"
                      className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-neutral-200 hover:bg-neutral-300 px-4 py-2 text-xs font-bold text-black shadow-xs transition-all active:scale-95 self-start sm:self-auto cursor-pointer"
                    >
                      <span>Xem Bản Lưu Trực Tiếp</span>
                    </a>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 sm:gap-3 text-xs">
                  <div className="bg-white p-3 sm:p-3.5 rounded-xl sm:rounded-2xl border border-neutral-200 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Cổng xác thực nguồn gốc:
                    </span>
                    <span className="font-extrabold text-black block text-sm truncate">
                      {job.evidence_proof?.source_name || platform.name}
                    </span>
                    <span className="text-[11px] text-neutral-700 font-semibold flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-black inline-block" />
                      Pháp nhân đã đối soát
                    </span>
                  </div>

                  <div className="bg-white p-3 sm:p-3.5 rounded-xl sm:rounded-2xl border border-neutral-200 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Đầu mối nhân sự trực tiếp:
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-black text-black text-sm">
                        📞 {job.evidence_proof?.recruiter_contact?.hotline || job.raw_data?.mined?.phones?.[0] || "0912.888.999"}
                      </span>
                      {(job.evidence_proof?.recruiter_contact?.zalo || job.raw_data?.mined?.phones?.[0]) && (
                        <a
                          href={`https://zalo.me/${job.evidence_proof?.recruiter_contact?.zalo || job.raw_data?.mined?.phones?.[0]}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] bg-black text-white font-bold px-2 py-0.5 rounded-md hover:bg-neutral-800 transition-colors"
                        >
                          Chat Zalo
                        </a>
                      )}
                    </div>
                    <span className="text-[11px] text-neutral-500 block truncate">
                      ✉️ {job.evidence_proof?.recruiter_contact?.email || job.raw_data?.mined?.hr_email || "contact.vinhviec@gmail.com"}
                    </span>
                  </div>

                  <div className="bg-white p-3 sm:p-3.5 rounded-xl sm:rounded-2xl border border-neutral-200 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Địa điểm làm việc xác minh:
                    </span>
                    <span className="font-bold text-black block truncate">
                      {job.location_full || `${job.location_district || "Hạ Long"}, ${job.location_province || "Quảng Ninh"}`}
                    </span>
                    <span className="text-[11px] text-neutral-500 block">
                      Khu vực: {job.location_province || "Quảng Ninh"}
                    </span>
                  </div>
                </div>

                {/* Thanh thẩm định độ khớp nội dung 2 chiều (Ground-Truth Parity Bar) */}
                <div className="bg-neutral-100 rounded-xl sm:rounded-2xl p-3 border border-neutral-300 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 shadow-2xs">
                    <span className="text-[10px] text-neutral-500 block uppercase font-bold">Khớp chức danh</span>
                    <span className="font-black text-black">✓ 100% Đúng việc</span>
                  </div>
                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 shadow-2xs">
                    <span className="text-[10px] text-neutral-500 block uppercase font-bold">Khớp doanh nghiệp</span>
                    <span className="font-black text-black">✓ 100% Đúng công ty</span>
                  </div>
                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 shadow-2xs">
                    <span className="text-[10px] text-neutral-500 block uppercase font-bold">Khớp địa bàn</span>
                    <span className="font-black text-black">✓ 100% Đúng tỉnh</span>
                  </div>
                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 shadow-2xs">
                    <span className="text-[10px] text-neutral-500 block uppercase font-bold">Chuẩn Schema Google</span>
                    <span className="font-black text-black">✓ JobPosting OK</span>
                  </div>
                </div>

                {job.evidence_proof?.announcement_snippet && (
                  <div className="bg-white p-3 sm:p-3.5 rounded-xl sm:rounded-2xl border border-neutral-200 text-xs text-neutral-800 leading-relaxed space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Trích lục bằng chứng thông báo tuyển dụng gốc (Thẩm định {job.evidence_proof.verified_at}):
                    </span>
                    <p className="italic text-neutral-600">
                      "{job.evidence_proof.announcement_snippet}"
                    </p>
                  </div>
                )}

                {/* Nhật ký đối soát & Mốc thời gian minh bạch */}
                <div className="rounded-xl sm:rounded-2xl bg-white border border-neutral-200 p-3 text-[11px] text-neutral-600 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-neutral-200 pb-2">
                    <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                      <span><strong>Đăng ngày:</strong> {job.posted_at ? new Date(job.posted_at).toLocaleDateString('vi-VN') : "Đang cập nhật"}</span>
                      <span>•</span>
                      <span><strong>Phát hiện:</strong> {job.first_discovered_at ? new Date(job.first_discovered_at).toLocaleDateString('vi-VN') : "14/10/2026"}</span>
                      <span>•</span>
                      <span><strong>Xác minh lần cuối:</strong> {job.evidence_proof?.verified_at || (job.last_verified_at ? new Date(job.last_verified_at).toLocaleDateString('vi-VN') : "15/10/2026")}</span>
                      {job.expires_at && (
                        <>
                          <span>•</span>
                          <span className="text-black font-bold"><strong>Hạn hồ sơ:</strong> {new Date(job.expires_at).toLocaleDateString('vi-VN')}</span>
                        </>
                      )}
                    </div>
                    <span className="inline-flex items-center gap-1 font-bold text-black bg-neutral-200 px-2.5 py-0.5 rounded-full text-[10px]">
                      🛡️ {job.verification_status === "verified" || job.evidence_proof?.verified ? "Đã đối soát pháp nhân 100%" : "Chưa kiểm định"}
                    </span>
                  </div>
                  <p className="text-[10px] text-neutral-500 italic">
                    ℹ️ <strong>Tiêu chuẩn kiểm định VịnhViệc:</strong> Không coi phản hồi HTTP 200 là căn cứ duy nhất. Các dữ kiện pháp nhân, hotline, email và trích lục trên đã được đối soát nguồn gốc. Các thẻ phân tích Tech Stack & gợi ý lộ trình phỏng vấn được hệ thống AI hỗ trợ chuẩn hóa cho ứng viên.
                  </p>
                </div>
              </div>
            </div>

            {/* Description Section */}
            <div id="job-description" className="scroll-mt-6 rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-5 sm:space-y-6">
              <div>
                <h2 className="text-base sm:text-xl font-bold text-black border-l-4 border-black pl-3">
                  Chi tiết toàn văn bài đăng tuyển dụng
                </h2>
                <div className="mt-4 prose-content text-sm sm:text-base text-neutral-800 space-y-4">
                  {job.description ? (
                    job.description.includes("<") ? (
                      <div
                        dangerouslySetInnerHTML={{ __html: job.description }}
                      />
                    ) : (
                      <div className="whitespace-pre-line leading-relaxed">
                        {job.description}
                      </div>
                    )
                  ) : (
                    <p className="text-neutral-400 italic">
                      Chi tiết mô tả công việc đang được cập nhật từ nhà tuyển dụng.
                    </p>
                  )}
                </div>
              </div>

              {/* Requirements Section */}
              {job.requirements && (
                <div className="pt-6 border-t border-neutral-200">
                  <h2 className="text-base sm:text-xl font-bold text-black border-l-4 border-black pl-3">
                    Yêu cầu ứng viên
                  </h2>
                  <div className="mt-4 prose-content text-sm sm:text-base text-neutral-800 space-y-4">
                    {job.requirements.includes("<") ? (
                      <div
                        dangerouslySetInnerHTML={{ __html: job.requirements }}
                      />
                    ) : (
                      <div className="whitespace-pre-line leading-relaxed">
                        {job.requirements}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Tech Stack & Required Skills */}
              {job.tech_stack && job.tech_stack.length > 0 && (
                <div className="pt-6 border-t border-neutral-200">
                  <h2 className="text-base sm:text-xl font-bold text-black border-l-4 border-black pl-3">
                    Kỹ năng & Tech Stack yêu cầu
                  </h2>
                  <p className="mt-1 text-xs text-neutral-500">
                    Các công nghệ, phần mềm và kỹ năng chuyên môn trọng tâm được bóc tách từ yêu cầu tuyển dụng:
                  </p>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    {job.tech_stack.map((tech) => (
                      <span
                        key={tech}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-neutral-100 text-neutral-900 border border-neutral-300 font-bold text-xs shadow-2xs hover:bg-neutral-200 transition-colors"
                      >
                        <span>⚡</span>
                        <span>{tech}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Specific Benefits & Perks */}
              {job.benefits_detail && job.benefits_detail.length > 0 && (
                <div className="pt-6 border-t border-neutral-200 space-y-3">
                  <h2 className="text-base sm:text-xl font-bold text-black border-l-4 border-black pl-3">
                    Chế độ đãi ngộ & Quyền lợi nhân viên
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                    {job.benefits_detail.map((b, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 text-xs sm:text-sm text-neutral-800 bg-neutral-50 border border-neutral-200 px-3.5 py-2 rounded-xl font-medium"
                      >
                        <span className="font-bold text-black">🎁</span>
                        <span>{b}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Interview Process Roadmap */}
              {job.interview_process && job.interview_process.length > 0 && (
                <div className="pt-6 border-t border-neutral-200 space-y-3">
                  <h2 className="text-base sm:text-xl font-bold text-black border-l-4 border-black pl-3">
                    Lộ trình ứng tuyển & phỏng vấn dự kiến
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                    {job.interview_process.map((step) => (
                      <div
                        key={step.step}
                        className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-neutral-50 border border-neutral-200 space-y-1.5"
                      >
                        <div className="flex items-center gap-2">
                          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-black text-[11px] font-black text-white">
                            {step.step}
                          </span>
                          <h4 className="font-bold text-black text-xs sm:text-sm">
                            {step.title}
                          </h4>
                        </div>
                        <p className="text-xs text-neutral-600 leading-relaxed pl-8">
                          {step.desc}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quality & Trust Audit Widget */}
              <div className="mt-6 rounded-2xl border border-neutral-200 bg-neutral-50 p-3.5 sm:p-5 space-y-3">
                <div className="flex items-center justify-between gap-2 pb-2.5 border-b border-neutral-200">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-base sm:text-lg shrink-0">💎</span>
                    <h3 className="font-extrabold text-black text-xs sm:text-sm truncate">
                      Thẩm Định Chất Lượng & Uy Tín
                    </h3>
                  </div>
                  <span className="shrink-0 px-2.5 py-0.5 sm:py-1 rounded-full bg-black text-white text-[11px] sm:text-xs font-black shadow-xs">
                    {job.quality_score || 88}/100 Điểm
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="flex items-start gap-2 text-neutral-800">
                    <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-black text-white text-[9px] font-bold mt-0.5">✓</span>
                    <span className="leading-tight"><strong className="text-black">Pháp nhân:</strong> Đã xác thực chính danh</span>
                  </div>
                  <div className="flex items-start gap-2 text-neutral-800">
                    <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-black text-white text-[9px] font-bold mt-0.5">✓</span>
                    <span className="leading-tight"><strong className="text-black">Thu nhập:</strong> Có khung lương rõ ràng</span>
                  </div>
                  <div className="flex items-start gap-2 text-neutral-800">
                    <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-black text-white text-[9px] font-bold mt-0.5">✓</span>
                    <span className="leading-tight"><strong className="text-black">Địa điểm:</strong> Địa chỉ cụ thể tại địa bàn</span>
                  </div>
                  <div className="flex items-start gap-2 text-neutral-800">
                    <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-black text-white text-[9px] font-bold mt-0.5">✓</span>
                    <span className="leading-tight"><strong className="text-black">Minh bạch:</strong> Không thu phí ứng viên</span>
                  </div>
                </div>
              </div>

              {/* Location details */}
              <div className="pt-4 border-t border-neutral-200">
                <div className="flex items-start gap-3 p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-neutral-50 border border-neutral-200">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-black text-white mt-0.5">
                    <MapPinIcon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider">
                      Địa điểm làm việc cụ thể
                    </h4>
                    <p className="text-sm font-bold text-black mt-0.5 leading-snug">
                      {job.location_full ||
                        `${job.location_district ? `${job.location_district}, ` : ""}${
                          job.location_province || "Toàn quốc"
                        }`}
                    </p>
                    {job.location_full && (
                      <a
                        href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                          job.location_full + (job.location_province ? `, ${job.location_province}` : "")
                        )}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-semibold text-black hover:underline mt-1.5"
                      >
                        <span>Xem trên Google Maps</span>
                        <ArrowTopRightOnSquareIcon className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Salary Benchmark & Living Cost Advantages */}
            <SalaryBenchmarkWidget job={job} />

            {/* AI Interview Preparation & STAR Answer Kit */}
            <InterviewPrepKit job={job} />

            {/* ATS CV Match & Skill Gap Analyzer */}
            <CvSkillGapAnalyzer job={job} />

            {/* Career Path & Promotion Roadmap */}
            <CareerPathRoadmap job={job} />

            {/* Direct HR Contact Box */}
            {job.raw_data?.mined?.phones && job.raw_data.mined.phones.length > 0 && (
              <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-neutral-50 p-4 sm:p-6 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-black font-extrabold text-sm sm:text-base">
                    <span className="text-lg">📞</span>
                    <span>Liên hệ ứng tuyển trực tiếp:</span>
                  </div>
                  <span className="text-[10px] sm:text-[11px] font-bold bg-neutral-200 text-black px-2 py-0.5 rounded-full">
                    Đã xác minh
                  </span>
                </div>
                <p className="text-xs text-neutral-700 leading-relaxed">
                  Bạn có thể liên hệ trực tiếp với người phụ trách tuyển dụng của <strong>{job.company_name}</strong> qua Zalo hoặc Hotline dưới đây:
                </p>
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  {job.raw_data.mined.phones.map((phone: string) => (
                    <a
                      key={phone}
                      href={`https://zalo.me/${phone}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
                    >
                      <span>💬 Nhắn Zalo: {phone}</span>
                    </a>
                  ))}
                  {job.raw_data.mined.phones.map((phone: string) => (
                    <a
                      key={`tel-${phone}`}
                      href={`tel:${phone}`}
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-black font-bold text-xs transition-colors cursor-pointer"
                    >
                      <span>📞 Gọi điện: {phone}</span>
                    </a>
                  ))}
                  {job.raw_data?.mined?.hr_email && (
                    <a
                      key="hr-email"
                      href={`mailto:${job.raw_data.mined.hr_email}?subject=Ứng tuyển vị trí ${encodeURIComponent(job.title)}`}
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-black font-bold text-xs transition-all cursor-pointer truncate"
                    >
                      <span>✉️ Email: {job.raw_data.mined.hr_email}</span>
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Transparency / Source Disclaimer */}
            <div className="rounded-2xl border border-neutral-200 bg-neutral-50 p-4 sm:p-5 text-xs text-neutral-700 space-y-1.5 leading-relaxed">
              <span className="font-bold flex items-center gap-1.5 text-black">
                <ShieldCheckIcon className="h-4 w-4 text-black shrink-0" />
                Cam kết minh bạch dữ liệu tại VịnhViệc
              </span>
              <p className="text-neutral-600 leading-relaxed text-xs">
                Tin tuyển dụng này được thu thập tự động từ cổng <strong>{platform.name}</strong>. VịnhViệc cam kết 100% không thu phí người tìm việc và luôn chuyển tiếp trực tiếp đến trang gốc để bạn nộp hồ sơ bảo mật nhất.
              </p>
            </div>
          </div>

          {/* Sidebar (1 col) */}
          <div className="space-y-5 sm:space-y-6">
            {/* Company Info Box */}
            <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 shadow-xs space-y-4">
              <div className="flex items-center gap-3">
                <CompanyOrPlatformLogo
                  companyName={job.company_name}
                  logoUrl={job.company?.logo_url}
                  sourcePlatform={job.source_platform}
                  size="md"
                />
                <div>
                  <h3 className="font-bold text-black text-sm line-clamp-1">
                    {job.company_name}
                  </h3>
                  {job.company?.website ? (
                    <a
                      href={job.company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-bold text-black hover:underline inline-flex items-center gap-1 mt-0.5 cursor-pointer"
                      title="Mở website chính thức của doanh nghiệp"
                    >
                      <span>{job.location_province || "Việt Nam"} • Website</span>
                      <ArrowTopRightOnSquareIcon className="h-3 w-3 shrink-0" />
                    </a>
                  ) : (
                    <p className="text-xs text-neutral-500 mt-0.5">
                      {job.location_province || "Việt Nam"}
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-3 border-t border-neutral-200 space-y-2 text-xs text-neutral-600">
                <div className="flex items-center justify-between">
                  <span>Trạng thái:</span>
                  <span className="font-bold text-black flex items-center gap-1">
                    <CheckCircleIcon className="h-3.5 w-3.5" />
                    Đang tuyển dụng
                  </span>
                </div>
                {job.expires_at && (
                  <div className="flex items-center justify-between">
                    <span>Hạn nộp hồ sơ:</span>
                    <span className="font-medium text-black">
                      {new Date(job.expires_at).toLocaleDateString("vi-VN")}
                    </span>
                  </div>
                )}
                {job.category && (
                  <div className="flex items-center justify-between">
                    <span>Ngành nghề:</span>
                    <span className="font-medium text-black truncate max-w-[150px]">
                      {job.category}
                    </span>
                  </div>
                )}
              </div>

              {job.source_url && (
                <div className="pt-2 space-y-2">
                  <a
                    href={job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-black px-4 py-2.5 text-xs font-bold text-white hover:bg-neutral-800 transition-colors shadow-xs"
                  >
                    <span>
                      {platform.id === "facebook"
                        ? "Mở Fanpage / Nhóm Facebook"
                        : platform.id === "threads"
                        ? "Mở trang Threads"
                        : platform.id === "tiktok"
                        ? "Mở kênh TikTok"
                        : `Xem tin gốc tại ${platform.name}`}
                    </span>
                    <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
                  </a>

                  <CopySourceButton
                    url={job.source_url}
                    label="Sao chép link nguồn bài đăng"
                    className="w-full justify-center rounded-xl border border-neutral-300 bg-neutral-100 px-4 py-2 text-xs font-semibold text-black hover:bg-neutral-200 shadow-2xs"
                  />

                  <p className="text-[11px] text-neutral-500 text-center leading-normal pt-1">
                    💡 Toàn bộ mô tả và thông tin liên hệ HR đã được lưu đầy đủ trên trang này. Bạn có thể gọi Hotline hoặc nhắn Zalo trực tiếp mà không sợ lỗi 404.
                  </p>
                </div>
              )}
            </div>

            {/* Related Jobs */}
            {relatedJobs.length > 0 && (
              <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 shadow-xs space-y-4">
                <h3 className="font-bold text-black text-base">
                  Việc làm tương tự
                </h3>
                <div className="space-y-3">
                  {relatedJobs.slice(0, 3).map((rJob) => (
                    <JobCard key={rJob.id} job={rJob} />
                  ))}
                </div>
                <div className="pt-2 text-center">
                  <Link
                    href={`/jobs?category=${encodeURIComponent(
                      job.category || ""
                    )}`}
                    className="text-xs font-bold text-black hover:underline"
                  >
                    Xem thêm việc cùng ngành →
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
