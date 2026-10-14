"use client";

import { useEffect, useState } from "react";
import { Job } from "@/types/job";

const STORAGE_KEY = "cdata_saved_jobs_v1";

export function getSavedJobIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function isJobSaved(jobId: string): boolean {
  const ids = getSavedJobIds();
  return ids.includes(jobId);
}

export function toggleSaveJob(jobId: string): boolean {
  if (typeof window === "undefined") return false;
  try {
    const ids = getSavedJobIds();
    const idx = ids.indexOf(jobId);
    let nextIds: string[];
    let saved = false;

    if (idx >= 0) {
      nextIds = ids.filter((id) => id !== jobId);
      saved = false;
    } else {
      nextIds = [jobId, ...ids];
      saved = true;
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextIds));
    window.dispatchEvent(new Event("cdata-saved-jobs-updated"));
    return saved;
  } catch {
    return false;
  }
}

export function useSavedJobs() {
  const [savedIds, setSavedIds] = useState<string[]>([]);

  useEffect(() => {
    setSavedIds(getSavedJobIds());

    const handleUpdate = () => {
      setSavedIds(getSavedJobIds());
    };

    window.addEventListener("cdata-saved-jobs-updated", handleUpdate);
    window.addEventListener("storage", handleUpdate);

    return () => {
      window.removeEventListener("cdata-saved-jobs-updated", handleUpdate);
      window.removeEventListener("storage", handleUpdate);
    };
  }, []);

  return {
    savedIds,
    count: savedIds.length,
    isSaved: (id: string) => savedIds.includes(id),
    toggle: (id: string) => toggleSaveJob(id),
  };
}
