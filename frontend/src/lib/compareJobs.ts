"use client";

import { useEffect, useState } from "react";
import { Job } from "@/types/job";

const COMPARE_STORAGE_KEY = "cdata_compared_jobs";
const MAX_COMPARE_JOBS = 4;

export function getStoredComparedJobs(): Job[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(COMPARE_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveComparedJobs(jobs: Job[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(COMPARE_STORAGE_KEY, JSON.stringify(jobs.slice(0, MAX_COMPARE_JOBS)));
    window.dispatchEvent(new CustomEvent("cdata-compare-updated", { detail: jobs }));
  } catch {
    // ignore
  }
}

export function useCompareJobs() {
  const [comparedJobs, setComparedJobs] = useState<Job[]>([]);

  useEffect(() => {
    setComparedJobs(getStoredComparedJobs());

    const handleUpdate = (e: any) => {
      if (e.detail && Array.isArray(e.detail)) {
        setComparedJobs(e.detail);
      } else {
        setComparedJobs(getStoredComparedJobs());
      }
    };

    window.addEventListener("cdata-compare-updated", handleUpdate);
    window.addEventListener("storage", handleUpdate);
    return () => {
      window.removeEventListener("cdata-compare-updated", handleUpdate);
      window.removeEventListener("storage", handleUpdate);
    };
  }, []);

  const addJobToCompare = (job: Job): boolean => {
    const current = getStoredComparedJobs();
    if (current.some((j) => String(j.id) === String(job.id))) {
      return false; // already added
    }
    if (current.length >= MAX_COMPARE_JOBS) {
      return false; // maximum reached
    }
    const updated = [...current, job];
    saveComparedJobs(updated);
    setComparedJobs(updated);
    return true;
  };

  const removeJobFromCompare = (jobId: string | number) => {
    const current = getStoredComparedJobs();
    const updated = current.filter((j) => String(j.id) !== String(jobId));
    saveComparedJobs(updated);
    setComparedJobs(updated);
  };

  const clearCompareJobs = () => {
    saveComparedJobs([]);
    setComparedJobs([]);
  };

  const isJobCompared = (jobId: string | number) => {
    return comparedJobs.some((j) => String(j.id) === String(jobId));
  };

  return {
    comparedJobs,
    count: comparedJobs.length,
    addJobToCompare,
    removeJobFromCompare,
    clearCompareJobs,
    isJobCompared,
    isMaxReached: comparedJobs.length >= MAX_COMPARE_JOBS,
  };
}
