"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  CurrencyDollarIcon,
  MapPinIcon,
  ArrowUpRightIcon,
  PencilSquareIcon,
  CheckBadgeIcon,
  TrashIcon,
  PlusIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
} from "@heroicons/react/24/outline";
import { Job } from "@/types/job";
import { formatSalary, getSourcePlatformInfo } from "@/lib/utils";
import CompanyOrPlatformLogo from "@/components/CompanyOrPlatformLogo";
import {
  useApplicationTracker,
  ApplicationStage,
} from "@/lib/applicationTracker";
import { useSavedJobs } from "@/lib/savedJobs";

interface JobKanbanBoardProps {
  jobs: Job[];
}

export default function JobKanbanBoard({ jobs }: JobKanbanBoardProps) {
  const { savedIds } = useSavedJobs();
  const {
    appliedMap,
    markApplied,
    removeApplied,
  } = useApplicationTracker();

  const [editingNoteJobId, setEditingNoteJobId] = useState<string | null>(null);
  const [tempNote, setTempNote] = useState("");

  // Map jobs by ID for fast lookup
  const jobsById = new Map<string, Job>(jobs.map((j) => [String(j.id), j]));

  // 1. Column Saved (saved but not yet marked applied)
  const savedJobList = savedIds
    .map((id) => jobsById.get(String(id)))
    .filter((j): j is Job => Boolean(j && !appliedMap[String(j.id)]));

  // 2. Column Submitted
  const submittedJobList = Object.values(appliedMap)
    .filter((r) => r.stage === "submitted")
    .map((r) => jobsById.get(String(r.jobId)))
    .filter((j): j is Job => Boolean(j));

  // 3. Column Interviewing
  const interviewingJobList = Object.values(appliedMap)
    .filter((r) => r.stage === "interviewing")
    .map((r) => jobsById.get(String(r.jobId)))
    .filter((j): j is Job => Boolean(j));

  // 4. Column Offer
  const offerJobList = Object.values(appliedMap)
    .filter((r) => r.stage === "offer")
    .map((r) => jobsById.get(String(r.jobId)))
    .filter((j): j is Job => Boolean(j));

  const handleMoveStage = (
    jobId: string | number,
    newStage: ApplicationStage,
    currentNotes: string = ""
  ) => {
    markApplied(jobId, newStage, currentNotes);
  };

  const handleSaveNote = (jobId: string | number) => {
    const existing = appliedMap[String(jobId)];
    const stage = existing?.stage || "submitted";
    markApplied(jobId, stage, tempNote);
    setEditingNoteJobId(null);
  };

  const columns = [
    {
      id: "saved",
      title: "Đã Lưu & Chuẩn Bị",
      icon: "📌",
      color: "border-neutral-200 bg-neutral-50/50",
      items: savedJobList,
      description: "Các việc làm bạn đang cân nhắc",
    },
    {
      id: "submitted",
      title: "Đã Nộp Hồ Sơ",
      icon: "📝",
      color: "border-neutral-300 bg-neutral-50/80",
      items: submittedJobList,
      description: "Đã gửi CV, chờ phản hồi từ HR",
    },
    {
      id: "interviewing",
      title: "Vòng Phỏng Vấn",
      icon: "🎯",
      color: "border-black/30 bg-neutral-100/70",
      items: interviewingJobList,
      description: "Đang trao đổi hoặc làm bài test",
    },
    {
      id: "offer",
      title: "Nhận Offer & Đạt",
      icon: "🏆",
      color: "border-black bg-white ring-1 ring-black/10",
      items: offerJobList,
      description: "Chúc mừng! Bạn đã nhận đề nghị tuyển dụng",
    },
  ];

  return (
    <div className="space-y-4 animate-fadeIn">
      {/* Board Description */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 bg-neutral-100 rounded-2xl border border-neutral-300 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-base">📊</span>
          <span>
            <strong>Bảng Kanban Quản Lý Ứng Tuyển:</strong> Kéo đẩy tiến trình từ lúc quan tâm, nộp hồ sơ, phỏng vấn đến khi nhận Offer. Toàn bộ lưu trữ an toàn trên thiết bị của bạn.
          </span>
        </div>
      </div>

      {/* 4-Column Responsive Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
        {columns.map((col) => (
          <div
            key={col.id}
            className={`flex flex-col rounded-2xl border p-3.5 min-h-[500px] ${col.color} shadow-xs transition-all`}
          >
            {/* Column Header */}
            <div className="flex items-center justify-between pb-3 border-b border-neutral-200">
              <div className="flex items-center gap-2">
                <span className="text-lg">{col.icon}</span>
                <div>
                  <h3 className="font-bold text-black text-xs sm:text-sm">
                    {col.title}
                  </h3>
                  <p className="text-[10px] text-neutral-500">
                    {col.description}
                  </p>
                </div>
              </div>
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-black text-white font-bold text-xs shadow-2xs">
                {col.items.length}
              </span>
            </div>

            {/* Cards List */}
            <div className="space-y-3 pt-3 flex-1">
              {col.items.length > 0 ? (
                col.items.map((job) => {
                  const appliedRec = appliedMap[String(job.id)];
                  const salaryDisplay = formatSalary(
                    job.salary_min,
                    job.salary_max,
                    job.salary_text
                  );
                  const platform = getSourcePlatformInfo(job.source_platform);
                  const isEditingNote = editingNoteJobId === String(job.id);

                  return (
                    <div
                      key={job.id}
                      className="bg-white rounded-xl border border-neutral-200 p-3 shadow-2xs hover:shadow-md hover:border-black transition-all space-y-2.5"
                    >
                      {/* Top: Logo + Company */}
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <CompanyOrPlatformLogo
                            companyName={job.company_name}
                            logoUrl={job.company?.logo_url}
                            sourcePlatform={job.source_platform}
                            size="sm"
                          />
                          <p className="text-xs font-bold text-neutral-900 truncate">
                            {job.company_name}
                          </p>
                        </div>
                        {job.evidence_proof?.verified && (
                          <CheckBadgeIcon
                            className="h-4 w-4 text-black shrink-0"
                            title="Đã xác thực minh bạch"
                          />
                        )}
                      </div>

                      {/* Job Title */}
                      <h4 className="text-xs font-black text-black line-clamp-2 hover:underline leading-snug">
                        <Link href={`/jobs/${job.id}`}>{job.title}</Link>
                      </h4>

                      {/* Salary & Location */}
                      <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                        <span className="font-bold text-neutral-900 bg-neutral-100 px-2 py-0.5 rounded-md border border-neutral-200">
                          {salaryDisplay}
                        </span>
                        <span className="text-neutral-500 flex items-center gap-0.5 truncate max-w-[130px]">
                          <MapPinIcon className="h-3 w-3 shrink-0" />
                          <span className="truncate">
                            {job.location_province || "Toàn quốc"}
                          </span>
                        </span>
                      </div>

                      {/* Private Note Area */}
                      {appliedRec?.notes && !isEditingNote && (
                        <div className="p-2 rounded-lg bg-neutral-50 border border-neutral-200 text-[11px] text-neutral-700 leading-relaxed flex items-start justify-between gap-1">
                          <span className="line-clamp-2">
                            💬 {appliedRec.notes}
                          </span>
                          <button
                            type="button"
                            onClick={() => {
                              setEditingNoteJobId(String(job.id));
                              setTempNote(appliedRec.notes || "");
                            }}
                            className="text-neutral-400 hover:text-black shrink-0"
                            title="Sửa ghi chú"
                          >
                            <PencilSquareIcon className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      )}

                      {/* Note Edit Mode */}
                      {isEditingNote && (
                        <div className="space-y-1.5 pt-1">
                          <textarea
                            rows={2}
                            value={tempNote}
                            onChange={(e) => setTempNote(e.target.value)}
                            placeholder="Ghi chú lịch phỏng vấn, liên hệ HR..."
                            className="w-full p-2 text-xs rounded-lg border border-neutral-300 focus:outline-none focus:ring-1 focus:ring-black"
                          />
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              type="button"
                              onClick={() => setEditingNoteJobId(null)}
                              className="text-[10px] text-neutral-500 hover:text-black px-2 py-1"
                            >
                              Hủy
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSaveNote(job.id)}
                              className="text-[10px] bg-black text-white px-2.5 py-1 rounded-md font-bold"
                            >
                              Lưu
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Stage Progression Buttons */}
                      <div className="pt-2 border-t border-neutral-100 flex items-center justify-between gap-1 text-[11px]">
                        {/* Left / Back Button */}
                        {col.id === "submitted" && (
                          <button
                            type="button"
                            onClick={() => removeApplied(job.id)}
                            className="inline-flex items-center gap-0.5 text-neutral-500 hover:text-black px-1.5 py-1 rounded hover:bg-neutral-100"
                            title="Chuyển về mục Đã Lưu"
                          >
                            <ChevronLeftIcon className="h-3 w-3" />
                            <span>Lưu</span>
                          </button>
                        )}
                        {col.id === "interviewing" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleMoveStage(
                                job.id,
                                "submitted",
                                appliedRec?.notes || ""
                              )
                            }
                            className="inline-flex items-center gap-0.5 text-neutral-500 hover:text-black px-1.5 py-1 rounded hover:bg-neutral-100"
                            title="Quay lại trạng thái Đã nộp"
                          >
                            <ChevronLeftIcon className="h-3 w-3" />
                            <span>Đã nộp</span>
                          </button>
                        )}
                        {col.id === "offer" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleMoveStage(
                                job.id,
                                "interviewing",
                                appliedRec?.notes || ""
                              )
                            }
                            className="inline-flex items-center gap-0.5 text-neutral-500 hover:text-black px-1.5 py-1 rounded hover:bg-neutral-100"
                            title="Quay lại trạng thái Phỏng vấn"
                          >
                            <ChevronLeftIcon className="h-3 w-3" />
                            <span>Phỏng vấn</span>
                          </button>
                        )}

                        {/* Note Trigger Button */}
                        {!isEditingNote && !appliedRec?.notes && (
                          <button
                            type="button"
                            onClick={() => {
                              setEditingNoteJobId(String(job.id));
                              setTempNote("");
                            }}
                            className="text-[10px] text-neutral-400 hover:text-black inline-flex items-center gap-0.5"
                          >
                            <PlusIcon className="h-3 w-3" />
                            <span>Ghi chú</span>
                          </button>
                        )}

                        {/* Right / Next Stage Button */}
                        {col.id === "saved" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleMoveStage(job.id, "submitted", "Đã nộp hồ sơ")
                            }
                            className="ml-auto inline-flex items-center gap-1 font-bold text-black hover:text-neutral-700 bg-neutral-100 px-2 py-1 rounded-lg border border-neutral-300"
                          >
                            <span>Nộp đơn</span>
                            <ChevronRightIcon className="h-3 w-3" />
                          </button>
                        )}
                        {col.id === "submitted" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleMoveStage(
                                job.id,
                                "interviewing",
                                appliedRec?.notes || ""
                              )
                            }
                            className="ml-auto inline-flex items-center gap-1 font-bold text-black hover:text-neutral-700 bg-neutral-100 px-2 py-1 rounded-lg border border-neutral-300"
                          >
                            <span>Phỏng vấn</span>
                            <ChevronRightIcon className="h-3 w-3" />
                          </button>
                        )}
                        {col.id === "interviewing" && (
                          <button
                            type="button"
                            onClick={() =>
                              handleMoveStage(
                                job.id,
                                "offer",
                                appliedRec?.notes || ""
                              )
                            }
                            className="ml-auto inline-flex items-center gap-1 font-bold text-white bg-black hover:bg-neutral-800 px-2.5 py-1 rounded-lg shadow-2xs"
                          >
                            <span>Nhận Offer 🏆</span>
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="h-32 border-2 border-dashed border-neutral-200 rounded-xl flex items-center justify-center text-center p-3 text-neutral-400 text-xs">
                  <span>Chưa có việc làm nào ở giai đoạn này</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
