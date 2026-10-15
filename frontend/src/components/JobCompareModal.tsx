"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import {
  XMarkIcon,
  CurrencyDollarIcon,
  MapPinIcon,
  BriefcaseIcon,
  ClockIcon,
  ArrowTopRightOnSquareIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { useCompareJobs } from "@/lib/compareJobs";
import CompanyOrPlatformLogo from "@/components/CompanyOrPlatformLogo";
import { formatSalary, formatJobType } from "@/lib/utils";

interface JobCompareModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function JobCompareModal({
  isOpen,
  onClose,
}: JobCompareModalProps) {
  const { comparedJobs, removeJobFromCompare, clearCompareJobs } = useCompareJobs();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!isOpen || comparedJobs.length === 0 || !mounted) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className="relative w-full max-w-5xl rounded-3xl bg-white shadow-2xl border border-neutral-200 p-6 sm:p-8 z-10 space-y-6 max-h-[92vh] overflow-y-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200 text-xl font-bold">
              ⚖️
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-black text-black flex items-center gap-2">
                <span>Bảng So Sánh Đối Chiếu Việc Làm Trực Tiếp</span>
                <span className="text-[10px] bg-neutral-100 text-neutral-800 border border-neutral-300 font-bold px-2.5 py-0.5 rounded-full">
                  {comparedJobs.length} vị trí
                </span>
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Xem chi tiết quyền lợi, đãi ngộ và môi trường làm việc cạnh nhau để đưa ra lựa chọn tối ưu.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={clearCompareJobs}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-neutral-700 hover:text-black hover:bg-neutral-100 border border-neutral-200 transition-colors flex items-center gap-1 cursor-pointer"
            >
              <TrashIcon className="h-3.5 w-3.5" />
              <span>Xóa so sánh</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Matrix Table */}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr className="border-b border-neutral-200">
                <th className="p-3 text-left font-bold text-neutral-500 w-32 uppercase tracking-wider bg-neutral-50 rounded-l-xl">
                  Tiêu chí so sánh
                </th>
                {comparedJobs.map((job) => (
                  <th
                    key={job.id}
                    className="p-4 text-left min-w-[220px] max-w-[280px] bg-neutral-50/50 align-top relative group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <CompanyOrPlatformLogo
                          companyName={job.company_name}
                          logoUrl={job.company?.logo_url}
                          sourcePlatform={job.source_platform}
                          size="sm"
                        />
                        <span className="font-extrabold text-black line-clamp-1">
                          {job.company_name}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeJobFromCompare(job.id)}
                        className="text-neutral-400 hover:text-black p-1"
                        title="Bỏ khỏi so sánh"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                    <Link
                      href={`/jobs/${job.id}`}
                      className="block font-black text-black hover:underline mt-2 text-sm leading-snug line-clamp-2"
                    >
                      {job.title}
                    </Link>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {/* Row 1: Salary */}
              <tr>
                <td className="p-3 font-bold text-neutral-700 bg-neutral-50/70">
                  <div className="flex items-center gap-1.5">
                    <CurrencyDollarIcon className="h-4 w-4 text-black" />
                    <span>Mức lương</span>
                  </div>
                </td>
                {comparedJobs.map((job) => (
                  <td key={job.id} className="p-4">
                    <span className="font-extrabold text-black bg-neutral-100 px-2.5 py-1 rounded-lg border border-neutral-300 text-xs">
                      {formatSalary(job.salary_min, job.salary_max, job.salary_text)}
                    </span>
                  </td>
                ))}
              </tr>

              {/* Row 2: Location */}
              <tr>
                <td className="p-3 font-bold text-neutral-700 bg-neutral-50/70">
                  <div className="flex items-center gap-1.5">
                    <MapPinIcon className="h-4 w-4 text-black" />
                    <span>Địa điểm</span>
                  </div>
                </td>
                {comparedJobs.map((job) => (
                  <td key={job.id} className="p-4 text-neutral-800 font-medium leading-relaxed">
                    {job.location_full ||
                      `${job.location_district ? `${job.location_district}, ` : ""}${
                        job.location_province || "Hạ Long, Quảng Ninh"
                      }`}
                  </td>
                ))}
              </tr>

              {/* Row 3: Job Type */}
              <tr>
                <td className="p-3 font-bold text-neutral-700 bg-neutral-50/70">
                  <div className="flex items-center gap-1.5">
                    <BriefcaseIcon className="h-4 w-4 text-black" />
                    <span>Hình thức</span>
                  </div>
                </td>
                {comparedJobs.map((job) => (
                  <td key={job.id} className="p-4 text-neutral-800 font-semibold">
                    {formatJobType(job.job_type)}
                  </td>
                ))}
              </tr>

              {/* Row 4: Experience */}
              <tr>
                <td className="p-3 font-bold text-neutral-700 bg-neutral-50/70">
                  <div className="flex items-center gap-1.5">
                    <ClockIcon className="h-4 w-4 text-black" />
                    <span>Kinh nghiệm</span>
                  </div>
                </td>
                {comparedJobs.map((job) => (
                  <td key={job.id} className="p-4 text-neutral-800">
                    {job.experience_level || "Không yêu cầu cụ thể"}
                  </td>
                ))}
              </tr>

              {/* Row 5: Shift / Perks Mined */}
              <tr>
                <td className="p-3 font-bold text-neutral-700 bg-neutral-50/70">
                  <span>Phúc lợi nổi bật</span>
                </td>
                {comparedJobs.map((job) => (
                  <td key={job.id} className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {job.raw_data?.mined?.benefits?.map((b: string) => (
                        <span
                          key={b}
                          className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 text-[10px] font-semibold border border-neutral-200"
                        >
                          🎁 {b}
                        </span>
                      ))}
                      {job.raw_data?.mined?.shifts?.map((s: string) => (
                        <span
                          key={s}
                          className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 text-[10px] font-semibold border border-neutral-200"
                        >
                          🕒 {s}
                        </span>
                      ))}
                      {(!job.raw_data?.mined?.benefits || job.raw_data.mined.benefits.length === 0) && (
                        <span className="text-neutral-400 italic">Theo quy định công ty</span>
                      )}
                    </div>
                  </td>
                ))}
              </tr>

              {/* Row 6: Action Apply */}
              <tr>
                <td className="p-3 font-bold text-neutral-700 bg-neutral-50/70">
                  <span>Thao tác</span>
                </td>
                {comparedJobs.map((job) => {
                  const phone = job.raw_data?.mined?.phones?.[0];
                  return (
                    <td key={job.id} className="p-4">
                      <div className="space-y-1.5">
                        <Link
                          href={`/jobs/${job.id}`}
                          className="w-full inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-colors"
                        >
                          <span>Xem chi tiết</span>
                          <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
                        </Link>
                        {phone && (
                          <a
                            href={`https://zalo.me/${phone}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full inline-flex items-center justify-center gap-1 px-3 py-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 text-neutral-900 font-bold text-[11px] border border-neutral-300 transition-colors"
                          >
                            <span>Zalo: {phone}</span>
                          </a>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>,
    document.body
  );
}
