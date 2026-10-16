"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  XMarkIcon,
  ClockIcon,
  FireIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  BoltIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { VIETNAM_PROVINCES } from "@/constants/vietnamData";
import { loadAllJobsForClient } from "@/lib/clientSearch";
import { Job } from "@/types/job";
import HighlightMatch, { stripTonesExact } from "@/components/HighlightMatch";

// Clear legacy search history keys from browser storage once
const LEGACY_RECENT_SEARCHES_KEY = "vinhviec_recent_searches";

const POPULAR_HALONG_SEARCHES = [
  { label: "IT & Phần mềm Hạ Long", q: "IT", prov: "Quảng Ninh" },
  { label: "Khách Sạn & Resort Bãi Cháy", q: "Khách Sạn", prov: "Quảng Ninh" },
  { label: "Kế toán tổng hợp", q: "Kế Toán", prov: "Quảng Ninh" },
  { label: "Cảng Cái Lân & KCN", q: "Cái Lân", prov: "Quảng Ninh" },
  { label: "Tập đoàn Than - TKV", q: "Khai Thác", prov: "Quảng Ninh" },
  { label: "Làm việc từ xa (Remote)", q: "Remote", prov: "" },
];

interface SearchBarProps {
  initialQuery?: string;
  initialProvince?: string;
  initialLive?: boolean;
  initialStrictMode?: boolean;
  initialVerifiedOnly?: boolean;
  compact?: boolean;
  className?: string;
}

export default function SearchBar({
  initialQuery = "",
  initialProvince = "",
  initialLive = false,
  initialStrictMode = false,
  initialVerifiedOnly = false,
  compact = false,
  className = "",
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [province, setProvince] = useState(initialProvince);
  const [liveCrawl, setLiveCrawl] = useState(initialLive);
  const [strictMode, setStrictMode] = useState(initialStrictMode);
  const [verifiedOnly, setVerifiedOnly] = useState(initialVerifiedOnly);

  // Autocomplete Suggestions State (No search history tracking)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync initial query & province
  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    setProvince(initialProvince);
  }, [initialProvince]);

  // Clean legacy search history from localStorage as requested
  useEffect(() => {
    try {
      localStorage.removeItem(LEGACY_RECENT_SEARCHES_KEY);
      localStorage.removeItem("c_data_recent_searches");
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  // Preload jobs for real-time suggestions
  useEffect(() => {
    loadAllJobsForClient()
      .then((jobs) => {
        if (Array.isArray(jobs)) {
          setAllJobs(jobs);
        }
      })
      .catch(() => {});
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Compute live suggestions when query is typed (>= 1 character)
  const suggestions = useMemo(() => {
    const trimmed = query.trim();
    if (!trimmed || allJobs.length === 0) {
      return { titles: [], companies: [], skills: [] };
    }

    const normQuery = stripTonesExact(trimmed).toLowerCase();
    const titleMap = new Map<string, number>();
    const companyMap = new Map<string, number>();
    const skillMap = new Map<string, number>();

    for (const job of allJobs) {
      // Match Title
      if (job.title) {
        const normTitle = stripTonesExact(job.title).toLowerCase();
        if (normTitle.includes(normQuery)) {
          titleMap.set(job.title, (titleMap.get(job.title) || 0) + 1);
        }
      }
      // Match Company
      if (job.company_name) {
        const normComp = stripTonesExact(job.company_name).toLowerCase();
        if (normComp.includes(normQuery)) {
          companyMap.set(job.company_name, (companyMap.get(job.company_name) || 0) + 1);
        }
      }
      // Match Tech Stack
      if (Array.isArray(job.tech_stack)) {
        for (const skill of job.tech_stack) {
          const normSkill = stripTonesExact(skill).toLowerCase();
          if (normSkill.includes(normQuery)) {
            skillMap.set(skill, (skillMap.get(skill) || 0) + 1);
          }
        }
      }
    }

    return {
      titles: Array.from(titleMap.entries())
        .slice(0, 4)
        .map(([text, count]) => ({ text, count })),
      companies: Array.from(companyMap.entries())
        .slice(0, 3)
        .map(([text, count]) => ({ text, count })),
      skills: Array.from(skillMap.entries())
        .slice(0, 3)
        .map(([text, count]) => ({ text, count })),
    };
  }, [query, allJobs]);

  // Flatten active suggestions for keyboard navigation
  const flatActiveItems = useMemo(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      return [];
    }
    const items: Array<{
      label: string;
      q: string;
      prov?: string;
      type: "title" | "company" | "skill";
    }> = [];
    suggestions.titles.forEach((t) =>
      items.push({ label: t.text, q: t.text, type: "title" })
    );
    suggestions.companies.forEach((c) =>
      items.push({ label: c.text, q: c.text, type: "company" })
    );
    suggestions.skills.forEach((s) =>
      items.push({ label: s.text, q: s.text, type: "skill" })
    );
    return items;
  }, [query, suggestions]);

  const executeSearch = (targetQuery: string, targetProvince?: string) => {
    setIsDropdownOpen(false);

    const params = new URLSearchParams();
    if (targetQuery.trim()) params.set("q", targetQuery.trim());
    const effProvince = targetProvince !== undefined ? targetProvince : province;
    if (effProvince) params.set("province", effProvince);
    if (liveCrawl) params.set("live", "true");
    if (strictMode) params.set("strict_mode", "true");
    if (verifiedOnly) params.set("verified_only", "true");

    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (
      highlightedIndex >= 0 &&
      highlightedIndex < flatActiveItems.length
    ) {
      const item = flatActiveItems[highlightedIndex];
      setQuery(item.q);
      if (item.prov !== undefined) setProvince(item.prov);
      executeSearch(item.q, item.prov);
    } else {
      executeSearch(query, province);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isDropdownOpen) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        setIsDropdownOpen(true);
      }
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev < flatActiveItems.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev > 0 ? prev - 1 : flatActiveItems.length - 1
      );
    } else if (e.key === "Escape") {
      setIsDropdownOpen(false);
      setHighlightedIndex(-1);
    }
  };

  const clearQuery = () => {
    setQuery("");
    setHighlightedIndex(-1);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const hasSuggestions =
    suggestions.titles.length > 0 ||
    suggestions.companies.length > 0 ||
    suggestions.skills.length > 0;

  return (
    <div ref={containerRef} className="relative w-full">
      <form
        onSubmit={handleSubmit}
        className={`w-full ${
          compact
            ? "bg-white p-2 rounded-2xl border border-neutral-300 shadow-xs"
            : "bg-white p-2.5 sm:p-3 rounded-2xl md:rounded-3xl border border-neutral-300 shadow-md focus-within:border-black"
        } ${className}`}
      >
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
          {/* Keyword Search Input */}
          <div className="relative flex-1 flex items-center">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-neutral-400">
              <MagnifyingGlassIcon className="h-5 w-5 text-neutral-400" />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setIsDropdownOpen(Boolean(e.target.value.trim()));
                setHighlightedIndex(-1);
              }}
              onFocus={() => {
                if (query.trim()) {
                  setIsDropdownOpen(true);
                }
              }}
              onKeyDown={handleKeyDown}
              placeholder="Chức danh, vị trí, kỹ năng (IT, Kế toán, Khách sạn...)"
              className="w-full pl-10 pr-9 py-3 text-sm sm:text-base text-neutral-900 placeholder-neutral-400 bg-transparent rounded-xl focus:outline-none font-medium"
              autoComplete="off"
            />
            {query && (
              <button
                type="button"
                onClick={clearQuery}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-neutral-400 hover:text-black cursor-pointer"
                title="Xóa từ khóa"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Divider in desktop */}
          <div className="hidden sm:block w-px h-8 bg-neutral-200 shrink-0" />

          {/* Province Select Dropdown */}
          <div className="relative w-full sm:w-60 flex items-center">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-neutral-400">
              <MapPinIcon className="h-5 w-5 text-neutral-400" />
            </div>
            <select
              value={province}
              onChange={(e) => setProvince(e.target.value)}
              className="w-full pl-10 pr-8 py-3 text-sm sm:text-base text-neutral-900 bg-neutral-50 sm:bg-transparent rounded-xl focus:outline-none font-medium cursor-pointer appearance-none"
            >
              <option value="">Toàn quốc (63 tỉnh)</option>
              <optgroup label="Tỉnh / Thành phố trọng điểm">
                {VIETNAM_PROVINCES.filter((p) => p.popular).map((p) => (
                  <option key={`pop-${p.code}`} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Tất cả các tỉnh khác">
                {VIETNAM_PROVINCES.filter((p) => !p.popular).map((p) => (
                  <option key={`all-${p.code}`} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </optgroup>
            </select>
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-neutral-400">
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-black hover:bg-neutral-800 text-white font-bold rounded-xl text-sm sm:text-base shadow-xs transition-colors shrink-0 cursor-pointer"
          >
            <span>Tìm việc</span>
          </button>
        </div>

        {/* Streamlined Filter Toggles & Popular Chips */}
        <div className="mt-3 pt-2.5 border-t border-neutral-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
          {/* Quick Filters */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar max-w-full py-0.5">
            <button
              type="button"
              onClick={() => setStrictMode(!strictMode)}
              className={`shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors cursor-pointer ${
                strictMode
                  ? "bg-black text-white border-black"
                  : "bg-neutral-100 text-neutral-700 border-neutral-200 hover:bg-neutral-200 hover:text-black"
              }`}
              title="Lọc chuẩn điều kiện cứng: không lẫn địa bàn khác"
            >
              <span>🎯 Khớp chuẩn</span>
            </button>

            <button
              type="button"
              onClick={() => setVerifiedOnly(!verifiedOnly)}
              className={`shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors cursor-pointer ${
                verifiedOnly
                  ? "bg-black text-white border-black"
                  : "bg-neutral-100 text-neutral-700 border-neutral-200 hover:bg-neutral-200 hover:text-black"
              }`}
              title="Chỉ hiển thị tin đã có bằng chứng xác thực"
            >
              <span>🛡️ Đã xác thực</span>
            </button>

            <button
              type="button"
              onClick={() => setLiveCrawl(!liveCrawl)}
              className={`shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors cursor-pointer ${
                liveCrawl
                  ? "bg-black text-white border-black"
                  : "bg-neutral-100 text-neutral-700 border-neutral-200 hover:bg-neutral-200 hover:text-black"
              }`}
              title="Kích hoạt quét sâu mạng xã hội Facebook, Threads"
            >
              <span>⚡ Quét MXH</span>
            </button>
          </div>

          {/* Clean Horizontal Popular Searches */}
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 w-full sm:w-auto">
            <span className="text-[11px] font-medium text-neutral-400 shrink-0">
              Gợi ý:
            </span>
            {POPULAR_HALONG_SEARCHES.slice(0, 5).map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => {
                  setQuery(chip.q);
                  if (chip.prov) setProvince(chip.prov);
                  executeSearch(chip.q, chip.prov);
                }}
                className="shrink-0 px-2.5 py-1 rounded-lg bg-neutral-100 hover:bg-neutral-200 text-neutral-800 hover:text-black border border-neutral-200 hover:border-black text-[11px] font-medium transition-colors cursor-pointer"
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      </form>

      {/* Autocomplete Suggestions Dropdown (Chỉ hiển thị khi đang gõ từ khóa) */}
      {isDropdownOpen && Boolean(query.trim()) && (
        <div className="absolute left-0 right-0 top-full mt-2 bg-white rounded-2xl border border-neutral-300 shadow-xl z-50 overflow-hidden divide-y divide-neutral-100 animate-fadeIn text-xs sm:text-sm">
          {hasSuggestions ? (
            /* Gợi ý autocomplete trực tiếp theo từ khóa đang gõ */
            <div className="p-2 sm:p-3 space-y-3 max-h-[380px] overflow-y-auto">
              {/* Job Titles Section */}
              {suggestions.titles.length > 0 && (
                <div>
                  <span className="px-2 py-1 text-[11px] font-bold text-neutral-400 uppercase tracking-wider block">
                    Vị trí / Chức danh công việc
                  </span>
                  <div className="space-y-0.5">
                    {suggestions.titles.map((titleItem, idx) => (
                      <div
                        key={titleItem.text}
                        onClick={() => {
                          setQuery(titleItem.text);
                          executeSearch(titleItem.text);
                        }}
                        className={`flex items-center justify-between p-2 rounded-xl cursor-pointer transition-colors ${
                          highlightedIndex === idx
                            ? "bg-neutral-100 font-bold text-black"
                            : "hover:bg-neutral-50 text-neutral-900"
                        }`}
                      >
                        <div className="flex items-center gap-2.5 truncate min-w-0">
                          <BriefcaseIcon className="h-4 w-4 text-neutral-500 shrink-0" />
                          <HighlightMatch
                            text={titleItem.text}
                            query={query}
                            className="truncate text-xs sm:text-sm font-medium"
                          />
                        </div>
                        <span className="text-[11px] font-semibold text-neutral-500 shrink-0 pl-2">
                          {titleItem.count} việc
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Companies Section */}
              {suggestions.companies.length > 0 && (
                <div>
                  <span className="px-2 py-1 text-[11px] font-bold text-neutral-400 uppercase tracking-wider block">
                    Doanh nghiệp & Đơn vị tuyển dụng
                  </span>
                  <div className="space-y-0.5">
                    {suggestions.companies.map((compItem, idx) => {
                      const itemIdx = suggestions.titles.length + idx;
                      return (
                        <div
                          key={compItem.text}
                          onClick={() => {
                            setQuery(compItem.text);
                            executeSearch(compItem.text);
                          }}
                          className={`flex items-center justify-between p-2 rounded-xl cursor-pointer transition-colors ${
                            highlightedIndex === itemIdx
                              ? "bg-neutral-100 font-bold text-black"
                              : "hover:bg-neutral-50 text-neutral-900"
                          }`}
                        >
                          <div className="flex items-center gap-2.5 truncate min-w-0">
                            <BuildingOfficeIcon className="h-4 w-4 text-neutral-500 shrink-0" />
                            <HighlightMatch
                              text={compItem.text}
                              query={query}
                              className="truncate text-xs sm:text-sm font-medium"
                            />
                          </div>
                          <span className="text-[11px] font-semibold text-neutral-500 shrink-0 pl-2">
                            {compItem.count} việc
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Skills Section */}
              {suggestions.skills.length > 0 && (
                <div>
                  <span className="px-2 py-1 text-[11px] font-bold text-neutral-400 uppercase tracking-wider block">
                    Kỹ năng &amp; Công nghệ
                  </span>
                  <div className="space-y-0.5">
                    {suggestions.skills.map((skillItem, idx) => {
                      const itemIdx =
                        suggestions.titles.length +
                        suggestions.companies.length +
                        idx;
                      return (
                        <div
                          key={skillItem.text}
                          onClick={() => {
                            setQuery(skillItem.text);
                            executeSearch(skillItem.text);
                          }}
                          className={`flex items-center justify-between p-2 rounded-xl cursor-pointer transition-colors ${
                            highlightedIndex === itemIdx
                              ? "bg-neutral-100 font-bold text-black"
                              : "hover:bg-neutral-50 text-neutral-900"
                          }`}
                        >
                          <div className="flex items-center gap-2.5 truncate min-w-0">
                            <BoltIcon className="h-4 w-4 text-neutral-500 shrink-0" />
                            <HighlightMatch
                              text={skillItem.text}
                              query={query}
                              className="truncate text-xs sm:text-sm font-medium"
                            />
                          </div>
                          <span className="text-[11px] font-semibold text-neutral-500 shrink-0 pl-2">
                            {skillItem.count} việc
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Mode 3: Query typed but no matches in local cache */
            <div className="p-4 text-center text-neutral-500 text-xs sm:text-sm">
              <p>Bấm Enter hoặc "Tìm việc" để tìm kiếm toàn diện cho "{query}"</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
