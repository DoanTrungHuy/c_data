"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { VIETNAM_PROVINCES } from "@/constants/vietnamData";

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

  // Đồng bộ giá trị khởi tạo khi URL thay đổi
  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    setProvince(initialProvince);
  }, [initialProvince]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (province) params.set("province", province);
    if (liveCrawl) params.set("live", "true");
    if (strictMode) params.set("strict_mode", "true");
    if (verifiedOnly) params.set("verified_only", "true");

    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
  };

  const clearQuery = () => {
    setQuery("");
  };

  return (
    <div className="relative w-full">
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
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Chức danh, vị trí, kỹ năng (IT, Kế toán, Khách sạn...)"
              className="w-full pl-10 pr-9 py-3 text-sm sm:text-base text-neutral-900 placeholder-neutral-400 bg-transparent rounded-xl focus:outline-none font-medium"
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
                  const params = new URLSearchParams();
                  if (chip.q.trim()) params.set("q", chip.q.trim());
                  if (chip.prov) params.set("province", chip.prov);
                  if (liveCrawl) params.set("live", "true");
                  if (strictMode) params.set("strict_mode", "true");
                  if (verifiedOnly) params.set("verified_only", "true");
                  router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
                }}
                className="shrink-0 px-2.5 py-1 rounded-lg bg-neutral-100 hover:bg-neutral-200 text-neutral-800 hover:text-black border border-neutral-200 hover:border-black text-[11px] font-medium transition-colors cursor-pointer"
              >
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
}
