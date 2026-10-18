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
  EyeIcon,
  EyeSlashIcon,
  ClipboardDocumentCheckIcon,
} from "@heroicons/react/24/outline";
import { Job } from "@/types/job";
import {
  formatSalary,
  formatDate,
  formatJobType,
  getSourcePlatformInfo,
  truncateText,
  isValidDirectJobUrl,
} from "@/lib/utils";
import CopySourceButton from "@/components/CopySourceButton";
import CompanyOrPlatformLogo from "@/components/CompanyOrPlatformLogo";
import SaveJobButton from "@/components/SaveJobButton";
import QuickApplyButton from "@/components/QuickApplyButton";
import HighlightMatch from "@/components/HighlightMatch";
import { useUserSkills, evaluateJobMatch } from "@/lib/skillMatcher";
import {
  useApplicationTracker,
  ApplicationStage,
} from "@/lib/applicationTracker";

const stageLabels: Record<ApplicationStage, string> = {
  submitted: "Đã nộp đơn",
  interviewing: "Phỏng vấn",
  offer: "Nhận Offer",
  rejected: "Đã từ chối",
};

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
  const [stageModalOpen, setStageModalOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const searchParams = useSearchParams();
  const effectiveQuery = searchQuery ?? (searchParams?.get("q") || "");

  const {
    isApplied,
    isDismissed,
    toggleApplied,
    toggleDismiss,
    appliedMap,
    markApplied,
    removeApplied,
  } = useApplicationTracker();

  const applied = isApplied(job.id);
  const dismissed = isDismissed(job.id);
  const appliedRecord = appliedMap[String(job.id)];
  const [customNotes, setCustomNotes] = useState(appliedRecord?.notes || "");
  const [selectedStage, setSelectedStage] = useState<ApplicationStage>(
    appliedRecord?.stage || "submitted"
  );

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (appliedRecord) {
      setSelectedStage(appliedRecord.stage);
      setCustomNotes(appliedRecord.notes || "");
    }
  }, [appliedRecord]);

  const { skills: userSkills, hasSkills } = useUserSkills();
  const evaluation = hasSkills ? evaluateJobMatch(job, userSkills) : null;

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
          dismissed
            ? "opacity-60 border-dashed border-neutral-300 bg-neutral-50/60"
            : featured
            ? "border-black ring-1 ring-black bg-white"
            : "border-neutral-200 hover:border-black"
        }`}
      >
        <div>
          {dismissed && (
            <div className="mb-2.5 px-3 py-1.5 rounded-xl bg-neutral-200/80 text-neutral-800 text-xs flex items-center justify-between border border-neutral-300">
              <span className="flex items-center gap-1.5 font-medium">
                <EyeSlashIcon className="h-3.5 w-3.5 text-neutral-600" />
                Tin này đang trong danh sách bị ẩn
              </span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleDismiss(job.id);
                }}
                className="text-black font-bold hover:underline cursor-pointer"
              >
                Hiện lại
              </button>
            </div>
          )}

          {/* Top Header: Company info + Save bookmark & Dismiss */}
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
                <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-neutral-500 mt-0.5">
                  <span className="flex items-center gap-1 shrink-0">
                    <ClockIcon className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                    <span>{relativeDate}</span>
                  </span>
                  {job.expires_at && (
                    <>
                      <span>•</span>
                      <span className="text-[10px] bg-neutral-100 text-neutral-700 px-1.5 py-0.5 rounded font-medium shrink-0" title={`Hạn nộp hồ sơ: ${new Date(job.expires_at).toLocaleDateString('vi-VN')}`}>
                        ⏳ Hạn: {new Date(job.expires_at).toLocaleDateString("vi-VN")}
                      </span>
                    </>
                  )}
                  <span>•</span>
                  <span className="truncate">{job.location_province || job.location_full || "Toàn quốc"}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1 shrink-0">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleDismiss(job.id);
                }}
                className={`p-2 rounded-xl transition-colors cursor-pointer ${
                  dismissed
                    ? "text-black bg-neutral-200"
                    : "text-neutral-400 hover:text-black hover:bg-neutral-100"
                }`}
                title={dismissed ? "Hiện lại tin tuyển dụng này" : "Ẩn tin tuyển dụng này khỏi danh sách"}
              >
                {dismissed ? (
                  <EyeIcon className="h-4 w-4" />
                ) : (
                  <EyeSlashIcon className="h-4 w-4" />
                )}
              </button>
              <SaveJobButton jobId={job.id} />
            </div>
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

          {/* Unified Badges Row: Salary, Experience, Job Type, Source Platform */}
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

            {/* Experience level if available */}
            {job.experience_level && (
              <span className="inline-flex items-center rounded-lg bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-800 border border-neutral-200">
                {job.experience_level}
              </span>
            )}

            {/* Source Platform with verified dot */}
            <span
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border border-neutral-200 bg-neutral-50 text-neutral-800"
              title={`Nguồn: ${platform.name} • ${job.verification_status === "active_confirmed" ? "Đã đối soát xác thực" : "Đang tuyển dụng"}`}
            >
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${job.verification_status === "active_confirmed" ? "bg-emerald-500 animate-pulse" : "bg-neutral-600"}`} />
              <span className="truncate max-w-[120px]">{platform.name}</span>
            </span>

            {/* AI Match Score if user profile has skills */}
            {evaluation && evaluation.score > 0 && (
              <span
                className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-black bg-black text-white border border-black"
                title={`Khớp ${evaluation.matchedSkills.length} kỹ năng bạn đã chọn`}
              >
                <span>✨ Khớp {Math.min(100, Math.max(0, Math.round(evaluation.score)))}%</span>
              </span>
            )}
          </div>

          {/* Tech Stack Chips (max 4) */}
          {job.tech_stack && job.tech_stack.length > 0 && (
            <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
              {job.tech_stack.slice(0, 4).map((tech: string) => (
                <span
                  key={tech}
                  className="px-2 py-0.5 rounded-md bg-neutral-50 text-neutral-700 border border-neutral-200 text-[11px] font-medium"
                >
                  {tech}
                </span>
              ))}
              {job.tech_stack.length > 4 && (
                <span
                  className="text-[11px] text-neutral-500 font-medium cursor-pointer hover:text-black hover:underline"
                  onClick={() => setPreviewOpen(true)}
                >
                  +{job.tech_stack.length - 4} nữa
                </span>
              )}
            </div>
          )}

          {/* Description snippet */}
          {job.description && (
            <p className="mt-2.5 text-xs text-neutral-500 line-clamp-2 leading-relaxed">
              <HighlightMatch
                text={truncateText(job.description.replace(/<[^>]*>?/gm, ""), 120)}
                query={effectiveQuery}
              />
            </p>
          )}
        </div>

        {/* Footer actions: Clean, focused, synchronized */}
        <div className="mt-4 pt-3 border-t border-neutral-100 flex items-center justify-between gap-2.5">
          {/* Left: Quick Preview & direct contact */}
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setPreviewOpen(true)}
              className="inline-flex items-center gap-1 text-xs font-semibold text-neutral-700 hover:text-black bg-neutral-100 hover:bg-neutral-200 border border-neutral-200 px-3 py-1.5 rounded-xl transition-colors cursor-pointer"
              title="Xem nhanh toàn văn bài đăng tuyển dụng"
            >
              <span>👁️ Xem nhanh</span>
            </button>

            {phone && (
              <a
                href={`https://zalo.me/${phone}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1 text-xs font-bold text-black bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3 py-1.5 rounded-xl transition-colors cursor-pointer"
                title="Nhắn tin Zalo trực tiếp với nhà tuyển dụng"
              >
                <span>💬 Zalo</span>
              </a>
            )}
          </div>

          {/* Right: Direct Source Link & Primary Detail CTA */}
          <div className="flex items-center gap-2">
            {isValidDirectJobUrl(job.source_url) && (
              <a
                href={job.source_url!}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="hidden sm:inline-flex items-center gap-1 text-xs font-semibold text-neutral-600 hover:text-black bg-neutral-50 hover:bg-neutral-100 border border-neutral-200 px-3 py-1.5 rounded-xl transition-all"
                title={`Mở nguồn tuyển dụng gốc: ${platform.name}`}
              >
                <span>Nguồn gốc</span>
                <ArrowUpRightIcon className="h-3.5 w-3.5 opacity-70" />
              </a>
            )}

            <Link
              href={`/jobs/${job.id}`}
              className="inline-flex items-center justify-center gap-1.5 text-xs font-bold text-white bg-black hover:bg-neutral-800 px-4 py-2 rounded-xl transition-all shadow-xs cursor-pointer group/link shrink-0"
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
                  {job.location_province || job.location_full || "Toàn quốc"} {job.location_district ? `(${job.location_district})` : ""}
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
                {isValidDirectJobUrl(job.source_url) && (
                  <>
                    <CopySourceButton
                      url={job.source_url!}
                      label="Chép link nguồn"
                      className="text-xs font-semibold text-neutral-700 hover:text-black border border-neutral-300 px-3 py-2 rounded-xl hover:bg-neutral-100"
                    />
                    <a
                      href={job.source_url!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-black hover:bg-neutral-800 px-4 py-2.5 rounded-xl transition-all shadow-xs"
                    >
                      <span>🌐 Xem nguồn gốc ({platform.name})</span>
                      <ArrowUpRightIcon className="h-3.5 w-3.5" />
                    </a>
                  </>
                )}
                {isValidDirectJobUrl(job.apply_url) && job.apply_url !== job.source_url && (
                  <a
                    href={job.apply_url!}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-black hover:bg-neutral-800 px-4 py-2.5 rounded-xl transition-all shadow-xs"
                  >
                    <span>🚀 Ứng tuyển trực tiếp</span>
                    <ArrowUpRightIcon className="h-3.5 w-3.5" />
                  </a>
                )}
                <QuickApplyButton
                  job={job}
                  className="px-3.5 py-2 text-xs"
                />
                <button
                  type="button"
                  onClick={() => setStageModalOpen(true)}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-neutral-800 bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 px-3 py-2 rounded-xl transition-colors cursor-pointer"
                >
                  <ClipboardDocumentCheckIcon className="h-4 w-4 text-black" />
                  <span>{applied ? `✓ ${stageLabels[appliedRecord?.stage || "submitted"]}` : "Theo dõi nộp đơn"}</span>
                </button>
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

      {/* Application Stage & Private Notes Tracker Modal */}
      {stageModalOpen && mounted && createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
            onClick={() => setStageModalOpen(false)}
          />
          <div className="relative w-full max-w-md rounded-3xl bg-white shadow-2xl border border-neutral-200 p-6 z-10 space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between pb-3 border-b border-neutral-200">
              <div className="flex items-center gap-2">
                <span className="text-xl">📝</span>
                <div>
                  <h4 className="font-bold text-black text-sm">Quản lý Tiến độ Ứng tuyển</h4>
                  <p className="text-[11px] text-neutral-500 line-clamp-1">{job.title}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setStageModalOpen(false)}
                className="p-1 rounded-lg text-neutral-400 hover:text-black cursor-pointer"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3.5 text-xs">
              <div>
                <label className="font-bold text-black block mb-1.5">Trạng thái hồ sơ:</label>
                <div className="grid grid-cols-2 gap-2">
                  {(["submitted", "interviewing", "offer", "rejected"] as ApplicationStage[]).map((st) => (
                    <button
                      key={st}
                      type="button"
                      onClick={() => setSelectedStage(st)}
                      className={`p-2 rounded-xl text-xs font-bold border transition-all text-center cursor-pointer ${
                        selectedStage === st
                          ? "bg-black text-white border-black shadow-xs"
                          : "bg-neutral-50 text-neutral-800 border-neutral-200 hover:bg-neutral-100"
                      }`}
                    >
                      {stageLabels[st]}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="font-bold text-black block mb-1.5">Ghi chú riêng của bạn:</label>
                <textarea
                  rows={3}
                  value={customNotes}
                  onChange={(e) => setCustomNotes(e.target.value)}
                  placeholder="Ví dụ: Đã gửi CV cho HR, hẹn phỏng vấn vòng 1 lúc 14h thứ Năm..."
                  className="w-full p-2.5 rounded-xl bg-neutral-50 border border-neutral-300 text-xs focus:outline-none focus:ring-1 focus:ring-black text-black font-medium"
                />
              </div>

              {appliedRecord?.appliedAt && (
                <p className="text-[11px] text-neutral-500">
                  Ngày bắt đầu theo dõi: {new Date(appliedRecord.appliedAt).toLocaleDateString("vi-VN")} {new Date(appliedRecord.appliedAt).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}
                </p>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-neutral-200">
                <button
                  type="button"
                  onClick={() => {
                    removeApplied(job.id);
                    setStageModalOpen(false);
                  }}
                  className="text-xs font-semibold text-neutral-500 hover:text-black hover:underline cursor-pointer"
                >
                  Xóa khỏi danh sách đã nộp
                </button>
                <button
                  type="button"
                  onClick={() => {
                    markApplied(job.id, selectedStage, customNotes);
                    setStageModalOpen(false);
                  }}
                  className="px-4 py-2 rounded-xl bg-black text-white text-xs font-bold hover:bg-neutral-800 cursor-pointer shadow-xs"
                >
                  Lưu thay đổi
                </button>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
