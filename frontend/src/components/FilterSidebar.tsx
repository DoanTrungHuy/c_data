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
  const selectedExperience = searchParams?.get("experience_level") || "";
  const selectedRemote = searchParams?.get("remote") === "true";
  const selectedEnterprise = searchParams?.get("enterprise_only") === "true";
  const selectedVerified = searchParams?.get("verified_only") === "true";

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
      selectedTech ||
      selectedExperience ||
      selectedRemote ||
      selectedEnterprise ||
      selectedVerified
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

      {/* 1. Location & Priority */}
      <div className="space-y-3 pb-5 border-b border-neutral-100">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-black">
            Địa điểm (Tỉnh / Thành phố)
          </label>
          {selectedProvince && (
            <button
              onClick={() => updateParam("province", "")}
              className="text-[10px] text-neutral-500 hover:text-black hover:underline font-semibold cursor-pointer"
            >
              Đặt lại
            </button>
          )}
        </div>
        <div className="relative mb-2">
          <MagnifyingGlassIcon className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            placeholder="Tìm nhanh tỉnh thành..."
            value={provinceSearch}
            onChange={(e) => setProvinceSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-neutral-200 focus:outline-none focus:ring-1 focus:ring-black bg-neutral-50"
          />
        </div>
        <div className="max-h-36 overflow-y-auto pr-1 space-y-1 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="province"
              value=""
              checked={selectedProvince === ""}
              onChange={() => updateParam("province", "")}
              className="accent-black"
            />
            <span className="font-medium">Tất cả địa điểm</span>
          </label>
          {filteredProvinces.map((prov) => (
            <label
              key={prov.code}
              className="flex items-center justify-between cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800"
            >
              <div className="flex items-center gap-2">
                <input
                  type="radio"
                  name="province"
                  value={prov.name}
                  checked={selectedProvince === prov.name}
                  onChange={() => updateParam("province", prov.name)}
                  className="accent-black"
                />
                <span>{prov.name}</span>
              </div>
              {prov.popular && (
                <span className="text-[10px] font-bold text-black bg-neutral-200 px-1.5 py-0.2 rounded">
                  Hot
                </span>
              )}
            </label>
          ))}
        </div>

        {/* Priority Checkboxes */}
        <div className="space-y-1.5 pt-2 border-t border-neutral-100 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-900 font-semibold">
            <input
              type="checkbox"
              checked={selectedEnterprise}
              onChange={(e) => updateParam("enterprise_only", e.target.checked ? "true" : "")}
              className="accent-black rounded"
            />
            <span>🌟 Trọng điểm Hạ Long</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800 font-medium">
            <input
              type="checkbox"
              checked={selectedVerified}
              onChange={(e) => updateParam("verified_only", e.target.checked ? "true" : "")}
              className="accent-black rounded"
            />
            <span>🛡️ Tin đã thẩm định đối soát</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800 font-medium">
            <input
              type="checkbox"
              checked={selectedRemote}
              onChange={(e) => updateParam("remote", e.target.checked ? "true" : "")}
              className="accent-black rounded"
            />
            <span>🏠 Làm việc từ xa (Remote)</span>
          </label>
        </div>
      </div>

      {/* 2. Industry & Tech Stack */}
      <div className="space-y-3 pb-5 border-b border-neutral-100">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-black">
            Ngành nghề chuyên môn
          </label>
          {selectedCategory && (
            <button
              onClick={() => updateParam("category", "")}
              className="text-[10px] text-neutral-500 hover:text-black hover:underline font-semibold cursor-pointer"
            >
              Đặt lại
            </button>
          )}
        </div>
        <div className="space-y-1 text-xs max-h-40 overflow-y-auto pr-1">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="category"
              value=""
              checked={selectedCategory === ""}
              onChange={() => updateParam("category", "")}
              className="accent-black"
            />
            <span className="font-medium">Tất cả ngành nghề</span>
          </label>
          {POPULAR_CATEGORIES.map((cat) => (
            <label
              key={cat.slug}
              className="flex items-center justify-between cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800"
            >
              <div className="flex items-center gap-2 truncate">
                <input
                  type="radio"
                  name="category"
                  value={cat.name}
                  checked={selectedCategory === cat.name}
                  onChange={() => updateParam("category", cat.name)}
                  className="accent-black"
                />
                <span className="truncate">{cat.name}</span>
              </div>
            </label>
          ))}
        </div>

        {/* Tech Stack Cloud */}
        <div className="pt-2 border-t border-neutral-100">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-bold text-neutral-600 uppercase tracking-wider">
              Kỹ năng / Tech Stack
            </span>
            {selectedTech && (
              <button
                onClick={() => updateParam("tech_stack", "")}
                className="text-[10px] text-neutral-500 hover:text-black hover:underline font-semibold cursor-pointer"
              >
                Bỏ chọn
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-1">
            {[
              "Cisco", "Fortinet", "Windows Server", "Linux", "Opera PMS",
              "Micros POS", "Python", "React.js", "SQL Server", "ERP SAP"
            ].map((tech) => (
              <button
                key={tech}
                type="button"
                onClick={() => updateParam("tech_stack", selectedTech === tech ? "" : tech)}
                className={`text-[10px] font-bold px-2 py-1 rounded-md border transition-colors cursor-pointer ${
                  selectedTech === tech
                    ? "bg-black text-white border-black"
                    : "bg-neutral-100 text-neutral-800 border-neutral-200 hover:bg-neutral-200"
                }`}
              >
                {tech}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 3. Seniority & Experience */}
      <div className="space-y-2 pb-5 border-b border-neutral-100">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-black">
            Cấp bậc &amp; Kinh nghiệm
          </label>
          {selectedExperience && (
            <button
              onClick={() => updateParam("experience_level", "")}
              className="text-[10px] text-neutral-500 hover:text-black hover:underline font-semibold cursor-pointer"
            >
              Đặt lại
            </button>
          )}
        </div>
        <div className="space-y-1 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="experience_level"
              value=""
              checked={selectedExperience === ""}
              onChange={() => updateParam("experience_level", "")}
              className="accent-black"
            />
            <span>Tất cả cấp bậc</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-black font-semibold">
            <input
              type="radio"
              name="experience_level"
              value="fresher"
              checked={selectedExperience === "fresher"}
              onChange={() => updateParam("experience_level", "fresher")}
              className="accent-black"
            />
            <span>🎓 Fresher / Thực tập</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-black font-semibold">
            <input
              type="radio"
              name="experience_level"
              value="junior"
              checked={selectedExperience === "junior"}
              onChange={() => updateParam("experience_level", "junior")}
              className="accent-black"
            />
            <span>💻 Junior (1 - 2 năm)</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="experience_level"
              value="middle"
              checked={selectedExperience === "middle"}
              onChange={() => updateParam("experience_level", "middle")}
              className="accent-black"
            />
            <span>⚡ Middle (2 - 4 năm)</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="experience_level"
              value="senior"
              checked={selectedExperience === "senior"}
              onChange={() => updateParam("experience_level", "senior")}
              className="accent-black"
            />
            <span>👑 Senior / Quản lý</span>
          </label>
        </div>
      </div>

      {/* 4. Salary Range & Job Type */}
      <div className="space-y-3 pb-5 border-b border-neutral-100">
        <label className="text-xs font-bold uppercase tracking-wider text-black block">
          Mức lương &amp; Hình thức
        </label>
        <div className="space-y-1 text-xs">
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
                className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800"
              >
                <input
                  type="radio"
                  name="salary_range"
                  checked={isChecked}
                  onChange={() => handleSalaryChange(range.min, range.max)}
                  className="accent-black"
                />
                <span>{range.label}</span>
              </label>
            );
          })}
        </div>

        <div className="pt-2 border-t border-neutral-100 space-y-1 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="job_type"
              value=""
              checked={selectedJobType === ""}
              onChange={() => updateParam("job_type", "")}
              className="accent-black"
            />
            <span className="font-medium">Tất cả hình thức</span>
          </label>
          {JOB_TYPES.map((jt) => (
            <label
              key={jt.value}
              className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800"
            >
              <input
                type="radio"
                name="job_type"
                value={jt.value}
                checked={selectedJobType === jt.value}
                onChange={() => updateParam("job_type", jt.value)}
                className="accent-black"
              />
              <span>{jt.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 5. Source Platform & Quality Tier */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-black">
            Nguồn tuyển dụng
          </label>
          {selectedPlatform && (
            <button
              onClick={() => updateParam("source_platform", "")}
              className="text-[10px] text-neutral-500 hover:text-black hover:underline font-semibold cursor-pointer"
            >
              Đặt lại
            </button>
          )}
        </div>
        <div className="space-y-1 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800">
            <input
              type="radio"
              name="source_platform"
              value=""
              checked={selectedPlatform === ""}
              onChange={() => updateParam("source_platform", "")}
              className="accent-black"
            />
            <span className="font-medium">Tất cả nguồn</span>
          </label>
          {SOURCE_PLATFORMS.map((platform) => (
            <label
              key={platform.id}
              className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-neutral-800"
            >
              <input
                type="radio"
                name="source_platform"
                value={platform.id}
                checked={selectedPlatform === platform.id}
                onChange={() => updateParam("source_platform", platform.id)}
                className="accent-black"
              />
              <span>{platform.name}</span>
            </label>
          ))}
        </div>

        {/* Quality Tier */}
        <div className="pt-2 border-t border-neutral-100 space-y-1 text-xs">
          <label className="flex items-center gap-2 cursor-pointer p-1 rounded-lg hover:bg-neutral-50 text-black font-semibold">
            <input
              type="radio"
              name="quality_tier"
              value="diamond"
              checked={selectedQualityTier === "diamond"}
              onChange={() => updateParam("quality_tier", selectedQualityTier === "diamond" ? "" : "diamond")}
              className="accent-black"
            />
            <span>💎 Thẩm định Kim Cương (≥ 85đ)</span>
          </label>
        </div>
      </div>
    </aside>
  );
}
