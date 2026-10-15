"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  FunnelIcon,
  XMarkIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import {
  VIETNAM_PROVINCES,
  POPULAR_CATEGORIES,
  JOB_TYPES,
  SALARY_RANGES,
  SOURCE_PLATFORMS,
} from "@/constants/vietnamData";

interface FilterSidebarProps {
  onCloseMobile?: () => void;
  className?: string;
}

export default function FilterSidebar({
  onCloseMobile,
  className = "",
}: FilterSidebarProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read current filters from URL
  const selectedProvince = searchParams?.get("province") || "";
  const selectedCategory = searchParams?.get("category") || "";
  const selectedJobType = searchParams?.get("job_type") || "";
  const selectedPlatform = searchParams?.get("source_platform") || "";
  const selectedSalaryMin = searchParams?.get("salary_min") || "";
  const selectedSalaryMax = searchParams?.get("salary_max") || "";
  const selectedQualityTier = searchParams?.get("quality_tier") || "";
  const selectedTech = searchParams?.get("tech_stack") || "";

  // Local state for searching provinces
  const [provinceSearch, setProvinceSearch] = useState("");

  const updateParam = (key: string, value: string | undefined | null) => {
    const params = new URLSearchParams(searchParams?.toString() || "");
    if (value && value !== "") {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    // Reset to page 1 whenever filter changes
    params.delete("page");

    router.push(`/jobs?${params.toString()}`);
  };

  const handleSalaryChange = (min?: number, max?: number) => {
    const params = new URLSearchParams(searchParams?.toString() || "");
    if (min !== undefined) {
      params.set("salary_min", min.toString());
    } else {
      params.delete("salary_min");
    }

    if (max !== undefined) {
      params.set("salary_max", max.toString());
    } else {
      params.delete("salary_max");
    }
    params.delete("page");
    router.push(`/jobs?${params.toString()}`);
  };

  const handleResetFilters = () => {
    const params = new URLSearchParams();
    const currentQ = searchParams?.get("q");
    if (currentQ) params.set("q", currentQ);
    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
    if (onCloseMobile) onCloseMobile();
  };

  const hasActiveFilters = Boolean(
    selectedProvince ||
      selectedCategory ||
      selectedJobType ||
      selectedPlatform ||
      selectedSalaryMin ||
      selectedSalaryMax ||
      selectedQualityTier ||
      selectedTech
  );

  const filteredProvinces = VIETNAM_PROVINCES.filter((p) =>
    p.name.toLowerCase().includes(provinceSearch.toLowerCase())
  );

  return (
    <aside
      className={`w-full bg-white rounded-2xl border border-neutral-200 p-5 shadow-xs space-y-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-neutral-100">
        <div className="flex items-center gap-2 text-black font-bold text-base">
          <FunnelIcon className="h-5 w-5 text-black" />
          <span>Bộ lọc tìm kiếm</span>
        </div>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={handleResetFilters}
            className="flex items-center gap-1 text-xs font-semibold text-neutral-600 hover:text-black hover:underline cursor-pointer"
          >
            <ArrowPathIcon className="h-3.5 w-3.5" />
            <span>Xóa lọc</span>
          </button>
        )}

        {onCloseMobile && (
          <button
            type="button"
            onClick={onCloseMobile}
            className="lg:hidden p-1 text-neutral-400 hover:text-black rounded-lg cursor-pointer"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* 0. Quality Tier Filter */}
      <div className="space-y-2 pb-4 border-b border-neutral-100">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-black flex items-center gap-1">
            <span>💎 Thẩm Định Chất Lượng</span>
          </label>
          {selectedQualityTier && (
            <button
              onClick={() => updateParam("quality_tier", "")}
              className="text-[10px] text-neutral-600 hover:text-black hover:underline font-semibold cursor-pointer"
            >
              Đặt lại
            </button>
          )}
        </div>
        <div className="space-y-1 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-neutral-100 text-neutral-800">
            <input
              type="radio"
              name="quality_tier"
              value=""
              checked={selectedQualityTier === ""}
              onChange={() => updateParam("quality_tier", "")}
              className="text-black focus:ring-black"
            />
            <span>Tất cả tin tuyển dụng</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-neutral-100 text-black font-bold">
            <input
              type="radio"
              name="quality_tier"
              value="diamond"
              checked={selectedQualityTier === "diamond"}
              onChange={() => updateParam("quality_tier", "diamond")}
              className="text-black focus:ring-black"
            />
            <span>💎 Thẩm định Kim Cương (≥ 85đ)</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-neutral-100 text-black font-semibold">
            <input
              type="radio"
              name="quality_tier"
              value="gold"
              checked={selectedQualityTier === "gold"}
              onChange={() => updateParam("quality_tier", "gold")}
              className="text-black focus:ring-black"
            />
            <span>⭐ Đạt chuẩn kiểm định (≥ 70đ)</span>
          </label>
        </div>
      </div>

      {/* Tech Stack Cloud Filter */}
      <div className="space-y-2 pb-4 border-b border-neutral-200">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-black flex items-center gap-1">
            <span>⚡ Kỹ Năng / Tech Stack</span>
          </label>
          {selectedTech && (
            <button
              onClick={() => updateParam("tech_stack", "")}
              className="text-[10px] text-neutral-500 hover:text-black hover:underline font-semibold cursor-pointer"
            >
              Bỏ chọn
            </button>
          )}
        </div>
        <div className="flex flex-wrap gap-1.5 pt-1">
          {[
            "Cisco", "Fortinet", "Windows Server", "Linux", "Opera PMS",
            "Micros POS", "SCADA / DCS", "PLC Siemens", "HIS Quản Lý Bệnh Viện",
            "Python", "React.js", "SQL Server", "ERP SAP", "Docker & Container"
          ].map((tech) => (
            <button
              key={tech}
              type="button"
              onClick={() => updateParam("tech_stack", selectedTech === tech ? "" : tech)}
              className={`text-[11px] font-bold px-2 py-1 rounded-lg border transition-all cursor-pointer ${
                selectedTech === tech
                  ? "bg-black text-white border-black shadow-xs"
                  : "bg-neutral-100 text-neutral-800 border-neutral-200 hover:bg-neutral-200"
              }`}
            >
              {tech}
            </button>
          ))}
        </div>
      </div>

      {/* 1. Province Filter */}
      <div className="space-y-2">
        <label className="text-xs font-bold uppercase tracking-wider text-neutral-700">
          Địa điểm (Tỉnh / Thành phố)
        </label>
        <div className="relative mb-2">
          <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-neutral-400" />
          <input
            type="text"
            placeholder="Lọc tỉnh thành..."
            value={provinceSearch}
            onChange={(e) => setProvinceSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-neutral-300 focus:outline-none focus:ring-1 focus:ring-black"
          />
        </div>
        <div className="max-h-40 overflow-y-auto pr-1 space-y-1 text-sm">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700">
            <input
              type="radio"
              name="province"
              value=""
              checked={selectedProvince === ""}
              onChange={() => updateParam("province", "")}
              className="text-black focus:ring-black accent-black rounded"
            />
            <span className="text-xs font-medium">Tất cả địa điểm</span>
          </label>
          {filteredProvinces.map((prov) => (
            <label
              key={prov.code}
              className="flex items-center justify-between cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700"
            >
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="province"
                  value={prov.name}
                  checked={selectedProvince === prov.name}
                  onChange={() => updateParam("province", prov.name)}
                  className="text-black focus:ring-black accent-black"
                />
                <span className="text-xs">{prov.name}</span>
              </div>
              {prov.popular && (
                <span className="text-[10px] font-bold text-black bg-neutral-200 px-1.5 py-0.5 rounded">
                  Hot
                </span>
              )}
            </label>
          ))}
        </div>
      </div>

      {/* 2. Category Filter */}
      <div className="space-y-2 pt-4 border-t border-neutral-200">
        <label className="text-xs font-bold uppercase tracking-wider text-neutral-700">
          Ngành nghề chuyên môn
        </label>
        <div className="space-y-1.5 text-sm max-h-48 overflow-y-auto pr-1">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700">
            <input
              type="radio"
              name="category"
              value=""
              checked={selectedCategory === ""}
              onChange={() => updateParam("category", "")}
              className="text-black focus:ring-black accent-black"
            />
            <span className="text-xs font-medium">Tất cả ngành nghề</span>
          </label>
          {POPULAR_CATEGORIES.map((cat) => (
            <label
              key={cat.slug}
              className="flex items-center justify-between cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700"
            >
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="category"
                  value={cat.name}
                  checked={selectedCategory === cat.name}
                  onChange={() => updateParam("category", cat.name)}
                  className="text-black focus:ring-black accent-black"
                />
                <span className="text-xs line-clamp-1">{cat.name}</span>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* 3. Job Type Filter */}
      <div className="space-y-2 pt-4 border-t border-neutral-200">
        <label className="text-xs font-bold uppercase tracking-wider text-neutral-700">
          Hình thức làm việc
        </label>
        <div className="space-y-1.5 text-sm">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700">
            <input
              type="radio"
              name="job_type"
              value=""
              checked={selectedJobType === ""}
              onChange={() => updateParam("job_type", "")}
              className="text-black focus:ring-black accent-black"
            />
            <span className="text-xs font-medium">Tất cả hình thức</span>
          </label>
          {JOB_TYPES.map((jt) => (
            <label
              key={jt.value}
              className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700"
            >
              <input
                type="radio"
                name="job_type"
                value={jt.value}
                checked={selectedJobType === jt.value}
                onChange={() => updateParam("job_type", jt.value)}
                className="text-black focus:ring-black accent-black"
              />
              <span className="text-xs">{jt.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 4. Salary Range Filter */}
      <div className="space-y-2 pt-4 border-t border-neutral-200">
        <label className="text-xs font-bold uppercase tracking-wider text-neutral-700">
          Mức lương
        </label>
        <div className="space-y-1.5 text-sm">
          {SALARY_RANGES.map((range, idx) => {
            const isChecked =
              (range.min === undefined &&
                range.max === undefined &&
                !selectedSalaryMin &&
                !selectedSalaryMax) ||
              (String(range.min) === selectedSalaryMin &&
                String(range.max) === selectedSalaryMax);

            return (
              <label
                key={`sal-${idx}`}
                className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700"
              >
                <input
                  type="radio"
                  name="salary_range"
                  checked={isChecked}
                  onChange={() => handleSalaryChange(range.min, range.max)}
                  className="text-black focus:ring-black accent-black"
                />
                <span className="text-xs">{range.label}</span>
              </label>
            );
          })}
        </div>
      </div>

      {/* 5. Source Platform Filter */}
      <div className="space-y-2 pt-4 border-t border-neutral-200">
        <label className="text-xs font-bold uppercase tracking-wider text-neutral-700">
          Nguồn tuyển dụng
        </label>
        <div className="space-y-1.5 text-sm">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700">
            <input
              type="radio"
              name="source_platform"
              value=""
              checked={selectedPlatform === ""}
              onChange={() => updateParam("source_platform", "")}
              className="text-black focus:ring-black accent-black"
            />
            <span className="text-xs font-medium">Tất cả nguồn</span>
          </label>
          {SOURCE_PLATFORMS.map((platform) => (
            <label
              key={platform.id}
              className="flex items-center gap-2 cursor-pointer p-1 rounded hover:bg-neutral-100 text-neutral-700"
            >
              <input
                type="radio"
                name="source_platform"
                value={platform.id}
                checked={selectedPlatform === platform.id}
                onChange={() => updateParam("source_platform", platform.id)}
                className="text-black focus:ring-black accent-black"
              />
              <span className="text-xs">{platform.name}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  );
}
