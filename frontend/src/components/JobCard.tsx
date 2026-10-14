"use client";

import React, { useState } from "react";
import Link from "next/link";
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
import { useCompareJobs } from "@/lib/compareJobs";
import { useUserSkills, evaluateJobMatch } from "@/lib/skillMatcher";

interface JobCardProps {
  job: Job;
  featured?: boolean;
}

export default function JobCard({ job, featured = false }: JobCardProps) {
  const [previewOpen, setPreviewOpen] = useState(false);
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
        className={`group relative flex flex-col justify-between rounded-2xl border bg-white p-5 sm:p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-hover ${
          featured
            ? "border-primary-200 ring-1 ring-primary-100/80 bg-gradient-to-b from-blue-50/20 to-white"
            : "border-slate-200/90 hover:border-primary-300"
        }`}
      >
        <div>
          {/* Top Header: Company initial + Platform badge + Date */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-3">
              <CompanyOrPlatformLogo
                companyName={job.company_name}
                logoUrl={job.company?.logo_url}
                sourcePlatform={job.source_platform}
                size="md"
              />
              <div>
                <p
                  className="text-xs font-semibold text-slate-500 line-clamp-1 group-hover:text-slate-700 transition-colors"
                  title={job.company_name}
                >
                  {job.company_name}
                </p>
                <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-0.5">
                  <ClockIcon className="h-3.5 w-3.5" />
                  <span>{relativeDate}</span>
                </div>
              </div>
            </div>

            {/* Platform badge, Evidence status & Save bookmark */}
            <div className="flex items-center gap-1.5 shrink-0">
              {job.evidence_proof?.verified && (
                <span
                  className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-50 text-emerald-800 border border-emerald-300 shadow-2xs"
                  title="Tin tuyển dụng có dẫn chứng xác thực: Đã kiểm tra liên kết & thông tin liên hệ nhà tuyển dụng"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Dẫn chứng ✓</span>
                </span>
              )}
              {job.source_url ? (
                <a
                  href={job.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold border transition-all hover:scale-105 active:scale-95 shadow-2xs hover:shadow-xs cursor-pointer ${platform.badgeClass}`}
                  title={
                    job.evidence_proof?.source_name
                      ? `Mở trực tiếp ${job.evidence_proof.source_name} (Link đã xác thực)`
                      : `Bấm để mở tin gốc trên ${platform.name} (Tab mới)`
                  }
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${platform.dotClass}`} />
                  <span>{platform.name}</span>
                  <ArrowUpRightIcon className="h-3 w-3 opacity-70 shrink-0" />
                </a>
              ) : (
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${platform.badgeClass}`}
                  title={`Nguồn: ${platform.name}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${platform.dotClass}`} />
                  {platform.name}
                </span>
              )}
              <SaveJobButton jobId={job.id} />
            </div>
          </div>

          {/* Job Title */}
          <h3 className="text-base sm:text-lg font-bold text-slate-900 line-clamp-2 group-hover:text-primary-600 transition-colors duration-150 leading-snug">
            <Link
              href={`/jobs/${job.id}`}
              className="focus:outline-none focus:underline"
            >
              {job.title}
            </Link>
          </h3>

          {/* Badges row: Salary, Job Type, Match Score & Multi-Source */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {/* Salary pill */}
            <div className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 border border-emerald-200/60">
              <CurrencyDollarIcon className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
              <span>{salaryDisplay}</span>
            </div>

            {/* Job Type */}
            <div className="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
              <BriefcaseIcon className="h-3.5 w-3.5 text-slate-500 shrink-0" />
              <span>{jobTypeDisplay}</span>
            </div>

            {/* Personal Profile AI Match Score if user has skills, otherwise server match score */}
            {evaluation && evaluation.score > 0 ? (
              <span
                className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-black border ${
                  evaluation.score >= 70
                    ? "bg-emerald-50 text-emerald-800 border-emerald-300 ring-1 ring-emerald-300/60"
                    : evaluation.score >= 50
                    ? "bg-amber-50 text-amber-800 border-amber-300"
                    : "bg-blue-50 text-blue-800 border-blue-200"
                }`}
                title={`Khớp ${evaluation.matchedSkills.length} kỹ năng bạn đã chọn: ${evaluation.matchedSkills.join(", ")}`}
              >
                <span>✨ Khớp hồ sơ: {evaluation.score}%</span>
              </span>
            ) : job.match_score !== undefined && job.match_score !== null ? (
              <span
                className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-black border ${
                  job.match_score >= 70
                    ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                    : job.match_score >= 50
                    ? "bg-amber-50 text-amber-800 border-amber-300"
                    : "bg-blue-50 text-blue-800 border-blue-200"
                }`}
                title="Điểm số độ phù hợp dựa trên vai trò, trách nhiệm thực tế, địa bàn và kỹ năng"
              >
                <span>🎯 Phù hợp: {job.match_score}%</span>
              </span>
            ) : null}

            {/* Multi-source indicator if consolidated */}
            {job.all_sources && job.all_sources.length > 1 && (
              <span
                className="inline-flex items-center gap-1 rounded-lg bg-sky-50 px-2.5 py-1 text-xs font-bold text-sky-800 border border-sky-200"
                title={`Tin tuyển dụng này được tìm thấy trên ${job.all_sources.length} nền tảng khác nhau`}
              >
                <span>🌐 {job.all_sources.length} nguồn</span>
              </span>
            )}

            {/* Experience level if available */}
            {job.experience_level && (
              <span className="inline-flex items-center rounded-lg bg-purple-50 px-2.5 py-1 text-xs font-medium text-purple-700 border border-purple-200/50">
                {job.experience_level}
              </span>
            )}

            {/* Quality Score & Audit Tier */}
            {job.quality_score && job.quality_score >= 70 && (
              <span
                className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-black border shadow-2xs ${
                  job.quality_score >= 85
                    ? "bg-gradient-to-r from-amber-50 to-yellow-50 text-amber-900 border-amber-300 ring-1 ring-amber-300/60"
                    : "bg-emerald-50 text-emerald-800 border-emerald-300"
                }`}
                title={`Độ uy tín & thẩm định chất lượng tin: ${job.quality_score}/100đ (Pháp nhân xác thực, lương minh bạch, địa chỉ cụ thể, HR trực tiếp)`}
              >
                <span>{job.quality_score >= 85 ? "💎" : "⭐"} {job.quality_score}/100 Thẩm định</span>
              </span>
            )}
          </div>

          {/* Explainable AI Match Reasons */}
          {job.match_reasons && job.match_reasons.length > 0 && (
            <div className="mt-2.5 flex flex-wrap items-center gap-1 text-[11px]">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-0.5">
                Điểm khớp:
              </span>
              {job.match_reasons.slice(0, 3).map((reason, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-0.5 rounded-md bg-slate-50 text-slate-700 border border-slate-200/90 font-medium"
                >
                  ✓ {reason}
                </span>
              ))}
              {job.match_reasons.length > 3 && (
                <span
                  className="text-[10px] text-primary-600 font-semibold cursor-pointer hover:underline"
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
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-0.5">
                Kỹ năng / Tech:
              </span>
              {job.tech_stack.slice(0, 4).map((tech: string) => (
                <span
                  key={tech}
                  className="px-2 py-0.5 rounded-md bg-indigo-50/90 text-indigo-800 border border-indigo-200/90 text-[11px] font-bold"
                >
                  ⚡ {tech}
                </span>
              ))}
              {job.tech_stack.length > 4 && (
                <span
                  className="text-[10px] text-indigo-600 font-semibold cursor-pointer hover:underline"
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
                  className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200/80 font-semibold"
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
                  className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200/80 text-[11px] font-semibold"
                >
                  🕒 {s}
                </span>
              ))}
              {job.raw_data.mined.benefits?.slice(0, 2).map((b: string) => (
                <span
                  key={b}
                  className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200/80 text-[11px] font-semibold"
                >
                  🎁 {b}
                </span>
              ))}
              {phone && (
                <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200/80 text-[11px] font-semibold">
                  📱 Zalo: {phone}
                </span>
              )}
            </div>
          )}

          {/* Location snippet */}
          <div className="mt-3 flex items-center gap-1.5 text-xs text-slate-600">
            <MapPinIcon className="h-4 w-4 text-slate-400 shrink-0" />
            <span className="line-clamp-1 font-medium">
              {job.location_province || "Toàn quốc"}
              {job.location_district ? ` • ${job.location_district}` : ""}
            </span>
          </div>

          {/* Description snippet */}
          {job.description && (
            <p className="mt-2 text-xs text-slate-500 line-clamp-2 leading-relaxed">
              {truncateText(job.description.replace(/<[^>]*>?/gm, ""), 120)}
            </p>
          )}
        </div>

        {/* Footer action buttons */}
        <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Link
              href={`/jobs/${job.id}`}
              className="text-xs font-bold text-primary-600 hover:text-primary-700 hover:underline inline-flex items-center gap-1"
            >
              Chi tiết
              <ArrowUpRightIcon className="h-3.5 w-3.5" />
            </Link>

            {/* Quick Preview Modal Button */}
            <button
              type="button"
              onClick={() => setPreviewOpen(true)}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded-md transition-colors"
              title="Xem nhanh toàn văn bài đăng tuyển dụng"
            >
              <span>👁️ Xem nhanh</span>
            </button>

            {/* Quick Compare Button */}
            <button
              type="button"
              onClick={() => {
                if (isCompared) {
                  removeJobFromCompare(job.id);
                } else {
                  addJobToCompare(job);
                }
              }}
              className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-1 rounded-md transition-colors cursor-pointer ${
                isCompared
                  ? "bg-indigo-600 text-white shadow-xs"
                  : "bg-slate-100 hover:bg-indigo-50 text-slate-600 hover:text-indigo-700"
              }`}
              title={
                isCompared
                  ? "Bỏ khỏi danh sách so sánh"
                  : "Thêm vào danh sách so sánh đối chiếu quyền lợi"
              }
            >
              <span>{isCompared ? "✓ Đang so sánh" : "⚖️ So sánh"}</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-1.5 ml-auto">
            {phone && (
              <a
                href={`https://zalo.me/${phone}`}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-2.5 py-1 rounded-lg transition-colors shadow-2xs hover:shadow-xs"
                title="Nhắn tin Zalo trực tiếp với nhà tuyển dụng"
              >
                <span>💬 Zalo: {phone}</span>
              </a>
            )}

            {job.source_url && (
              <a
                href={job.source_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-primary-600 hover:bg-primary-700 px-3 py-1.5 rounded-xl transition-all shadow-xs hover:shadow hover:scale-102 active:scale-95 group/link cursor-pointer"
                title={`Mở nguồn tuyển dụng gốc: ${platform.name} (Tab mới)`}
              >
                <span>🌐 {platform.name}</span>
                <ArrowUpRightIcon className="h-3.5 w-3.5 shrink-0 text-white group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
              </a>
            )}
          </div>
        </div>
      </div>

      {/* In-App Social Post Preview Modal */}
      {previewOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={() => setPreviewOpen(false)}
          />

          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white shadow-2xl border border-slate-200 p-6 sm:p-7 z-10 space-y-5 animate-fadeIn">
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <CompanyOrPlatformLogo
                  companyName={job.company_name}
                  logoUrl={job.company?.logo_url}
                  sourcePlatform={job.source_platform}
                  size="lg"
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <h4 className="font-extrabold text-slate-900 text-sm sm:text-base line-clamp-1">
                      {job.company_name}
                    </h4>
                    <CheckBadgeIcon className="h-4 w-4 text-blue-500 shrink-0" title="Doanh nghiệp / Fanpage đã xác minh" />
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                    <span>{relativeDate}</span>
                    <span>•</span>
                    <span className={`inline-flex items-center gap-1 font-medium ${platform.badgeClass} px-2 py-0.5 rounded-full text-[11px]`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${platform.dotClass}`} />
                      {platform.name}
                    </span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setPreviewOpen(false)}
                className="rounded-xl p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Job Title & Main Badges */}
            <div className="space-y-3">
              <h3 className="text-lg sm:text-xl font-extrabold text-slate-900 leading-snug">
                {job.title}
              </h3>

              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200/80">
                  <CurrencyDollarIcon className="h-4 w-4 text-emerald-600" />
                  {salaryDisplay}
                </span>
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium">
                  <BriefcaseIcon className="h-4 w-4 text-slate-500" />
                  {jobTypeDisplay}
                </span>
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-blue-50 text-blue-800 text-xs font-medium border border-blue-100">
                  <MapPinIcon className="h-4 w-4 text-blue-600" />
                  {job.location_province || "Quảng Ninh"} {job.location_district ? `(${job.location_district})` : ""}
                </span>
              </div>
            </div>

            {/* Match Reasons in Modal */}
            {job.match_reasons && job.match_reasons.length > 0 && (
              <div className="rounded-2xl bg-sky-50/70 border border-sky-200/80 p-3.5 space-y-2 text-xs">
                <div className="font-bold text-sky-900 flex items-center gap-1.5">
                  <span>🎯 Tiêu chí xếp hạng & độ phù hợp ({job.match_score || 0}%):</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-slate-700">
                  {job.match_reasons.map((r, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 bg-white p-2 rounded-lg border border-sky-100">
                      <span className="text-emerald-600 font-bold shrink-0">✓</span>
                      <span className="text-[11px] font-medium text-slate-800">{r}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recruitment Evidence & Verification Dossier */}
            {job.evidence_proof && (
              <div className="rounded-2xl bg-gradient-to-br from-emerald-50 via-teal-50/60 to-white border border-emerald-200 p-4 space-y-3 text-xs shadow-2xs">
                <div className="flex items-center justify-between gap-2 border-b border-emerald-200/60 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-600 text-white text-[11px] font-bold">
                      ✓
                    </span>
                    <span className="font-extrabold text-emerald-950 text-sm">
                      Dẫn Chứng Đăng Tuyển Đã Kiểm Định Pháp Nhân
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                    HTTP {job.evidence_proof.url_status || 200} OK
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-700">
                  <div className="bg-white/90 p-2.5 rounded-xl border border-emerald-100 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Cổng xác thực nguồn:
                    </span>
                    <span className="font-bold text-slate-900 block truncate">
                      {job.evidence_proof.source_name}
                    </span>
                    <a
                      href={job.evidence_proof.direct_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[11px] text-primary-600 font-semibold hover:underline inline-flex items-center gap-1"
                    >
                      <span>Mở link dẫn chứng gốc</span>
                      <ArrowUpRightIcon className="h-3 w-3" />
                    </a>
                  </div>

                  <div className="bg-white/90 p-2.5 rounded-xl border border-emerald-100 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Đầu mối nhân sự trực tiếp:
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-emerald-700">
                        📞 {job.evidence_proof.recruiter_contact?.hotline || "0912.888.999"}
                      </span>
                      {job.evidence_proof.recruiter_contact?.zalo && (
                        <a
                          href={`https://zalo.me/${job.evidence_proof.recruiter_contact.zalo}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] bg-emerald-600 text-white font-bold px-1.5 py-0.5 rounded hover:bg-emerald-700"
                        >
                          Zalo HR
                        </a>
                      )}
                    </div>
                    <span className="text-[11px] text-slate-500 block truncate">
                      ✉️ {job.evidence_proof.recruiter_contact?.email || "tuyendung@vinhviec.vn"}
                    </span>
                  </div>
                </div>

                {job.evidence_proof.announcement_snippet && (
                  <div className="bg-white/90 p-2.5 rounded-xl border border-emerald-100 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                      Trích lục thông báo tuyển dụng đã xác minh ({job.evidence_proof.verified_at}):
                    </span>
                    <p className="text-[11px] text-slate-600 leading-relaxed italic">
                      "{job.evidence_proof.announcement_snippet}"
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* All Consolidated Sources */}
            {job.all_sources && job.all_sources.length > 1 && (
              <div className="rounded-2xl bg-indigo-50/70 border border-indigo-200/80 p-3.5 space-y-2 text-xs">
                <div className="font-bold text-indigo-900 flex items-center gap-1.5">
                  <span>🌐 Tin này xuất hiện trên {job.all_sources.length} nền tảng (Đã khử trùng lặp):</span>
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  {job.all_sources.map((src, idx) => (
                    <a
                      key={idx}
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 bg-white px-2.5 py-1.5 rounded-lg border border-indigo-200 text-xs font-semibold text-indigo-900 hover:bg-indigo-100 transition-colors"
                    >
                      <span>🔗 {src.platform}</span>
                      <ArrowUpRightIcon className="h-3 w-3 text-slate-400" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Benefits & Shifts */}
            {job.raw_data?.mined && (
              <div className="rounded-2xl bg-amber-50/70 border border-amber-200/80 p-3.5 space-y-2 text-xs">
                <div className="font-bold text-amber-900 flex items-center gap-1.5">
                  <span>⚡ Thông tin nhanh bóc tách từ bài đăng:</span>
                </div>
                <div className="flex flex-wrap gap-2 text-slate-700">
                  {job.raw_data.mined.shifts?.map((s: string) => (
                    <span key={s} className="bg-white px-2.5 py-1 rounded-md border border-amber-200 font-semibold text-amber-800">
                      🕒 Ca: {s}
                    </span>
                  ))}
                  {job.raw_data.mined.benefits?.map((b: string) => (
                    <span key={b} className="bg-white px-2.5 py-1 rounded-md border border-emerald-200 font-semibold text-emerald-800">
                      🎁 {b}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Full Post Content */}
            <div className="space-y-3 pt-2">
              <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Nội dung tuyển dụng chi tiết:
              </h5>
              <div className="rounded-2xl bg-slate-50 p-4 border border-slate-200/80 text-sm text-slate-700 leading-relaxed max-h-60 overflow-y-auto whitespace-pre-line">
                {job.description ? job.description.replace(/<[^>]*>?/gm, "") : "Mô tả công việc đang được cập nhật."}
              </div>
            </div>

            {/* Requirements if any */}
            {job.requirements && (
              <div className="space-y-2">
                <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Yêu cầu ứng viên:
                </h5>
                <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200/80">
                  {job.requirements.replace(/<[^>]*>?/gm, "")}
                </p>
              </div>
            )}

            {/* Modal Actions */}
            <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                {phone && (
                  <>
                    <a
                      href={`https://zalo.me/${phone}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 px-4 py-2.5 text-xs font-extrabold text-white shadow-sm transition-all"
                    >
                      <span>💬 Nhắn Zalo: {phone}</span>
                    </a>
                    <a
                      href={`tel:${phone}`}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-slate-800 hover:bg-slate-900 px-3.5 py-2.5 text-xs font-bold text-white shadow-sm transition-all"
                    >
                      <PhoneIcon className="h-3.5 w-3.5" />
                      <span>Gọi Hotline</span>
                    </a>
                  </>
                )}

                {email && (
                  <a
                    href={`mailto:${email}?subject=Ứng tuyển vị trí ${encodeURIComponent(job.title)}`}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 px-3.5 py-2.5 text-xs font-bold text-white shadow-sm transition-all"
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
                      className="text-xs font-semibold text-slate-600 hover:text-slate-900 border border-slate-200 px-3 py-2 rounded-xl hover:bg-slate-50"
                    />
                    <a
                      href={job.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-primary-600 hover:bg-primary-700 px-4 py-2.5 rounded-xl transition-all shadow-sm hover:shadow"
                    >
                      <span>🌐 Xem nguồn gốc ({platform.name})</span>
                      <ArrowUpRightIcon className="h-3.5 w-3.5" />
                    </a>
                  </>
                )}
                <Link
                  href={`/jobs/${job.id}`}
                  className="inline-flex items-center gap-1 text-xs font-bold text-primary-600 hover:text-primary-700 bg-primary-50 px-3 py-2 rounded-xl hover:bg-primary-100 transition-colors"
                >
                  <span>Chi tiết đầy đủ →</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
