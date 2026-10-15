"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  SparklesIcon,
  BoltIcon,
  XMarkIcon,
  BuildingOffice2Icon,
  CurrencyDollarIcon,
  CheckBadgeIcon,
} from "@heroicons/react/24/outline";
import { VIETNAM_PROVINCES } from "@/constants/vietnamData";
import { Job } from "@/types/job";
import { loadAllJobsForClient, searchJobsRealtime } from "@/lib/clientSearch";

interface SearchBarProps {
  initialQuery?: string;
  initialProvince?: string;
  initialLive?: boolean;
  initialStrictMode?: boolean;
  initialVerifiedOnly?: boolean;
  compact?: boolean;
  className?: string;
  onRealtimeChange?: (query: string, province: string) => void;
}

export default function SearchBar({
  initialQuery = "",
  initialProvince = "",
  initialLive = false,
  initialStrictMode = false,
  initialVerifiedOnly = false,
  compact = false,
  className = "",
  onRealtimeChange,
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [province, setProvince] = useState(initialProvince);
  const [liveCrawl, setLiveCrawl] = useState(initialLive);
  const [strictMode, setStrictMode] = useState(initialStrictMode);
  const [verifiedOnly, setVerifiedOnly] = useState(initialVerifiedOnly);

  // Real-time search states
  const [realtimeJobs, setRealtimeJobs] = useState<Job[]>([]);
  const [realtimeTotal, setRealtimeTotal] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Lắng nghe thay đổi từ ngoài vào
  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    setProvince(initialProvince);
  }, [initialProvince]);

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Thực hiện tìm kiếm Real-time mỗi khi query hoặc province thay đổi
  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed && !province) {
      setRealtimeJobs([]);
      setRealtimeTotal(0);
      setIsOpen(false);
      onRealtimeChange?.("", province);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const allJobs = await loadAllJobsForClient();
        const results = searchJobsRealtime(allJobs, {
          q: trimmed,
          province: province || undefined,
          strict_mode: strictMode,
          verified_only: verifiedOnly,
          page_size: 6,
        });

        setRealtimeJobs(results.items);
        setRealtimeTotal(results.total);
        if (trimmed.length > 0 || province) {
          setIsOpen(true);
        }
      } catch (err) {
        console.warn("Realtime search error:", err);
      } finally {
        setIsSearching(false);
      }

      onRealtimeChange?.(trimmed, province);
    }, 150); // 150ms debounce cho trải nghiệm siêu mượt

    return () => clearTimeout(timer);
  }, [query, province, strictMode, verifiedOnly, onRealtimeChange]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsOpen(false);
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (province) params.set("province", province);
    if (liveCrawl) params.set("live", "true");
    if (strictMode) params.set("strict_mode", "true");
    if (verifiedOnly) params.set("verified_only", "true");

    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
  };

  const handleSelectJob = (jobId: string | number) => {
    setIsOpen(false);
    router.push(`/jobs/${jobId}`);
  };

  const clearQuery = () => {
    setQuery("");
    setRealtimeJobs([]);
    setIsOpen(false);
    onRealtimeChange?.("", province);
  };

  return (
    <div ref={containerRef} className="relative w-full">
      <form
        onSubmit={handleSubmit}
        className={`w-full ${
          compact
            ? "bg-white p-2 rounded-2xl border border-slate-200 shadow-sm"
            : "bg-white/95 backdrop-blur-md p-2.5 sm:p-3 rounded-2xl md:rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-200/60"
        } ${className}`}
      >
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
          {/* Keyword Search Input with Real-time indicator */}
          <div className="relative flex-1 flex items-center">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              {isSearching ? (
                <div className="h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              ) : (
                <MagnifyingGlassIcon className="h-5 w-5 text-slate-400" />
              )}
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => {
                if (query.trim() || province) setIsOpen(true);
              }}
              placeholder="Chức danh, vị trí, kỹ năng (IT, Kế toán, Khách sạn...)"
              className="w-full pl-10 pr-9 py-3 text-sm sm:text-base text-slate-800 placeholder-slate-400 bg-transparent rounded-xl focus:outline-none font-medium"
            />
            {query && (
              <button
                type="button"
                onClick={clearQuery}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Divider in desktop */}
          <div className="hidden sm:block w-px h-8 bg-slate-200 shrink-0" />

          {/* Province Select Dropdown */}
          <div className="relative w-full sm:w-60 flex items-center">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <MapPinIcon className="h-5 w-5 text-slate-400" />
            </div>
            <select
              value={province}
              onChange={(e) => setProvince(e.target.value)}
              className="w-full pl-10 pr-8 py-3 text-sm sm:text-base text-slate-800 bg-slate-50 sm:bg-transparent rounded-xl focus:outline-none font-medium cursor-pointer appearance-none"
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
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
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
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm sm:text-base shadow-xs transition-colors shrink-0"
          >
            <span>Tìm việc</span>
          </button>
        </div>

        {/* Streamlined Filter Toggles & Popular Chips */}
        <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2.5 text-xs">
          {/* Quick Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setStrictMode(!strictMode)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                strictMode
                  ? "bg-blue-50 text-blue-700 border-blue-200 font-semibold"
                  : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
              title="Lọc chuẩn điều kiện cứng: không lẫn địa bàn khác"
            >
              <span>🎯 Khớp chuẩn</span>
            </button>

            <button
              type="button"
              onClick={() => setVerifiedOnly(!verifiedOnly)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                verifiedOnly
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200 font-semibold"
                  : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
              title="Chỉ hiển thị tin đã có bằng chứng xác thực"
            >
              <span>🛡️ Đã xác thực</span>
            </button>

            <button
              type="button"
              onClick={() => setLiveCrawl(!liveCrawl)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-colors cursor-pointer ${
                liveCrawl
                  ? "bg-amber-50 text-amber-800 border-amber-200 font-semibold"
                  : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100"
              }`}
              title="Kích hoạt quét sâu mạng xã hội Facebook, Threads"
            >
              <span>⚡ Quét MXH</span>
            </button>
          </div>

          {/* Clean Horizontal Popular Searches */}
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 max-w-full">
            <span className="text-[11px] font-medium text-slate-400 shrink-0">
              Gợi ý:
            </span>
            {[
              { label: "IT Hạ Long", q: "IT", prov: "Quảng Ninh" },
              { label: "Khách Sạn Bãi Cháy", q: "Khách Sạn", prov: "Quảng Ninh" },
              { label: "Ngành Than", q: "Khai Thác", prov: "Quảng Ninh" },
              { label: "Cảng Cái Lân", q: "Cái Lân", prov: "Quảng Ninh" },
              { label: "FPT Telecom", q: "FPT", prov: "Quảng Ninh" },
              { label: "Làm từ xa", q: "Remote", prov: "" },
            ].map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => {
                  setQuery(chip.q);
                  if (chip.prov) setProvince(chip.prov);
                }}
                className="shrink-0 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-blue-50 text-slate-600 hover:text-blue-700 text-[11px] font-medium transition-colors cursor-pointer"
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      </form>

      {/* POPUP DROPDOWN TÌM KIẾM THỜI GIAN THỰC (REAL-TIME INSTANT RESULTS) */}
      {isOpen && (query.trim() || province) && (
        <div className="absolute top-full left-0 right-0 mt-2 z-50 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {/* Header dropdown */}
          <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-bold text-slate-800">
                Tìm kiếm tức thì (Real-time):{" "}
                <strong className="text-primary-700 font-black">
                  {realtimeTotal}
                </strong>{" "}
                việc làm phù hợp
              </span>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-slate-600 text-xs font-semibold"
            >
              Đóng ✕
            </button>
          </div>

          {/* Danh sách công việc tìm thấy trong thời gian thực */}
          <div className="max-h-[380px] overflow-y-auto divide-y divide-slate-100">
            {realtimeJobs.length > 0 ? (
              realtimeJobs.map((job) => (
                <div
                  key={job.id}
                  onClick={() => handleSelectJob(job.id)}
                  className="p-3.5 sm:p-4 hover:bg-slate-50/90 cursor-pointer transition-colors flex items-start justify-between gap-3 group"
                >
                  <div className="space-y-1 min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-sm font-bold text-slate-900 group-hover:text-primary-600 transition-colors line-clamp-1">
                        {job.title}
                      </h4>
                      {job.evidence_proof?.verified && (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-300 shrink-0">
                          ✓ Dẫn chứng
                        </span>
                      )}
                      {job.match_score && job.match_score > 30 && (
                        <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 shrink-0">
                          ⚡ {Math.round(job.match_score)}% phù hợp
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-500 flex-wrap">
                      <span className="flex items-center gap-1 font-medium text-slate-700 truncate max-w-[200px]">
                        <BuildingOffice2Icon className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                        <span>{job.company_name}</span>
                        <CheckBadgeIcon className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                      </span>

                      <span className="flex items-center gap-1 text-slate-600">
                        <MapPinIcon className="h-3.5 w-3.5 text-accent-500 shrink-0" />
                        <span>{job.location_province || "Quảng Ninh"}</span>
                      </span>

                      <span className="flex items-center gap-1 font-semibold text-emerald-600">
                        <CurrencyDollarIcon className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                        <span>{job.salary_text || "Thỏa thuận"}</span>
                      </span>
                    </div>

                    {job.match_reasons && job.match_reasons.length > 0 && (
                      <p className="text-[11px] text-primary-600 font-medium line-clamp-1">
                        ✓ {job.match_reasons[0]}
                      </p>
                    )}
                  </div>

                  <div className="text-right shrink-0">
                    <span className="inline-block px-2.5 py-1 rounded-lg bg-primary-50 text-primary-700 font-bold text-xs group-hover:bg-primary-600 group-hover:text-white transition-all shadow-2xs">
                      Xem ngay ➔
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-8 text-center space-y-2">
                <p className="text-sm font-semibold text-slate-700">
                  Không tìm thấy việc làm nào khớp hoàn toàn với "{query}"
                </p>
                <p className="text-xs text-slate-500">
                  Thử tìm kiếm với từ khóa ngắn gọn hơn như: "IT", "Khách sạn", "Kế toán"
                </p>
              </div>
            )}
          </div>

          {/* Footer nút xem tất cả */}
          {realtimeTotal > 0 && (
            <div className="p-3 bg-slate-50 border-t border-slate-100 text-center">
              <button
                type="button"
                onClick={handleSubmit}
                className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-bold text-primary-600 hover:text-primary-700 transition-colors"
              >
                <span>Xem toàn bộ {realtimeTotal} việc làm cho</span>
                <span className="underline">
                  "{query.trim() || province || "Tất cả"}"
                </span>
                <span>➔</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
