"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { VIETNAM_PROVINCES } from "@/constants/vietnamData";

interface SearchBarProps {
  initialQuery?: string;
  initialProvince?: string;
  initialLive?: boolean;
  initialStrictMode?: boolean;
  compact?: boolean;
  className?: string;
}

export default function SearchBar({
  initialQuery = "",
  initialProvince = "",
  initialLive = false,
  initialStrictMode = false,
  compact = false,
  className = "",
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [province, setProvince] = useState(initialProvince);
  const [liveCrawl, setLiveCrawl] = useState(initialLive);
  const [strictMode, setStrictMode] = useState(initialStrictMode);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (province) params.set("province", province);
    if (liveCrawl) params.set("live", "true");
    if (strictMode) params.set("strict_mode", "true");

    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`w-full ${
        compact
          ? "bg-white p-2 rounded-2xl border border-slate-200 shadow-sm"
          : "bg-white/95 backdrop-blur-md p-2.5 sm:p-3 rounded-2xl md:rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-200/60"
      } ${className}`}
    >
      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-2 md:gap-3">
        {/* Keyword Search Input */}
        <div className="relative flex-1 flex items-center">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            <MagnifyingGlassIcon className="h-5 w-5" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Chức danh, từ khóa hoặc công ty..."
            className="w-full pl-10 pr-4 py-3 text-sm md:text-base text-slate-800 placeholder-slate-400 bg-transparent rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 font-medium"
          />
        </div>

        {/* Divider in desktop */}
        <div className="hidden md:block w-px h-8 bg-slate-200 shrink-0" />

        {/* Province Select Dropdown */}
        <div className="relative w-full md:w-64 flex items-center">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            <MapPinIcon className="h-5 w-5 text-accent-500" />
          </div>
          <select
            value={province}
            onChange={(e) => setProvince(e.target.value)}
            className="w-full pl-10 pr-8 py-3 text-sm md:text-base text-slate-800 bg-slate-50 md:bg-transparent rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 font-medium cursor-pointer appearance-none"
          >
            <option value="">Tất cả tỉnh thành (63 tỉnh)</option>
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
          className="inline-flex items-center justify-center gap-2 px-6 py-3 md:py-3.5 bg-gradient-to-r from-accent-500 to-amber-500 hover:from-accent-600 hover:to-amber-600 text-white font-bold rounded-xl text-sm md:text-base shadow-md shadow-accent-500/25 transition-all duration-200 active:scale-95 shrink-0"
        >
          <SparklesIcon className="h-5 w-5 text-white/90" />
          <span>Tìm việc</span>
        </button>
      </div>

      {/* Search Mode Toggles: Live Crawl & Strict Mode */}
      <div className="mt-2.5 px-2 flex flex-wrap items-center justify-between gap-3 text-xs border-t border-slate-100 pt-2">
        <div className="flex flex-wrap items-center gap-4">
          {/* Strict Constraint Matching */}
          <label className="inline-flex items-center gap-1.5 cursor-pointer select-none text-slate-700 hover:text-slate-900 transition-colors">
            <input
              type="checkbox"
              checked={strictMode}
              onChange={(e) => setStrictMode(e.target.checked)}
              className="rounded text-primary-600 focus:ring-primary-500 h-3.5 w-3.5 border-slate-300"
            />
            <span className="font-semibold flex items-center gap-1">
              <span>🎯</span>
              <span>Khớp chuẩn ràng buộc cứng (Địa bàn, Remote, Không công tác xa)</span>
            </span>
          </label>

          {/* Realtime Live Crawl Toggle */}
          <label className="inline-flex items-center gap-1.5 cursor-pointer select-none text-slate-700 hover:text-slate-900 transition-colors">
            <input
              type="checkbox"
              checked={liveCrawl}
              onChange={(e) => setLiveCrawl(e.target.checked)}
              className="rounded text-amber-500 focus:ring-amber-400 h-3.5 w-3.5 border-slate-300"
            />
            <span className="font-semibold flex items-center gap-1">
              <span className="text-amber-500 font-bold">⚡</span>
              <span>Bật Quét Realtime Đa Nguồn (Sàn + MXH + Cổng công ty)</span>
            </span>
          </label>
        </div>

        <div className="flex items-center gap-2">
          {strictMode && (
            <span className="text-[11px] font-bold text-primary-700 bg-primary-50 border border-primary-200 px-2 py-0.5 rounded-full">
              Khớp chuẩn xác ON
            </span>
          )}
          {liveCrawl && (
            <span className="text-[11px] font-bold text-amber-600 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full animate-pulse">
              Live Crawl ON
            </span>
          )}
        </div>
      </div>

      {/* Popular quick keywords chips */}
      <div className="mt-2.5 px-2 pt-2 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-xs">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">
          🔥 Từ khóa hot:
        </span>
        {[
          "IT Officer Khách Sạn",
          "Lập trình viên React",
          "IT Helpdesk",
          "Lễ Tân Du Thuyền 5 Sao",
          "Tài Xế Lái Xe B2",
          "Giao Dịch Viên",
          "Phục Vụ Cà Phê / Nhà Hàng",
          "Kế Toán Kho",
        ].map((kw) => (
          <button
            key={kw}
            type="button"
            onClick={() => {
              setQuery(kw);
              const params = new URLSearchParams();
              params.set("q", kw);
              if (province) params.set("province", province);
              if (liveCrawl) params.set("live", "true");
              router.push(`/jobs?${params.toString()}`);
            }}
            className="px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-primary-50 hover:text-primary-600 text-slate-600 text-[11px] font-medium transition-colors border border-slate-200/60"
          >
            {kw}
          </button>
        ))}
      </div>
    </form>
  );
}
