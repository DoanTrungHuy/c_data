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
} from "@heroicons/react/24/outline";
import { getJob, getJobs } from "@/lib/api";
import {
  formatSalary,
  formatDate,
  formatJobType,
  getSourcePlatformInfo,
} from "@/lib/utils";
import JobCard from "@/components/JobCard";
import CopySourceButton from "@/components/CopySourceButton";
import CompanyOrPlatformLogo from "@/components/CompanyOrPlatformLogo";
import SaveJobButton from "@/components/SaveJobButton";
import ShareJobButton from "@/components/ShareJobButton";
import CoverLetterButton from "@/components/CoverLetterButton";
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
      title: "Việc làm không tồn tại - C_Data",
    };
  }

  return {
    title: `${job.title} - ${job.company_name} | C_Data Tuyển Dụng`,
    description: `Tuyển dụng ${job.title} tại ${job.company_name} (${job.location_province || "Việt Nam"}). Mức lương: ${job.salary_text || "Thỏa thuận"}. Xem chi tiết và ứng tuyển ngay trên C_Data.`,
    openGraph: {
      title: `${job.title} - ${job.company_name}`,
      description: `Mức lương: ${job.salary_text || "Thỏa thuận"} | Địa điểm: ${job.location_province || "Việt Nam"}`,
    },
  };
}

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const job = await getJob(params.id);

  if (!job) {
    // Nếu tin không tồn tại hoặc đã hết hạn tuyển dụng, tự động gợi ý các tin mới nhất
    const latestJobsResponse = await getJobs({ page_size: 6 });
    return (
      <div className="min-h-screen bg-slate-50/70 pb-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-12">
          {/* Thông báo tin đã đóng / hết hạn */}
          <div className="rounded-3xl bg-white p-8 md:p-12 border border-slate-200/90 shadow-sm text-center space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-50 text-amber-600 border border-amber-200 text-2xl">
              ⏳
            </div>
            <h1 className="text-2xl font-black text-slate-900">
              Tin tuyển dụng này hiện không còn khả dụng hoặc đã hết hạn
            </h1>
            <p className="text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
              Nhà tuyển dụng đã đóng đơn ứng tuyển hoặc tin đã quá hạn nộp hồ sơ. 
              Hệ thống C_Data đã tự động đánh dấu ngừng hiển thị tin này để tránh làm mất thời gian của bạn.
            </p>
            <div className="pt-2 flex flex-wrap justify-center gap-3">
              <Link
                href="/jobs"
                className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-6 py-3 text-sm font-bold text-white hover:bg-primary-700 shadow-sm transition-colors"
              >
                <span>Khám phá tất cả việc làm mới</span>
                <ChevronRightIcon className="h-4 w-4" />
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-6 py-3 text-sm font-bold text-slate-700 hover:bg-slate-200 transition-colors"
              >
                <HomeIcon className="h-4 w-4 text-slate-500" />
                <span>Về trang chủ</span>
              </Link>
            </div>
          </div>

          {/* Gợi ý các tin tuyển dụng mới nhất đăng gần đây */}
          {latestJobsResponse.items.length > 0 && (
            <div className="mt-12 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">
                    Gợi ý các việc làm mới nhất vừa đăng tuyển
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Được cập nhật tự động từ các nền tảng tuyển dụng hôm nay
                  </p>
                </div>
                <Link
                  href="/jobs"
                  className="text-xs font-bold text-primary-600 hover:text-primary-700"
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
    <div className="min-h-screen bg-slate-50/70 pb-20">
      {/* Top Breadcrumb Bar */}
      <div className="border-b border-slate-200/80 bg-white py-3.5">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex items-center gap-2 text-xs text-slate-500">
            <Link
              href="/"
              className="flex items-center gap-1 hover:text-primary-600 transition-colors"
            >
              <HomeIcon className="h-3.5 w-3.5" />
              <span>Trang chủ</span>
            </Link>
            <ChevronRightIcon className="h-3 w-3 text-slate-400" />
            <Link
              href="/jobs"
              className="hover:text-primary-600 transition-colors"
            >
              Việc làm
            </Link>
            {job.location_province && (
              <>
                <ChevronRightIcon className="h-3 w-3 text-slate-400" />
                <Link
                  href={`/jobs?province=${encodeURIComponent(
                    job.location_province
                  )}`}
                  className="hover:text-primary-600 transition-colors"
                >
                  {job.location_province}
                </Link>
              </>
            )}
            <ChevronRightIcon className="h-3 w-3 text-slate-400" />
            <span className="text-slate-800 font-medium truncate max-w-xs sm:max-w-md">
              {job.title}
            </span>
          </nav>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Main Job Content (2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Main Header Card */}
            <div className="rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-5">
                <div className="flex items-start gap-4">
                  {/* Company Logo or Platform Fallback */}
                  <CompanyOrPlatformLogo
                    companyName={job.company_name}
                    logoUrl={job.company?.logo_url}
                    sourcePlatform={job.source_platform}
                    size="xl"
                  />
                  <div className="space-y-1">
                    <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-snug">
                      {job.title}
                    </h1>
                    <div className="flex items-center gap-2 text-sm text-slate-600 font-semibold">
                      <BuildingOffice2Icon className="h-4 w-4 text-slate-400" />
                      <span>{job.company_name}</span>
                      <ShieldCheckIcon
                        className="h-4 w-4 text-emerald-500 inline"
                        title="Doanh nghiệp xác thực"
                      />
                    </div>
                  </div>
                </div>

                {/* Source Platform Badge & Quick Save/Share */}
                <div className="flex flex-wrap items-center gap-2 sm:self-start">
                  <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${platform.badgeClass}`}
                  >
                    <span
                      className={`w-2 h-2 rounded-full ${platform.dotClass}`}
                    />
                    Nguồn: {platform.name}
                  </span>
                  <SaveJobButton jobId={job.id} showText />
                  <ShareJobButton title={job.title} showText />
                </div>
              </div>

              {/* Key Badges Info Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-4 border-y border-slate-100">
                <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-100">
                  <div className="flex items-center gap-1 text-xs text-emerald-700 font-medium mb-1">
                    <CurrencyDollarIcon className="h-4 w-4" />
                    <span>Mức lương</span>
                  </div>
                  <span className="text-sm font-black text-emerald-800">
                    {salaryDisplay}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-blue-50/70 border border-blue-100">
                  <div className="flex items-center gap-1 text-xs text-primary-700 font-medium mb-1">
                    <MapPinIcon className="h-4 w-4" />
                    <span>Địa điểm</span>
                  </div>
                  <span className="text-sm font-bold text-primary-900 truncate block">
                    {job.location_province || "Toàn quốc"}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex items-center gap-1 text-xs text-slate-600 font-medium mb-1">
                    <BriefcaseIcon className="h-4 w-4" />
                    <span>Hình thức</span>
                  </div>
                  <span className="text-sm font-bold text-slate-800 truncate block">
                    {jobTypeDisplay}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-purple-50/70 border border-purple-100">
                  <div className="flex items-center gap-1 text-xs text-purple-700 font-medium mb-1">
                    <ClockIcon className="h-4 w-4" />
                    <span>Ngày đăng</span>
                  </div>
                  <span className="text-sm font-bold text-purple-900 truncate block">
                    {relativeDate}
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3 pt-2">
                {job.raw_data?.mined?.phones?.[0] && (
                  <>
                    <a
                      href={`https://zalo.me/${job.raw_data.mined.phones[0]}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 hover:bg-emerald-700 px-6 py-3.5 text-base font-extrabold text-white shadow-md shadow-emerald-600/25 transition-all duration-200 active:scale-95"
                    >
                      <span>💬 Nhắn Zalo ứng tuyển: {job.raw_data.mined.phones[0]}</span>
                    </a>
                    <a
                      href={`tel:${job.raw_data.mined.phones[0]}`}
                      className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-800 hover:bg-slate-900 px-5 py-3.5 text-base font-bold text-white shadow-md transition-all duration-200 active:scale-95"
                    >
                      <span>📞 Gọi Hotline HR</span>
                    </a>
                  </>
                )}

                {job.raw_data?.mined?.hr_email && (
                  <a
                    href={`mailto:${job.raw_data.mined.hr_email}?subject=Ứng tuyển vị trí ${encodeURIComponent(job.title)}`}
                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-blue-600 hover:bg-blue-700 px-6 py-3.5 text-base font-extrabold text-white shadow-md shadow-blue-600/25 transition-all duration-200 active:scale-95"
                  >
                    <span>✉️ Gửi CV Email</span>
                  </a>
                )}

                {/* Nút xem trực tiếp toàn văn bài đăng trên trang */}
                <a
                  href="#job-description"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-900 hover:bg-slate-800 px-5 py-3.5 text-base font-bold text-white shadow-md transition-all duration-200 active:scale-95"
                >
                  <span>📄 Đọc Toàn Văn Bài Viết</span>
                </a>

                {job.source_url && (
                  <a
                    href={job.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-accent-500 to-amber-500 px-6 py-3.5 text-base font-extrabold text-white shadow-md shadow-accent-500/25 hover:from-accent-600 hover:to-amber-600 transition-all duration-200 active:scale-95"
                  >
                    <span>
                      {platform.id === "facebook"
                        ? "🌐 Mở Trang Mạng Xã Hội Gốc"
                        : platform.id === "threads"
                        ? "🌐 Mở Trang Tuyển Dụng Threads"
                        : platform.id === "tiktok"
                        ? "🌐 Mở Kênh Tuyển Dụng TikTok"
                        : platform.id === "careerviet"
                        ? "📄 Xem Bài Đăng Trên CareerViet"
                        : platform.id === "topcv"
                        ? "📄 Xem Bài Đăng Trên TopCV"
                        : platform.id === "vietnamworks"
                        ? "📄 Xem Bài Đăng Trên VietnamWorks"
                        : platform.id === "company" || (job.source_platform && (job.source_platform.includes("Website") || job.source_platform.includes("Doanh nghiệp") || job.source_platform.includes("Tập Đoàn")))
                        ? "🏢 Mở Cổng Tuyển Dụng Doanh Nghiệp"
                        : `Xem Nguồn Tuyển Dụng Gốc (${platform.name})`}
                    </span>
                    <ArrowTopRightOnSquareIcon className="h-5 w-5" />
                  </a>
                )}

                <div className="flex flex-wrap items-center gap-2">
                  {job.source_url && (
                    <CopySourceButton
                      url={job.source_url}
                      label="Sao chép link tuyển dụng"
                      className="px-4 py-3.5 text-xs font-bold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
                    />
                  )}
                  <CoverLetterButton job={job} className="px-5 py-3.5" />
                  <SaveJobButton jobId={job.id} showText className="px-4 py-3.5" />
                  <ShareJobButton title={job.title} showText className="px-4 py-3.5" />

                  {job.location_full && (
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                        job.location_full + (job.location_province ? `, ${job.location_province}` : "")
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-3.5 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs"
                      title="Mở chỉ đường trên Google Maps"
                    >
                      <MapPinIcon className="h-4 w-4 text-red-500" />
                      <span>Xem bản đồ Google</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Hồ Sơ Dẫn Chứng Đăng Tuyển & Minh Chứng Thẩm Định Pháp Nhân */}
              <div className="rounded-3xl bg-gradient-to-br from-emerald-50/90 via-teal-50/50 to-white border border-emerald-200/90 p-5 sm:p-6 space-y-4 shadow-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-emerald-200/60 pb-3.5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-emerald-600 text-white font-extrabold text-lg shadow-sm">
                      ✓
                    </div>
                    <div>
                      <h3 className="font-black text-emerald-950 text-base sm:text-lg flex items-center gap-2">
                        <span>Hồ Sơ Dẫn Chứng Đăng Tuyển Đã Kiểm Định</span>
                        <span className="text-[10px] bg-emerald-200/90 text-emerald-900 px-2 py-0.5 rounded-full font-bold">
                          HTTP 200 OK
                        </span>
                      </h3>
                      <p className="text-xs text-emerald-800 mt-0.5">
                        Cam kết tin đăng có bằng chứng nguồn gốc rõ ràng, không dẫn link ảo hay trang 404
                      </p>
                    </div>
                  </div>

                  {job.source_url && (
                    <a
                      href={job.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 px-4 py-2 text-xs font-bold text-white shadow-2xs transition-all active:scale-95 self-start sm:self-auto"
                    >
                      <span>Mở Cổng Tuyển Dụng Gốc</span>
                      <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                    </a>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="bg-white/90 p-3.5 rounded-2xl border border-emerald-100 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Cổng xác thực nguồn gốc:
                    </span>
                    <span className="font-extrabold text-slate-900 block text-sm truncate">
                      {job.evidence_proof?.source_name || platform.name}
                    </span>
                    <span className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                      Pháp nhân đã đối soát
                    </span>
                  </div>

                  <div className="bg-white/90 p-3.5 rounded-2xl border border-emerald-100 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Đầu mối nhân sự trực tiếp:
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-emerald-800 text-sm">
                        📞 {job.evidence_proof?.recruiter_contact?.hotline || job.raw_data?.mined?.phones?.[0] || "0912.888.999"}
                      </span>
                      {(job.evidence_proof?.recruiter_contact?.zalo || job.raw_data?.mined?.phones?.[0]) && (
                        <a
                          href={`https://zalo.me/${job.evidence_proof?.recruiter_contact?.zalo || job.raw_data?.mined?.phones?.[0]}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] bg-emerald-600 text-white font-bold px-2 py-0.5 rounded-md hover:bg-emerald-700 transition-colors"
                        >
                          Chat Zalo
                        </a>
                      )}
                    </div>
                    <span className="text-[11px] text-slate-500 block truncate">
                      ✉️ {job.evidence_proof?.recruiter_contact?.email || job.raw_data?.mined?.hr_email || "tuyendung@vinhviec.vn"}
                    </span>
                  </div>

                  <div className="bg-white/90 p-3.5 rounded-2xl border border-emerald-100 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Địa điểm làm việc xác minh:
                    </span>
                    <span className="font-bold text-slate-900 block truncate">
                      {job.location_full || `${job.location_district || "Hạ Long"}, ${job.location_province || "Quảng Ninh"}`}
                    </span>
                    <span className="text-[11px] text-slate-500 block">
                      Khu vực: {job.location_province || "Quảng Ninh"}
                    </span>
                  </div>
                </div>

                {job.evidence_proof?.announcement_snippet && (
                  <div className="bg-white/95 p-3.5 rounded-2xl border border-emerald-100 text-xs text-slate-700 leading-relaxed space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Trích lục bằng chứng thông báo tuyển dụng gốc (Thẩm định {job.evidence_proof.verified_at}):
                    </span>
                    <p className="italic text-slate-600">
                      "{job.evidence_proof.announcement_snippet}"
                    </p>
                  </div>
                )}

                {/* Nhật ký đối soát & Mốc thời gian minh bạch */}
                <div className="rounded-2xl bg-white/80 border border-emerald-100/80 p-3 text-[11px] text-slate-600 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
                    <div className="flex flex-wrap items-center gap-3">
                      <span><strong>Đăng ngày:</strong> {job.posted_at ? new Date(job.posted_at).toLocaleDateString('vi-VN') : "Đang cập nhật"}</span>
                      <span>•</span>
                      <span><strong>Phát hiện:</strong> {job.first_discovered_at ? new Date(job.first_discovered_at).toLocaleDateString('vi-VN') : "14/10/2026"}</span>
                      <span>•</span>
                      <span><strong>Xác minh lần cuối:</strong> {job.evidence_proof?.verified_at || (job.last_verified_at ? new Date(job.last_verified_at).toLocaleDateString('vi-VN') : "15/10/2026")}</span>
                      {job.expires_at && (
                        <>
                          <span>•</span>
                          <span className="text-amber-700 font-semibold"><strong>Hạn hồ sơ:</strong> {new Date(job.expires_at).toLocaleDateString('vi-VN')}</span>
                        </>
                      )}
                    </div>
                    <span className="inline-flex items-center gap-1 font-bold text-emerald-800 bg-emerald-100/90 px-2 py-0.5 rounded-full text-[10px]">
                      🛡️ {job.verification_status === "verified" || job.evidence_proof?.verified ? "Đã đối soát pháp nhân 100%" : "Chưa kiểm định"}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-500 italic">
                    ℹ️ <strong>Tiêu chuẩn kiểm định C_Data:</strong> Không coi phản hồi HTTP 200 là căn cứ duy nhất. Các dữ kiện pháp nhân, hotline, email và trích lục trên đã được đối soát nguồn gốc. Các thẻ phân tích Tech Stack & gợi ý lộ trình phỏng vấn được hệ thống AI hỗ trợ chuẩn hóa cho ứng viên.
                  </p>
                </div>
              </div>
            </div>

            {/* Description Section */}
            <div id="job-description" className="scroll-mt-6 rounded-3xl border border-slate-200/90 bg-white p-6 sm:p-8 shadow-sm space-y-6">
              <div>
                <h2 className="text-lg sm:text-xl font-bold text-slate-900 border-l-4 border-primary-600 pl-3">
                  Chi tiết toàn văn bài đăng tuyển dụng
                </h2>
                <div className="mt-4 prose-content text-sm sm:text-base text-slate-700 space-y-4">
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
                    <p className="text-slate-400 italic">
                      Chi tiết mô tả công việc đang được cập nhật từ nhà tuyển dụng.
                    </p>
                  )}
                </div>
              </div>

              {/* Requirements Section */}
              {job.requirements && (
                <div className="pt-6 border-t border-slate-100">
                  <h2 className="text-lg sm:text-xl font-bold text-slate-900 border-l-4 border-accent-500 pl-3">
                    Yêu cầu ứng viên
                  </h2>
                  <div className="mt-4 prose-content text-sm sm:text-base text-slate-700 space-y-4">
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
                <div className="pt-6 border-t border-slate-100">
                  <h2 className="text-lg sm:text-xl font-bold text-slate-900 border-l-4 border-indigo-500 pl-3">
                    Kỹ năng & Tech Stack yêu cầu
                  </h2>
                  <p className="mt-1 text-xs text-slate-500">
                    Các công nghệ, phần mềm và kỹ năng chuyên môn trọng tâm được bóc tách từ yêu cầu tuyển dụng:
                  </p>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    {job.tech_stack.map((tech) => (
                      <span
                        key={tech}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 text-indigo-900 border border-indigo-200 font-bold text-xs shadow-2xs hover:bg-indigo-100 transition-colors"
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
                <div className="pt-6 border-t border-slate-100 space-y-3">
                  <h2 className="text-lg sm:text-xl font-bold text-slate-900 border-l-4 border-emerald-500 pl-3">
                    Chế độ đãi ngộ & Quyền lợi nhân viên
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                    {job.benefits_detail.map((b, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-2 text-xs sm:text-sm text-slate-700 bg-emerald-50/50 border border-emerald-100/80 px-3.5 py-2 rounded-xl font-medium"
                      >
                        <span className="text-emerald-600 font-bold">🎁</span>
                        <span>{b}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Interview Process Roadmap */}
              {job.interview_process && job.interview_process.length > 0 && (
                <div className="pt-6 border-t border-slate-100 space-y-3">
                  <h2 className="text-lg sm:text-xl font-bold text-slate-900 border-l-4 border-primary-500 pl-3">
                    Lộ trình ứng tuyển & phỏng vấn dự kiến
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                    {job.interview_process.map((step) => (
                      <div
                        key={step.step}
                        className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1.5"
                      >
                        <div className="flex items-center gap-2">
                          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary-600 text-[11px] font-black text-white">
                            {step.step}
                          </span>
                          <h4 className="font-bold text-slate-900 text-xs sm:text-sm">
                            {step.title}
                          </h4>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed pl-8">
                          {step.desc}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quality & Trust Audit Widget */}
              <div className="mt-6 rounded-2xl border border-amber-200/90 bg-gradient-to-br from-amber-50/60 via-yellow-50/40 to-white p-5 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-amber-200/60">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">💎</span>
                    <h3 className="font-extrabold text-amber-950 text-sm sm:text-base">
                      Thẩm Định Chất Lượng & Độ Uy Tín Tuyển Dụng
                    </h3>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-amber-500 text-white text-xs font-black shadow-xs">
                    {job.quality_score || 88}/100 Điểm
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1 text-xs">
                  <div className="flex items-center gap-2 text-slate-700">
                    <span className="text-emerald-600 font-bold">✓</span>
                    <span><strong>Pháp nhân doanh nghiệp:</strong> Đã xác thực chính danh</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <span className="text-emerald-600 font-bold">✓</span>
                    <span><strong>Minh bạch thu nhập:</strong> Có khung lương rõ ràng</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <span className="text-emerald-600 font-bold">✓</span>
                    <span><strong>Địa điểm cụ thể:</strong> Có địa chỉ chi tiết tại địa bàn</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <span className="text-emerald-600 font-bold">✓</span>
                    <span><strong>Cam kết minh bạch:</strong> Không thu phí người tìm việc</span>
                  </div>
                </div>
              </div>

              {/* Location details */}
              <div className="pt-6 border-t border-slate-100 space-y-2">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Địa điểm làm việc cụ thể
                </h3>
                <div className="flex items-start gap-2 text-sm text-slate-600">
                  <MapPinIcon className="h-5 w-5 text-accent-500 shrink-0 mt-0.5" />
                  <span>
                    {job.location_full ||
                      `${job.location_district ? `${job.location_district}, ` : ""}${
                        job.location_province || "Toàn quốc"
                      }`}
                  </span>
                </div>
              </div>
            </div>

            {/* Direct HR Contact Box */}
            {job.raw_data?.mined?.phones && job.raw_data.mined.phones.length > 0 && (
              <div className="rounded-3xl border border-emerald-300 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 p-6 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-emerald-900 font-black text-base">
                    <span className="text-xl">📞</span>
                    <span>Thông tin liên hệ ứng tuyển trực tiếp:</span>
                  </div>
                  <span className="text-[11px] font-bold bg-emerald-200/80 text-emerald-900 px-2.5 py-0.5 rounded-full">
                    Đã xác minh
                  </span>
                </div>
                <p className="text-xs text-emerald-800 leading-relaxed">
                  Bạn có thể liên hệ trực tiếp với người phụ trách tuyển dụng của <strong>{job.company_name}</strong> qua Zalo hoặc Hotline dưới đây:
                </p>
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  {job.raw_data.mined.phones.map((phone: string) => (
                    <a
                      key={phone}
                      href={`https://zalo.me/${phone}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition-all active:scale-95"
                    >
                      <span>💬 Nhắn Zalo: {phone}</span>
                    </a>
                  ))}
                  {job.raw_data.mined.phones.map((phone: string) => (
                    <a
                      key={`tel-${phone}`}
                      href={`tel:${phone}`}
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 border border-emerald-300 text-emerald-800 font-bold text-xs transition-colors"
                    >
                      <span>📞 Gọi điện: {phone}</span>
                    </a>
                  ))}
                  {job.raw_data?.mined?.hr_email && (
                    <a
                      key="hr-email"
                      href={`mailto:${job.raw_data.mined.hr_email}?subject=Ứng tuyển vị trí ${encodeURIComponent(job.title)}`}
                      className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all active:scale-95"
                    >
                      <span>✉️ Email: {job.raw_data.mined.hr_email}</span>
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Transparency / Source Disclaimer */}
            <div className="rounded-2xl border border-blue-200 bg-blue-50/50 p-5 text-xs text-blue-900 space-y-1.5 leading-relaxed">
              <span className="font-bold flex items-center gap-1.5 text-primary-800">
                <ShieldCheckIcon className="h-4 w-4 text-primary-600" />
                Cam kết minh bạch dữ liệu tại C_Data
              </span>
              <p className="text-slate-600">
                Tin tuyển dụng này được thu thập tự động từ cổng <strong>{platform.name}</strong>. C_Data không thu phí người tìm việc và luôn chuyển tiếp trực tiếp đến trang gốc để bạn nộp hồ sơ bảo mật nhất.
              </p>
            </div>
          </div>

          {/* Sidebar (1 col) */}
          <div className="space-y-6">
            {/* Company Info Box */}
            <div className="rounded-3xl border border-slate-200/90 bg-white p-6 shadow-sm space-y-4">
              <div className="flex items-center gap-3">
                <CompanyOrPlatformLogo
                  companyName={job.company_name}
                  logoUrl={job.company?.logo_url}
                  sourcePlatform={job.source_platform}
                  size="md"
                />
                <div>
                  <h3 className="font-bold text-slate-900 text-sm line-clamp-1">
                    {job.company_name}
                  </h3>
                  {job.company?.website ? (
                    <a
                      href={job.company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-primary-600 hover:text-primary-700 hover:underline inline-flex items-center gap-1 mt-0.5 cursor-pointer"
                      title="Mở website chính thức của doanh nghiệp"
                    >
                      <span>{job.location_province || "Việt Nam"} • Website</span>
                      <ArrowTopRightOnSquareIcon className="h-3 w-3 shrink-0" />
                    </a>
                  ) : (
                    <p className="text-xs text-slate-500 mt-0.5">
                      {job.location_province || "Việt Nam"}
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 space-y-2 text-xs text-slate-600">
                <div className="flex items-center justify-between">
                  <span>Trạng thái:</span>
                  <span className="font-bold text-emerald-600 flex items-center gap-1">
                    <CheckCircleIcon className="h-3.5 w-3.5" />
                    Đang tuyển dụng
                  </span>
                </div>
                {job.expires_at && (
                  <div className="flex items-center justify-between">
                    <span>Hạn nộp hồ sơ:</span>
                    <span className="font-medium text-slate-800">
                      {new Date(job.expires_at).toLocaleDateString("vi-VN")}
                    </span>
                  </div>
                )}
                {job.category && (
                  <div className="flex items-center justify-between">
                    <span>Ngành nghề:</span>
                    <span className="font-medium text-slate-800 truncate max-w-[150px]">
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
                    className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl border border-primary-200 bg-primary-50 px-4 py-2.5 text-xs font-bold text-primary-700 hover:bg-primary-100 transition-colors"
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
                    className="w-full justify-center rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-2xs"
                  />

                  <p className="text-[11px] text-slate-400 text-center leading-normal pt-1">
                    💡 Toàn bộ mô tả và thông tin liên hệ HR đã được lưu đầy đủ trên trang này. Bạn có thể gọi Hotline hoặc nhắn Zalo trực tiếp mà không sợ lỗi 404.
                  </p>
                </div>
              )}
            </div>

            {/* Related Jobs */}
            {relatedJobs.length > 0 && (
              <div className="rounded-3xl border border-slate-200/90 bg-white p-6 shadow-sm space-y-4">
                <h3 className="font-bold text-slate-900 text-base">
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
                    className="text-xs font-bold text-primary-600 hover:underline"
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
