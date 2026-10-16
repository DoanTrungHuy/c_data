"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Job } from "@/types/job";
import { loadAllJobsForClient, searchJobsRealtime } from "@/lib/clientSearch";
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  BriefcaseIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  BoltIcon,
  BuildingOfficeIcon,
  ArrowRightIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [allJobs, setAllJobs] = useState<Job[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load jobs when opened
  useEffect(() => {
    if (isOpen) {
      loadAllJobsForClient().then((jobs) => {
        if (jobs && jobs.length > 0) setAllJobs(jobs);
      });
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    } else {
      setQuery("");
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Global Keyboard shortcut listener (Cmd+K / Ctrl+K / '/')
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          // Open handled by parent or custom event
          window.dispatchEvent(new CustomEvent("open-command-palette"));
        }
      } else if (e.key === "Escape" && isOpen) {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Quick Action Presets
  const quickActions = [
    {
      id: "action-it-halong",
      label: "Việc làm IT & CNTT TP. Hạ Long",
      category: "Khu vực trọng điểm",
      icon: "💻",
      action: () => router.push("/jobs?q=IT&province=Qu%E1%BA%A3ng+Ninh"),
    },
    {
      id: "action-baichay-hotel",
      label: "Cụm Khách sạn & Resort Bãi Cháy",
      category: "Địa bàn",
      icon: "🏖️",
      action: () => router.push("/jobs?q=B%C3%A3i+Ch%C3%A1y"),
    },
    {
      id: "action-cailan-kcn",
      label: "KCN Cái Lân, Cảng Biển & Foxconn",
      category: "Địa bàn",
      icon: "🚢",
      action: () => router.push("/jobs?q=C%C3%A1i+L%C3%A2n"),
    },
    {
      id: "action-diamond",
      label: "Chỉ xem việc Thẩm định Kim Cương (85+ điểm)",
      category: "Chất lượng",
      icon: "💎",
      action: () => router.push("/jobs?quality_tier=diamond"),
    },
    {
      id: "action-high-salary",
      label: "Việc làm mức lương trên 20 triệu VNĐ",
      category: "Thu nhập",
      icon: "💰",
      action: () => router.push("/jobs?salary_min=20000000"),
    },
    {
      id: "action-saved",
      label: "Xem danh sách việc làm đã lưu của bạn",
      category: "Cá nhân",
      icon: "🔖",
      action: () => router.push("/jobs?saved=true"),
    },
  ];

  // Search Results
  const searchResults = useMemo(() => {
    if (!query.trim() || allJobs.length === 0) return [];
    const res = searchJobsRealtime(allJobs, { q: query.trim(), page_size: 6 });
    return res.items;
  }, [query, allJobs]);

  // Combined flat items list for keyboard navigation
  const flatItems = useMemo(() => {
    if (searchResults.length > 0) {
      return searchResults.map((j) => ({
        type: "job" as const,
        id: String(j.id),
        title: j.title,
        subtitle: `${j.company_name} • ${j.location_district || j.location_province || "Quảng Ninh"}`,
        meta: j.salary_text || "Thỏa thuận",
        action: () => router.push(`/jobs/${j.id}`),
      }));
    }
    return quickActions.map((a) => ({
      type: "action" as const,
      id: a.id,
      title: a.label,
      subtitle: a.category,
      meta: a.icon,
      action: a.action,
    }));
  }, [searchResults, quickActions, router]);

  // Handle arrow keys and enter
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % flatItems.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + flatItems.length) % flatItems.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (flatItems[selectedIndex]) {
        flatItems[selectedIndex].action();
        onClose();
      } else if (query.trim()) {
        router.push(`/jobs?q=${encodeURIComponent(query.trim())}`);
        onClose();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-14 sm:pt-20 p-3 sm:p-4 bg-black/60 backdrop-blur-xs animate-fadeIn">
      {/* Click outside to close */}
      <div className="fixed inset-0 -z-10" onClick={onClose} />

      <div className="relative w-full max-w-2xl bg-white rounded-2xl sm:rounded-3xl border border-neutral-200 shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-scaleIn">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 sm:py-4 border-b border-neutral-200 gap-3 bg-white">
          <MagnifyingGlassIcon className="h-5 w-5 text-neutral-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleInputKeyDown}
            placeholder="Tìm theo chức danh, công ty, kỹ năng (ví dụ: IT Bãi Cháy, Kế toán, React...)"
            className="flex-1 bg-transparent text-sm sm:text-base text-black placeholder:text-neutral-400 focus:outline-none font-medium"
          />
          {query ? (
            <button
              type="button"
              onClick={() => {
                setQuery("");
                inputRef.current?.focus();
              }}
              className="p-1 rounded-lg text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          ) : (
            <kbd className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-mono font-bold text-neutral-400 bg-neutral-100 border border-neutral-200 rounded-md">
              ESC
            </kbd>
          )}
        </div>

        {/* Content Area */}
        <div className="overflow-y-auto p-2 sm:p-3 divide-y divide-neutral-100 text-xs">
          {searchResults.length > 0 ? (
            <div className="space-y-1">
              <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-neutral-400">
                Việc làm phù hợp ({searchResults.length} kết quả hàng đầu):
              </div>
              {searchResults.map((job, idx) => {
                const isSelected = selectedIndex === idx;
                return (
                  <button
                    key={job.id}
                    type="button"
                    onClick={() => {
                      router.push(`/jobs/${job.id}`);
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full p-2.5 sm:p-3 rounded-xl flex items-center justify-between gap-3 text-left transition-colors cursor-pointer ${
                      isSelected
                        ? "bg-black text-white"
                        : "hover:bg-neutral-100 text-neutral-900"
                    }`}
                  >
                    <div className="min-w-0 flex-1 space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xs sm:text-sm truncate">
                          {job.title}
                        </span>
                        {job.quality_score && job.quality_score >= 85 && (
                          <span
                            className={`shrink-0 text-[10px] px-1.5 py-0.2 rounded-md font-bold ${
                              isSelected
                                ? "bg-white text-black"
                                : "bg-neutral-200 text-black"
                            }`}
                          >
                            💎 85+
                          </span>
                        )}
                      </div>
                      <p
                        className={`text-[11px] truncate ${
                          isSelected ? "text-neutral-300" : "text-neutral-500"
                        }`}
                      >
                        {job.company_name} • {job.location_district || job.location_province || "Quảng Ninh"}
                      </p>
                    </div>

                    <div className="shrink-0 text-right">
                      <span
                        className={`font-mono font-bold text-[11px] sm:text-xs block ${
                          isSelected ? "text-white" : "text-black"
                        }`}
                      >
                        {job.salary_text || "Thỏa thuận"}
                      </span>
                    </div>
                  </button>
                );
              })}

              <div className="pt-2 px-2 pb-1 text-center">
                <button
                  type="button"
                  onClick={() => {
                    router.push(`/jobs?q=${encodeURIComponent(query.trim())}`);
                    onClose();
                  }}
                  className="w-full py-2 text-xs font-bold text-black hover:bg-neutral-100 rounded-xl transition-colors cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <span>Xem toàn bộ kết quả tìm kiếm cho "{query}"</span>
                  <ArrowRightIcon className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ) : query.trim() ? (
            <div className="py-8 px-4 text-center space-y-2">
              <span className="text-3xl block">🔍</span>
              <p className="font-bold text-sm text-black">
                Không tìm thấy việc làm khớp chính xác với "{query}"
              </p>
              <p className="text-xs text-neutral-500 max-w-sm mx-auto">
                Thử tìm với các từ khóa phổ biến: <em>IT Support, Kế toán, Lễ tân, Novotel, React, Wyndham...</em>
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-neutral-400">
                Truy cập nhanh & Lối tắt nổi bật:
              </div>
              {quickActions.map((action, idx) => {
                const isSelected = selectedIndex === idx;
                return (
                  <button
                    key={action.id}
                    type="button"
                    onClick={() => {
                      action.action();
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full p-2.5 sm:p-3 rounded-xl flex items-center justify-between gap-3 text-left transition-colors cursor-pointer ${
                      isSelected
                        ? "bg-black text-white"
                        : "hover:bg-neutral-100 text-neutral-900"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-base sm:text-lg shrink-0">
                        {action.icon}
                      </span>
                      <div>
                        <span className="font-bold text-xs sm:text-sm block">
                          {action.label}
                        </span>
                        <span
                          className={`text-[10px] uppercase font-bold tracking-wider ${
                            isSelected ? "text-neutral-400" : "text-neutral-400"
                          }`}
                        >
                          {action.category}
                        </span>
                      </div>
                    </div>
                    <ArrowRightIcon
                      className={`h-4 w-4 shrink-0 ${
                        isSelected ? "text-white" : "text-neutral-400"
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer Shortcut Guide */}
        <div className="p-3 bg-neutral-50 border-t border-neutral-200 flex items-center justify-between text-[11px] text-neutral-500 shrink-0">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded-sm bg-white border border-neutral-200 font-mono text-[10px]">↑</kbd>
              <kbd className="px-1.5 py-0.5 rounded-sm bg-white border border-neutral-200 font-mono text-[10px]">↓</kbd>
              <span>Điều hướng</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded-sm bg-white border border-neutral-200 font-mono text-[10px]">↵</kbd>
              <span>Chọn</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded-sm bg-white border border-neutral-200 font-mono text-[10px]">esc</kbd>
              <span>Đóng</span>
            </span>
          </div>

          <span className="hidden sm:inline font-semibold text-neutral-600">
            C_Data Realtime Engine (2ms)
          </span>
        </div>
      </div>
    </div>
  );
}
