"use client";

import { useEffect, useState } from "react";
import { Job } from "@/types/job";

const APPLIED_STORAGE_KEY = "vinhviec_applied_jobs_v1";
const DISMISSED_STORAGE_KEY = "vinhviec_dismissed_jobs_v1";

export type ApplicationStage = "submitted" | "interviewing" | "offer" | "rejected";

export interface AppliedJobRecord {
  jobId: string;
  appliedAt: string;
  stage: ApplicationStage;
  notes?: string;
}

// ==========================================
// 1. APPLIED JOBS TRACKING
// ==========================================

export function getAppliedJobs(): Record<string, AppliedJobRecord> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(APPLIED_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function isJobApplied(jobId: string | number): boolean {
  const applied = getAppliedJobs();
  return Boolean(applied[String(jobId)]);
}

export function getAppliedRecord(jobId: string | number): AppliedJobRecord | null {
  const applied = getAppliedJobs();
  return applied[String(jobId)] || null;
}

export function markJobApplied(
  jobId: string | number,
  stage: ApplicationStage = "submitted",
  notes: string = ""
): boolean {
  if (typeof window === "undefined") return false;
  try {
    const applied = getAppliedJobs();
    const id = String(jobId);
    applied[id] = {
      jobId: id,
      appliedAt: new Date().toISOString(),
      stage,
      notes: notes.trim(),
    };
    localStorage.setItem(APPLIED_STORAGE_KEY, JSON.stringify(applied));
    window.dispatchEvent(new Event("cdata-application-tracker-updated"));
    return true;
  } catch {
    return false;
  }
}

export function removeJobApplied(jobId: string | number): boolean {
  if (typeof window === "undefined") return false;
  try {
    const applied = getAppliedJobs();
    const id = String(jobId);
    if (applied[id]) {
      delete applied[id];
      localStorage.setItem(APPLIED_STORAGE_KEY, JSON.stringify(applied));
      window.dispatchEvent(new Event("cdata-application-tracker-updated"));
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

export function toggleJobApplied(jobId: string | number): boolean {
  if (isJobApplied(jobId)) {
    removeJobApplied(jobId);
    return false;
  } else {
    markJobApplied(jobId, "submitted", "Đã nộp hồ sơ ứng tuyển");
    return true;
  }
}

// ==========================================
// 2. DISMISSED / HIDDEN JOBS TRACKING
// ==========================================

export function getDismissedJobIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(DISMISSED_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function isJobDismissed(jobId: string | number): boolean {
  const dismissed = getDismissedJobIds();
  return dismissed.includes(String(jobId));
}

export function toggleDismissJob(jobId: string | number): boolean {
  if (typeof window === "undefined") return false;
  try {
    const dismissed = getDismissedJobIds();
    const id = String(jobId);
    let next: string[];
    let isHidden = false;

    if (dismissed.includes(id)) {
      next = dismissed.filter((x) => x !== id);
      isHidden = false;
    } else {
      next = [id, ...dismissed];
      isHidden = true;
    }

    localStorage.setItem(DISMISSED_STORAGE_KEY, JSON.stringify(next));
    window.dispatchEvent(new Event("cdata-application-tracker-updated"));
    return isHidden;
  } catch {
    return false;
  }
}

// ==========================================
// 3. REACT HOOK FOR REALTIME SYNC
// ==========================================

export function useApplicationTracker() {
  const [appliedMap, setAppliedMap] = useState<Record<string, AppliedJobRecord>>({});
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);

  useEffect(() => {
    const sync = () => {
      setAppliedMap(getAppliedJobs());
      setDismissedIds(getDismissedJobIds());
    };
    sync();

    window.addEventListener("cdata-application-tracker-updated", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("cdata-application-tracker-updated", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  return {
    appliedMap,
    dismissedIds,
    appliedCount: Object.keys(appliedMap).length,
    dismissedCount: dismissedIds.length,
    isApplied: (id: string | number) => Boolean(appliedMap[String(id)]),
    isDismissed: (id: string | number) => dismissedIds.includes(String(id)),
    toggleApplied: toggleJobApplied,
    toggleDismiss: toggleDismissJob,
    markApplied: markJobApplied,
    removeApplied: removeJobApplied,
  };
}

// ==========================================
// 4. CSV / EXCEL EXPORT UTILITY (UTF-8 BOM)
// ==========================================

export function exportJobsToCSV(jobs: Job[], filename: string = "vinhviec_jobs.csv"): void {
  if (typeof window === "undefined" || !jobs || jobs.length === 0) return;

  const appliedMap = getAppliedJobs();

  const headers = [
    "ID",
    "Tiêu đề việc làm",
    "Doanh nghiệp",
    "Tỉnh/Thành",
    "Quận/Huyện",
    "Mức lương",
    "Nền tảng nguồn",
    "Trạng thái nộp đơn",
    "Ngày nộp",
    "Ghi chú",
    "Link tuyển dụng gốc",
  ];

  const escapeCSV = (val: any) => {
    if (val === null || val === undefined) return '""';
    const str = String(val).replace(/"/g, '""');
    return `"${str}"`;
  };

  const rows = jobs.map((j) => {
    const appRecord = appliedMap[String(j.id)];
    const appStatus = appRecord ? `Đã nộp (${appRecord.stage})` : "Chưa nộp";
    const appDate = appRecord?.appliedAt ? new Date(appRecord.appliedAt).toLocaleDateString("vi-VN") : "";
    const appNotes = appRecord?.notes || "";

    return [
      escapeCSV(j.id),
      escapeCSV(j.title),
      escapeCSV(j.company_name),
      escapeCSV(j.location_province || "Toàn quốc"),
      escapeCSV(j.location_district || ""),
      escapeCSV(j.salary_text || "Thỏa thuận"),
      escapeCSV(j.source_platform || "Website"),
      escapeCSV(appStatus),
      escapeCSV(appDate),
      escapeCSV(appNotes),
      escapeCSV(j.source_url || ""),
    ].join(",");
  });

  // UTF-8 BOM prefix for Excel Vietnamese compatibility
  const csvContent = "\uFEFF" + [headers.join(","), ...rows].join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
