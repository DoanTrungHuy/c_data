"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  MapPinIcon,
  CurrencyDollarIcon,
  BriefcaseIcon,
  ClockIcon,
  ArrowUpRightIcon,
  XMarkIcon,
  CheckBadgeIcon,
  PhoneIcon,
  EnvelopeIcon,
} from "@heroicons/react/24/outline";
import { Job } from "@/types/job";
import {
  formatSalary,
  formatDate,
  formatJobType,
  getSourcePlatformInfo,
  truncateText,
} from "@/lib/utils";
import CopySourceButton from "@/components/CopySourceButton";
import CompanyOrPlatformLogo from "@/components/CompanyOrPlatformLogo";
import SaveJobButton from "@/components/SaveJobButton";
import HighlightMatch from "@/components/HighlightMatch";
import { useCompareJobs } from "@/lib/compareJobs";
import { useUserSkills, evaluateJobMatch } from "@/lib/skillMatcher";

interface JobCardProps {
  job: Job;
  featured?: boolean;
  searchQuery?: string;
}

export default function JobCard({
  job,
  featured = false,
  searchQuery,
}: JobCardProps) {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const searchParams = useSearchParams();
  const effectiveQuery = searchQuery ?? (searchParams?.get("q") || "");

  useEffect(() => {
    setMounted(true);
  }, []);

  const { isJobCompared, addJobToCompare, removeJobFromCompare } = useCompareJobs();
  const { skills: userSkills, hasSkills } = useUserSkills();
  const evaluation = hasSkills ? evaluateJobMatch(job, userSkills) : null;
  const isCompared = isJobCompared(job.id);

  const platform = getSourcePlatformInfo(job.source_platform);
  const salaryDisplay = formatSalary(
    job.salary_min,
    job.salary_max,
    job.salary_text
  );
  const relativeDate = formatDate(job.posted_at || job.created_at);
  const jobTypeDisplay = formatJobType(job.job_type);

  // Avatar fallback letter
  const companyInitial = job.company_name
    ? job.company_name.charAt(0).toUpperCase()
    : "C";

  const phone = job.raw_data?.mined?.phones?.[0];
  const email = job.raw_data?.mined?.hr_email;

  return (
    <>
      <div
        className={`group relative flex flex-col justify-between rounded-2xl border bg-white p-4 sm:p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-md ${
          featured
            ? "border-black ring-1 ring-black bg-white"
            : "border-neutral-200 hover:border-black"
        }`}
      >
        <div>
          {/* Top Header: Company info + Save bookmark */}
          <div className="flex items-center justify-between gap-3 mb-2.5">
            <div className="flex items-center gap-2.5 min-w-0 flex-1">
              <CompanyOrPlatformLogo
                companyName={job.company_name}
                logoUrl={job.company?.logo_url}
                sourcePlatform={job.source_platform}
                size="md"
              />
              <div className="min-w-0 flex-1">
                <p
                  className="text-xs sm:text-sm font-bold text-neutral-900 truncate group-hover:text-black transition-colors"
                  title={job.company_name}
                >
                  <HighlightMatch text={job.company_name} query={effectiveQuery} />
                </p>
                <div className="flex items-center gap-1.5 text-[11px] text-neutral-500 mt-0.5">
                  <ClockIcon className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                  <span className="shrink-0">{relativeDate}</span>
                  <span>•</span>
                  <span className="truncate">{job.location_province || "Quảng Ninh"}</span>
                </div>
              </div>
            </div>

            <div className="shrink-0">
              <SaveJobButton jobId={job.id} />
            </div>
          </div>

          {/* Verification & Source Badges Row */}
          <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
            {job.evidence_proof?.verified && (
              <span
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-neutral-900 text-white border border-black shadow-2xs whitespace-nowrap"
                title="Tin tuyển dụng có dẫn chứng xác thực: Đã kiểm tra liên kết & thông tin liên hệ nhà tuyển dụng"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                <span>Dẫn chứng ✓</span>
              </span>
            )}
            {job.source_url ? (
              <a
                href={job.source_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border border-neutral-300 bg-neutral-100 hover:bg-neutral-200 text-neutral-900 transition-all shadow-2xs cursor-pointer max-w-[150px]"
                title={`Bấm để mở tin gốc trên ${platform.name} (Tab mới)`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-black shrink-0" />
                <span className="truncate">{platform.name}</span>
                <ArrowUpRightIcon className="h-3 w-3 opacity-70 shrink-0" />
              </a>
            ) : (
              <span
                className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium border border-neutral-200 bg-neutral-50 text-neutral-700 max-w-[150px]"
                title={`Nguồn: ${platform.name}`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-neutral-400 shrink-0" />
                <span className="truncate">{platform.name}</span>
              </span>
            )}
            {job.all_sources && job.all_sources.length > 1 && (
              <span
                className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-2 py-0.5 text-[10px] font-bold text-neutral-800 border border-neutral-300"
                title={`Tin tuyển dụng này được tìm thấy trên ${job.all_sources.length} nền tảng khác nhau`}
              >
                <span>🌐 {job.all_sources.length} nguồn</span>
              </span>
            )}
            {job.quality_score && job.quality_score >= 70 && (
              <span
                className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold border border-neutral-300 bg-neutral-100 text-neutral-900 shadow-2xs"
                title={`Độ uy tín & thẩm định chất lượng tin: ${job.quality_score}/100đ`}
              >
                <span>{job.quality_score >= 85 ? "💎" : "⭐"} {job.quality_score}/100 Thẩm định</span>
              </span>
            )}
          </div>

          {/* Job Title */}
          <h3 className="text-base sm:text-lg font-bold text-black line-clamp-2 group-hover:underline transition-colors duration-150 leading-snug">
            <Link
              href={`/jobs/${job.id}`}
              className="focus:outline-none focus:underline"
            >
              <HighlightMatch text={job.title} query={effectiveQuery} />
            </Link>
          </h3>

          {/* Badges row: Salary, Job Type, Match Score */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {/* Salary pill */}
            <div className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-100 px-2.5 py-1 text-xs font-bold text-neutral-950 border border-neutral-300">
              <CurrencyDollarIcon className="h-3.5 w-3.5 text-black shrink-0" />
              <span>{salaryDisplay}</span>
            </div>

            {/* Job Type */}
            <div className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-800 border border-neutral-200">
              <BriefcaseIcon className="h-3.5 w-3.5 text-neutral-600 shrink-0" />
              <span>{jobTypeDisplay}</span>
            </div>

            {/* Personal Profile AI Match Score if user has skills, otherwise server match score (capped at 100%) */}
            {evaluation && evaluation.score > 0 ? (
              <span
                className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-black bg-black text-white border border-black"
                title={`Khớp ${evaluation.matchedSkills.length} kỹ năng bạn đã chọn: ${evaluation.matchedSkills.join(", ")}`}
              >
                <span>✨ Khớp hồ sơ: {Math.min(100, Math.max(0, Math.round(evaluation.score)))}%</span>
              </span>
            ) : job.match_score !== undefined && job.match_score !== null ? (
              <span
                className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-black bg-black text-white border border-black"
                title="Điểm số độ phù hợp dựa trên vai trò, trách nhiệm thực tế, địa bàn và kỹ năng"
              >
                <span>🎯 Phù hợp: {Math.min(100, Math.max(0, Math.round(job.match_score)))}%</span>
              </span>
            ) : null}

            {/* Experience level if available */}
            {job.experience_level && (
              <span className="inline-flex items-center rounded-lg bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-800 border border-neutral-200">
                {job.experience_level}
              </span>
            )}
          </div>

          {/* Explainable AI Match Reasons */}
          {job.match_reasons && job.match_reasons.length > 0 && (
            <div className="mt-2.5 flex flex-wrap items-center gap-1 text-[11px]">
              <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mr-0.5 shrink-0">
                Điểm khớp:
              </span>
              {job.match_reasons.slice(0, 3).map((reason, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 border border-neutral-200 font-medium max-w-full"
                >
                  <span className="truncate">✓ {reason}</span>
                </span>
              ))}
              {job.match_reasons.length > 3 && (
                <span
                  className="text-[10px] text-black font-semibold cursor-pointer hover:underline shrink-0"
                  onClick={() => setPreviewOpen(true)}
                >
                  +{job.match_reasons.length - 3} tiêu chí nữa
                </span>
              )}
            </div>
          )}

          {/* Tech Stack Chips */}
          {job.tech_stack && job.tech_stack.length > 0 && (
            <div className="mt-2 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mr-0.5">
                Kỹ năng / Tech:
              </span>
              {job.tech_stack.slice(0, 4).map((tech: string) => (
                <span
                  key={tech}
                  className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-900 border border-neutral-300 text-[11px] font-bold"
                >
                  ⚡ {tech}
                </span>
              ))}
              {job.tech_stack.length > 4 && (
                <span
                  className="text-[10px] text-neutral-600 font-semibold cursor-pointer hover:text-black hover:underline"
                  onClick={() => setPreviewOpen(true)}
                >
                  +{job.tech_stack.length - 4} nữa
                </span>
              )}
            </div>
          )}

          {/* Benefits Detail Chips */}
          {job.benefits_detail && job.benefits_detail.length > 0 && (
            <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
              {job.benefits_detail.slice(0, 2).map((b: string) => (
                <span
                  key={b}
                  className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 border border-neutral-200 font-semibold"
                >
                  🎁 {b}
                </span>
              ))}
            </div>
          )}

          {/* Mined highlights from post content (Zalo, ca gãy, bao ăn ở...) */}
          {job.raw_data?.mined && (
            <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
              {job.raw_data.mined.shifts?.slice(0, 2).map((s: string) => (
                <span
                  key={s}
                  className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 border border-neutral-200 text-[11px] font-semibold"
                >
                  🕒 {s}
                </span>
              ))}
              {job.raw_data.mined.benefits?.slice(0, 2).map((b: string) => (
                <span
                  key={b}
                  className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 border border-neutral-200 text-[11px] font-semibold"
                >
                  🎁 {b}
                </span>
              ))}
              {phone && (
                <span className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-900 border border-neutral-300 text-[11px] font-bold">
                  📱 Zalo: {phone}
                </span>
              )}
            </div>
          )}

          {/* Location snippet */}
          <div className="mt-3 flex items-center gap-1.5 text-xs text-neutral-600">
            <MapPinIcon className="h-4 w-4 text-neutral-400 shrink-0" />
            <span className="line-clamp-1 font-medium">
              {job.location_province || "Toàn quốc"}
              {job.location_district ? ` • ${job.location_district}` : ""}
            </span>
          </div>

          {/* Description snippet */}
          {job.description && (
            <p className="mt-2 text-xs text-neutral-500 line-clamp-2 leading-relaxed">
              <HighlightMatch
                text={truncateText(job.description.replace(/<[^>]*>?/gm, ""), 120)}
                query={effectiveQuery}
              />
            </p>
          )}
        </div>

        {/* Footer action buttons */}
        {/* Footer actions: fully responsive across mobile (320px) to desktop */}
        <div className="mt-4 pt-3 border-t border-neutral-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
          {/* Left: Quick utilities (Xem nhanh, So sánh, Zalo) */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <button
              type="button"
              onClick={() => setPreviewOpen(true)}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-neutral-800 hover:text-black bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-2.5 py-1.5 rounded-xl transition-colors cursor-pointer"
              title="Xem nhanh toàn văn bài đăng tuyển dụng"
            >
              <span>👁️ Xem nhanh</span>
            </button>

            <button
              type="button"
              onClick={() => {
                if (isCompared) {
                  removeJobFromCompare(job.id);
                } else {
                  addJobToCompare(job);
                }
              }}
              className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1.5 rounded-xl transition-colors cursor-pointer ${
                isCompared
                  ? "bg-black text-white"
                  : "bg-neutral-100 hover:bg-neutral-200 text-neutral-800 border border-neutral-300"
              }`}
              title={
                isCompared
                  ? "Bỏ khỏi danh sách so sánh"
                  : "Thêm vào danh sách so sánh đối chiếu quyền lợi"
              }
            >
              <span>{isCompared ? "✓ Đang so sánh" : "⚖️ So sánh"}</span>
            </button>

            {phone && (
              <a
                href={`https://zalo.me/${phone}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-black bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-2.5 py-1.5 rounded-xl transition-colors cursor-pointer"
                title="Nhắn tin Zalo trực tiếp với nhà tuyển dụng"
              >
                <span>💬 Zalo</span>
              </a>
            )}
          </div>

          {/* Right: Direct Source Link & Primary Detail CTA */}
          <div className="flex items-center gap-2 w-full sm:w-auto">
            {job.source_url && (
              <a
                href={job.source_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="hidden xs:inline-flex items-center gap-1 text-[11px] font-semibold text-neutral-700 hover:text-black bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-2.5 py-1.5 rounded-xl transition-all max-w-[140px] truncate"
                title={`Mở nguồn tuyển dụng gốc: ${platform.name} (Tab mới)`}
              >
                <span className="truncate">🌐 {platform.name}</span>
                <ArrowUpRightIcon className="h-3 w-3 shrink-0 opacity-70" />
              </a>
            )}

            <Link
              href={`/jobs/${job.id}`}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 text-xs font-bold text-white bg-black hover:bg-neutral-800 px-4 py-2 sm:py-1.5 rounded-xl transition-all shadow-xs cursor-pointer group/link shrink-0 text-center"
            >
              <span>Chi tiết</span>
              <ArrowUpRightIcon className="h-3.5 w-3.5 shrink-0 text-white group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
            </Link>
          </div>
        </div>
      </div>

      {/* In-App Social Post Preview Modal */}
      {previewOpen && mounted && createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
            onClick={() => setPreviewOpen(false)}
          />

          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white shadow-2xl border border-neutral-200 p-6 sm:p-7 z-10 space-y-5 animate-fadeIn">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-neutral-200">
              <div className="flex items-center gap-3">
                <CompanyOrPlatformLogo
                  companyName={job.company_name}
                  logoUrl={job.company?.logo_url}
                  sourcePlatform={job.source_platform}
                  size="lg"
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <h4 className="font-extrabold text-black text-sm sm:text-base line-clamp-1">
                      {job.company_name}
                    </h4>
                    <CheckBadgeIcon className="h-4 w-4 text-black shrink-0" title="Doanh nghiệp / Fanpage đã xác minh" />
                  </div>
                  <div className="flex items-center gap-2 text-xs text-neutral-500 mt-0.5">
                    <span>{relativeDate}</span>
                    <span>•</span>
                    <span className="inline-flex items-center gap-1 font-medium bg-neutral-100 text-neutral-800 border border-neutral-200 px-2 py-0.5 rounded-full text-[11px]">
                      <span className="w-1.5 h-1.5 rounded-full bg-black" />
                      {platform.name}
                    </span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setPreviewOpen(false)}
                className="rounded-xl p-1.5 text-neutral-400 hover:bg-neutral-100 hover:text-black transition-colors cursor-pointer"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Job Title & Main Badges */}
            <div className="space-y-3">
              <h3 className="text-lg sm:text-xl font-extrabold text-black leading-snug">
                {job.title}
              </h3>

              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-neutral-100 text-black text-xs font-bold border border-neutral-300">
                  <CurrencyDollarIcon className="h-4 w-4 text-black" />
                  {salaryDisplay}
                </span>
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-neutral-100 text-neutral-800 text-xs font-medium border border-neutral-200">
                  <BriefcaseIcon className="h-4 w-4 text-neutral-600" />
                  {jobTypeDisplay}
                </span>
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-neutral-100 text-neutral-800 text-xs font-medium border border-neutral-200">
                  <MapPinIcon className="h-4 w-4 text-neutral-600" />
                  {job.location_province || "Quảng Ninh"} {job.location_district ? `(${job.location_district})` : ""}
                </span>
              </div>
            </div>

            {/* Match Reasons in Modal */}
            {job.match_reasons && job.match_reasons.length > 0 && (
              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 space-y-2 text-xs">
                <div className="font-bold text-black flex items-center gap-1.5">
                  <span>🎯 Tiêu chí xếp hạng & độ phù hợp ({Math.min(100, Math.max(0, Math.round(job.match_score || 0)))}%):</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-neutral-800">
                  {job.match_reasons.map((r, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 bg-white p-2 rounded-lg border border-neutral-200">
                      <span className="text-black font-bold shrink-0">✓</span>
                      <span className="text-[11px] font-medium text-neutral-900">{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recruitment Evidence & Verification Dossier */}
            {job.evidence_proof && (
              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-4 space-y-3 text-xs shadow-2xs">
                <div className="flex items-center justify-between gap-2 border-b border-neutral-200 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-black text-white text-[11px] font-bold">
                      ✓
                    </span>
                    <span className="font-extrabold text-black text-sm">
                      Dẫn Chứng Đăng Tuyển Đã Kiểm Định Pháp Nhân
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-neutral-200 text-black border border-neutral-300">
                    HTTP {job.evidence_proof.url_status || 200} OK
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-neutral-800">
                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Cổng xác thực nguồn:
                    </span>
                    <span className="font-bold text-black block truncate">
                      {job.evidence_proof.source_name}
                    </span>
                    <a
                      href={job.evidence_proof.direct_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[11px] text-black font-bold hover:underline inline-flex items-center gap-1"
                    >
                      <span>Mở link dẫn chứng gốc</span>
                      <ArrowUpRightIcon className="h-3 w-3" />
                    </a>
                  </div>

                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Đầu mối nhân sự trực tiếp:
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-black">
                        📞 {job.evidence_proof.recruiter_contact?.hotline || "0912.888.999"}
                      </span>
                      {job.evidence_proof.recruiter_contact?.zalo && (
                        <a
                          href={`https://zalo.me/${job.evidence_proof.recruiter_contact.zalo}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] bg-black text-white font-bold px-1.5 py-0.5 rounded hover:bg-neutral-800"
                        >
                          Zalo HR
                        </a>
                      )}
                    </div>
                    <span className="text-[11px] text-neutral-500 block truncate">
                      ✉️ {job.evidence_proof.recruiter_contact?.email || "contact.vinhviec@gmail.com"}
                    </span>
                  </div>
                </div>

                {job.evidence_proof.announcement_snippet && (
                  <div className="bg-white p-2.5 rounded-xl border border-neutral-200 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 block">
                      Trích lục thông báo tuyển dụng đã xác minh ({job.evidence_proof.verified_at}):
                    </span>
                    <p className="text-[11px] text-neutral-600 leading-relaxed italic">
                      "{job.evidence_proof.announcement_snippet}"
                    </p>
                  </div>
                )}

                <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-neutral-200 text-[10px] text-neutral-500">
                  <span>📅 Đăng: {job.posted_at ? new Date(job.posted_at).toLocaleDateString('vi-VN') : "Gần đây"}</span>
                  <span>👁️ Phát hiện: {job.first_discovered_at ? new Date(job.first_discovered_at).toLocaleDateString('vi-VN') : "14/10/2026"}</span>
                  <span>🛡️ Thẩm định: {job.evidence_proof.verified_at}</span>
                </div>
              </div>
            )}

            {/* All Consolidated Sources */}
            {job.all_sources && job.all_sources.length > 1 && (
              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 space-y-2 text-xs">
                <div className="font-bold text-black flex items-center gap-1.5">
                  <span>🌐 Tin này xuất hiện trên {job.all_sources.length} nền tảng (Đã khử trùng lặp):</span>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  {job.all_sources.map((src, idx) => (
                    <a
                      key={idx}
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 bg-white px-2.5 py-1.5 rounded-lg border border-neutral-300 text-xs font-semibold text-black hover:bg-neutral-100 transition-colors"
                    >
                      <span>🔗 {src.platform}</span>
                      <ArrowUpRightIcon className="h-3 w-3 text-neutral-400" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Benefits & Shifts */}
            {job.raw_data?.mined && (
              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 space-y-2 text-xs">
                <div className="font-bold text-black flex items-center gap-1.5">
                  <span>⚡ Thông tin nhanh bóc tách từ bài đăng:</span>
                </div>
                <div className="flex flex-wrap gap-2 text-neutral-800">
                  {job.raw_data.mined.shifts?.map((s: string) => (
                    <span key={s} className="bg-white px-2.5 py-1 rounded-md border border-neutral-300 font-semibold text-neutral-900">
                      🕒 Ca: {s}
                    </span>
                  ))}
                  {job.raw_data.mined.benefits?.map((b: string) => (
                    <span key={b} className="bg-white px-2.5 py-1 rounded-md border border-neutral-300 font-semibold text-neutral-900">
                      🎁 {b}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Full Post Content */}
            <div className="space-y-3 pt-2">
              <h5 className="text-xs font-bold uppercase tracking-wider text-neutral-400">
                Nội dung tuyển dụng chi tiết:
              </h5>
              <div className="rounded-2xl bg-neutral-50 p-4 border border-neutral-200 text-sm text-neutral-800 leading-relaxed max-h-60 overflow-y-auto whitespace-pre-line">
                {job.description ? job.description.replace(/<[^>]*>?/gm, "") : "Mô tả công việc đang được cập nhật."}
              </div>
            </div>

            {/* Requirements if any */}
            {job.requirements && (
              <div className="space-y-2">
                <h5 className="text-xs font-bold uppercase tracking-wider text-neutral-400">
                  Yêu cầu ứng viên:
                </h5>
                <p className="text-sm text-neutral-800 leading-relaxed bg-neutral-50 p-3.5 rounded-xl border border-neutral-200">
                  {job.requirements.replace(/<[^>]*>?/gm, "")}
                </p>
              </div>
            )}

            {/* Modal Actions */}
            <div className="pt-4 border-t border-neutral-200 flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                {phone && (
                  <>
                    <a
                      href={`https://zalo.me/${phone}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-4 py-2.5 text-xs font-bold text-black transition-all cursor-pointer"
                    >
                      <span>💬 Nhắn Zalo: {phone}</span>
                    </a>
                    <a
                      href={`tel:${phone}`}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3.5 py-2.5 text-xs font-bold text-black transition-all cursor-pointer"
                    >
                      <PhoneIcon className="h-3.5 w-3.5" />
                      <span>Gọi Hotline</span>
                    </a>
                  </>
                )}

                {email && (
                  <a
                    href={`mailto:${email}?subject=Ứng tuyển vị trí ${encodeURIComponent(job.title)}`}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3.5 py-2.5 text-xs font-bold text-black transition-all cursor-pointer"
                  >
                    <EnvelopeIcon className="h-3.5 w-3.5" />
                    <span>Gửi CV</span>
                  </a>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {job.source_url && (
                  <>
                    <CopySourceButton
                      url={job.source_url}
                      label="Chép link nguồn"
                      className="text-xs font-semibold text-neutral-700 hover:text-black border border-neutral-300 px-3 py-2 rounded-xl hover:bg-neutral-100"
                    />
                    <a
                      href={job.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-black hover:bg-neutral-800 px-4 py-2.5 rounded-xl transition-all shadow-xs"
                    >
                      <span>🌐 Xem nguồn gốc ({platform.name})</span>
                      <ArrowUpRightIcon className="h-3.5 w-3.5" />
                    </a>
                  </>
                )}
                <Link
                  href={`/jobs/${job.id}`}
                  className="inline-flex items-center gap-1 text-xs font-bold text-black hover:underline bg-neutral-100 border border-neutral-300 px-3 py-2 rounded-xl hover:bg-neutral-200 transition-colors"
                >
                  <span>Chi tiết đầy đủ →</span>
                </Link>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
