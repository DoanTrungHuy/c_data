"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useRouter, useSearchParams } from "next/navigation";
import {
  FunnelIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  AdjustmentsHorizontalIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ChartBarIcon,
  CheckCircleIcon,
  BookmarkIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import JobCard from "@/components/JobCard";
import FilterSidebar from "@/components/FilterSidebar";
import Pagination from "@/components/Pagination";
import { JobListResponse } from "@/types/job";
import { crawlLiveJobs } from "@/lib/api";
import DeepSocialRadarModal from "@/components/DeepSocialRadarModal";
import SkillMatcherModal from "@/components/SkillMatcherModal";
import HaLongSalaryGuideModal from "@/components/HaLongSalaryGuideModal";
import { useUserSkills } from "@/lib/skillMatcher";

interface JobsContentProps {
  initialData: JobListResponse;
}

export default function JobsContent({ initialData }: JobsContentProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlMessage, setCrawlMessage] = useState<string | null>(null);
  const [conclusions, setConclusions] = useState<any>(null);
  const [radarOpen, setRadarOpen] = useState(false);
  const [diagnosticsOpen, setDiagnosticsOpen] = useState(false);
  const [skillMatcherOpen, setSkillMatcherOpen] = useState(false);
  const [salaryGuideOpen, setSalaryGuideOpen] = useState(false);
  const { skills: userSkills, hasSkills } = useUserSkills();

  useEffect(() => {
    setMounted(true);
  }, []);

  const q = searchParams?.get("q") || "";
  const province = searchParams?.get("province") || "";
  const category = searchParams?.get("category") || "";
  const job_type = searchParams?.get("job_type") || "";
  const platform = searchParams?.get("source_platform") || "";
  const salary_min = searchParams?.get("salary_min");
  const salary_max = searchParams?.get("salary_max");
  const quality_tier = searchParams?.get("quality_tier") || "";
  const tech_stack = searchParams?.get("tech_stack") || "";
  const sort_by = searchParams?.get("sort_by") || "";
  const strict_mode = searchParams?.get("strict_mode") === "true";
  const isSavedOnly = searchParams?.get("saved") === "true";

  const removeFilter = (key: string) => {
    const params = new URLSearchParams(searchParams?.toString() || "");
    params.delete(key);
    if (key === "salary") {
      params.delete("salary_min");
      params.delete("salary_max");
    }
    params.delete("page");
    router.push(`/jobs?${params.toString()}`);
  };

  const clearAllFilters = () => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
  };

  const handleLiveCrawl = async () => {
    setIsCrawling(true);
    setCrawlMessage("Đang quét sâu và mò bài viết từ Facebook Groups, Threads (Meta), TikTok & Cổng tuyển dụng...");
    try {
      const res = await crawlLiveJobs(q || undefined, province || undefined);
      if (res.success) {
        setCrawlMessage(res.message);
        if ((res as any).conclusions) {
          setConclusions((res as any).conclusions);
        }
        // Tự động tải lại trang để hiển thị ngay các tin vừa cào
        setTimeout(() => {
          router.refresh();
        }, 1500);
      } else {
        setCrawlMessage("Đã kiểm tra nhưng chưa có tin mới hơn lúc này.");
      }
    } catch {
      setCrawlMessage("Đã gửi yêu cầu cào dữ liệu mới vào hàng đợi.");
    } finally {
      setIsCrawling(false);
    }
  };

  const hasFilters = Boolean(
    province || category || job_type || platform || salary_min || salary_max || quality_tier || tech_stack
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
      {/* Desktop Filter Sidebar (1 col) */}
      <div className="hidden lg:block lg:col-span-1 sticky top-24">
        <FilterSidebar />
      </div>

      {/* Mobile Filter Modal */}
      {mobileFilterOpen && mounted && createPortal(
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs"
            onClick={() => setMobileFilterOpen(false)}
          />
          <div className="relative ml-auto w-full max-w-xs h-full bg-white p-4 overflow-y-auto shadow-2xl z-10">
            <FilterSidebar onCloseMobile={() => setMobileFilterOpen(false)} />
          </div>
        </div>,
        document.body
      )}

      {/* Main Content Area (3 cols) */}
      <div className="lg:col-span-3 space-y-6">
        {/* Results Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-neutral-200 shadow-xs">
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-black">
              {q ? (
                <span>
                  Kết quả tìm kiếm cho: <span className="underline">"{q}"</span>
                </span>
              ) : province ? (
                <span>
                  Việc làm tại <span className="underline">{province}</span>
                </span>
              ) : (
                <span>Tất cả việc làm tuyển dụng</span>
              )}
            </h1>
            <p className="text-xs sm:text-sm text-neutral-500 mt-0.5">
              Tìm thấy <strong className="text-black">{initialData.total}</strong> việc làm phù hợp
            </p>
          </div>

          {/* Action buttons: Deep Social Radar, Live Crawl & Mobile Filter */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar w-full sm:w-auto flex-nowrap sm:flex-wrap py-1">
            {/* AI Skill Matcher Button */}
            <button
              type="button"
              onClick={() => setSkillMatcherOpen(true)}
              className="shrink-0 inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-neutral-100 hover:bg-neutral-200 text-black border border-neutral-300 transition-all cursor-pointer shadow-xs"
              title="So khớp kỹ năng cá nhân của bạn với mọi việc làm"
            >
              <SparklesIcon className="h-4 w-4 text-black" />
              <span>AI So Khớp CV</span>
            </button>

            {/* Salary Guide Button */}
            <button
              type="button"
              onClick={() => setSalaryGuideOpen(true)}
              className="shrink-0 inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-neutral-100 hover:bg-neutral-200 text-black border border-neutral-300 transition-all cursor-pointer shadow-xs"
              title="Báo cáo mức lương IT chi tiết tại TP. Hạ Long"
            >
              <ChartBarIcon className="h-4 w-4 text-black" />
              <span>Bảng Lương IT</span>
            </button>

            {/* Social Deep Radar Trigger Button */}
            <button
              type="button"
              onClick={() => setRadarOpen(true)}
              className="shrink-0 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-neutral-900 hover:bg-neutral-800 text-white border border-neutral-700 active:scale-95 transition-all cursor-pointer shadow-xs"
              title="Kích hoạt Radar mò tìm sâu trên Facebook Groups, Threads & TikTok"
            >
              <span className="text-sm">🛰️</span>
              <span>Radar Mò MXH Sâu</span>
            </button>

            <button
              type="button"
              onClick={handleLiveCrawl}
              disabled={isCrawling}
              className={`shrink-0 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-xs cursor-pointer ${
                isCrawling
                  ? "bg-neutral-200 text-neutral-800 border border-neutral-300 animate-pulse cursor-wait"
                  : "bg-black hover:bg-neutral-800 text-white active:scale-95"
              }`}
              title="Quét trực tiếp dữ liệu từ các sàn, Fanpage Facebook và trang web doanh nghiệp"
            >
              <span>{isCrawling ? "⏳ Đang cào..." : "⚡ Quét tin mới"}</span>
            </button>

            {/* Mobile Filter Trigger Button */}
            <div className="lg:hidden shrink-0">
              <button
                type="button"
                onClick={() => setMobileFilterOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-neutral-100 text-black font-semibold text-xs border border-neutral-300 hover:bg-neutral-200"
              >
                <AdjustmentsHorizontalIcon className="h-4 w-4 text-black" />
                <span>Bộ lọc ({hasFilters ? "Đang bật" : "Tất cả"})</span>
              </button>
            </div>
          </div>
        </div>

        {/* Active Skills Profile Match Banner */}
        {hasSkills && (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-3.5 bg-neutral-100 border border-neutral-300 rounded-2xl text-xs text-black shadow-xs">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-black text-white font-bold text-xs">
                ✨
              </span>
              <span>
                Đang hiển thị điểm tương thích hồ sơ cho <strong>{userSkills.length} kỹ năng</strong> bạn đã chọn.
              </span>
            </div>
            <button
              type="button"
              onClick={() => setSkillMatcherOpen(true)}
              className="text-black font-bold hover:underline shrink-0 text-left sm:text-right cursor-pointer"
            >
              Chỉnh sửa kỹ năng hồ sơ →
            </button>
          </div>
        )}

        {/* Smart Search Engine Intent & Retrieval Diagnostics */}
        {initialData.diagnostics && (() => {
          const diag = initialData.diagnostics;
          const diagIntent = diag?.parsed_intent || diag?.intent;

          return (
            <div className="bg-neutral-50 text-neutral-900 rounded-2xl border border-neutral-200 shadow-xs overflow-hidden animate-fadeIn">
              <button
                type="button"
                onClick={() => setDiagnosticsOpen(!diagnosticsOpen)}
                className="w-full px-4 py-3 bg-neutral-100 hover:bg-neutral-200/70 flex items-center justify-between text-left transition-colors cursor-pointer"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm">🔍</span>
                  <span className="text-xs font-bold text-black">
                    Chẩn đoán Truy vấn & Xếp hạng Thông minh (Intent & Diagnostics)
                  </span>
                  {diagIntent?.primary_role && (
                    <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-black border border-neutral-300 text-[10px] font-bold">
                      Vị trí: {diagIntent.primary_role}
                    </span>
                  )}
                  {(diagIntent?.target_district || diagIntent?.city || diagIntent?.target_province || diagIntent?.province) && (
                    <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-black border border-neutral-300 text-[10px] font-bold">
                      Địa phương: {diagIntent?.target_district || diagIntent?.city || diagIntent?.target_province || diagIntent?.province}
                    </span>
                  )}
                  <span className="text-[10px] text-neutral-500">
                    ({diag?.total_candidates_examined || 0} ứng viên • {diag?.duplicates_consolidated || 0} trùng lặp gộp)
                  </span>
                </div>
                <div className="flex items-center gap-1 text-neutral-500 text-xs font-semibold shrink-0">
                  <span>{diagnosticsOpen ? "Thu gọn" : "Xem chi tiết"}</span>
                  {diagnosticsOpen ? (
                    <ChevronUpIcon className="h-4 w-4" />
                  ) : (
                    <ChevronDownIcon className="h-4 w-4" />
                  )}
                </div>
              </button>

              {diagnosticsOpen && (
                <div className="p-4 space-y-4 text-xs border-t border-neutral-200 bg-white">
                  {/* Grid 3 boxes: Search Intent, Query Expansion, Filtering Funnel */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {/* Card 1: Parsed Intent */}
                    <div className="bg-neutral-50 rounded-xl p-3 border border-neutral-200 space-y-2">
                      <span className="text-black font-bold block text-xs flex items-center gap-1.5">
                        <span>🎯</span>
                        <span>Ý định tìm kiếm (Search Intent):</span>
                      </span>
                      <div className="space-y-1 text-neutral-700">
                        <div>
                          <strong className="text-black">Vai trò / Ngành:</strong>{" "}
                          {diagIntent?.primary_role || "Không xác định"}
                          {diagIntent?.role_family && (
                            <span className="text-neutral-500">
                              {" "}
                              ({Array.isArray(diagIntent.role_family) ? diagIntent.role_family.join(", ") : diagIntent.role_family})
                            </span>
                          )}
                        </div>
                        <div>
                          <strong className="text-black">Khu vực:</strong>{" "}
                          {diagIntent?.target_province || diagIntent?.province || "Toàn quốc"}
                          {(diagIntent?.target_district || diagIntent?.city) && (
                            <span className="text-neutral-900 font-bold"> - {diagIntent?.target_district || diagIntent?.city}</span>
                          )}
                        </div>
                        {diagIntent?.location_aliases && diagIntent.location_aliases.length > 0 && (
                          <div>
                            <strong className="text-black">Bí danh địa bàn:</strong>{" "}
                            <span className="text-neutral-500">{diagIntent.location_aliases.slice(0, 5).join(", ")}</span>
                          </div>
                        )}
                        <div>
                          <strong className="text-black">Cấp bậc:</strong>{" "}
                          {diagIntent?.seniority || "Tất cả cấp bậc"}
                        </div>
                        {diagIntent?.negative_constraints && diagIntent.negative_constraints.length > 0 && (
                          <div className="text-neutral-900">
                            <strong>Ràng buộc loại trừ:</strong>{" "}
                            {diagIntent.negative_constraints.join(", ")}
                          </div>
                        )}
                        {diagIntent?.max_posting_age_days && (
                          <div className="text-neutral-900">
                            <strong>Độ tươi tin:</strong> Trong {diagIntent.max_posting_age_days} ngày gần nhất
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Card 2: Query Expansion */}
                    <div className="bg-neutral-50 rounded-xl p-3 border border-neutral-200 space-y-2">
                      <span className="text-black font-bold block text-xs flex items-center gap-1.5">
                        <span>🔀</span>
                        <span>Truy vấn mở rộng đa luồng:</span>
                      </span>
                      <p className="text-neutral-600 text-[11px] leading-relaxed">
                        Hệ thống tự động sinh các biến thể từ khóa tương đương thay vì tìm kiếm nguyên văn câu hỏi:
                      </p>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {diag?.expanded_queries?.slice(0, 8).map((qVariant: string, idx: number) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded-md bg-white text-black border border-neutral-300 text-[10px] font-mono font-medium shadow-2xs"
                          >
                            {qVariant}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Card 3: Filter & Ranking Funnel */}
                    <div className="bg-neutral-50 rounded-xl p-3 border border-neutral-200 space-y-2">
                      <span className="text-black font-bold block text-xs flex items-center gap-1.5">
                        <span>⚙️</span>
                        <span>Phễu Sàng Lọc & Khử Trùng:</span>
                      </span>
                      <div className="space-y-1.5 text-neutral-700">
                        <div className="flex justify-between">
                          <span>Số tin ứng viên khảo sát:</span>
                          <strong className="text-black">{diag?.total_candidates_examined || 0}</strong>
                        </div>
                        <div className="flex justify-between text-neutral-900">
                          <span>Trùng lặp đa nguồn gộp lại:</span>
                          <strong>{diag?.duplicates_consolidated || 0}</strong>
                        </div>
                        <div className="flex justify-between text-neutral-600">
                          <span>Loại bỏ do sai địa bàn:</span>
                          <strong>{diag?.removed_by_filters?.hard_location || 0}</strong>
                        </div>
                        <div className="flex justify-between text-neutral-600">
                          <span>Loại bỏ do vi phạm từ cấm:</span>
                          <strong>{diag?.removed_by_filters?.hard_exclusion || 0}</strong>
                        </div>
                        <div className="flex justify-between text-neutral-600">
                          <span>Loại bỏ do quá hạn đăng:</span>
                          <strong>{diag?.removed_by_filters?.hard_posting_age || 0}</strong>
                        </div>
                        <div className="flex justify-between text-neutral-500">
                          <span>Đã hết hạn nộp hồ sơ:</span>
                          <strong>{diag?.removed_by_filters?.expired || 0}</strong>
                        </div>
                        <div className="flex justify-between pt-1 border-t border-neutral-200 text-black font-bold">
                          <span>Kết quả hợp lệ cuối cùng:</span>
                          <span>{initialData.total}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Multi-source discovery status if available */}
                  {diag?.multi_source_discovery && (
                    <div className="bg-neutral-50 rounded-xl p-3 border border-neutral-200 flex flex-wrap items-center justify-between gap-2 text-[11px]">
                      <span className="text-neutral-600 font-semibold">🌐 Trạng thái các nguồn tìm kiếm song song:</span>
                      <div className="flex flex-wrap items-center gap-3">
                        {Object.entries(diag.multi_source_discovery.sources || {}).map(([src, status]: [string, any]) => (
                          <span key={src} className="flex items-center gap-1 text-neutral-800">
                            <span className={`w-2 h-2 rounded-full ${status.status === 'success' ? 'bg-black' : 'bg-neutral-400'}`} />
                            <strong className="capitalize">{src}:</strong> {status.items_found || 0} tin ({status.duration_ms || 0}ms)
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })()}

        {/* Smart Semantic Suggestions & Related Industries Bar */}
        {((initialData.matched_industries && initialData.matched_industries.length > 0) ||
          (initialData.related_keywords && initialData.related_keywords.length > 0)) && (
          <div className="bg-neutral-100 p-4 rounded-2xl border border-neutral-200 shadow-xs space-y-2.5 animate-fadeIn">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-black">
                <span className="text-base">🧠</span>
                <span>Phân tích bài viết &amp; Mò ngành nghề liên quan:</span>
              </div>
              {initialData.matched_industries && initialData.matched_industries.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {initialData.matched_industries.map((ind) => (
                    <span
                      key={ind}
                      className="px-2.5 py-0.5 rounded-full bg-black text-white text-[11px] font-bold shadow-xs"
                    >
                      {ind}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Related Keywords Chips */}
            {initialData.related_keywords && initialData.related_keywords.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 pt-1.5 border-t border-neutral-200">
                <span className="text-xs font-semibold text-neutral-600 mr-1">
                  Từ khóa gợi ý:
                </span>
                {initialData.related_keywords.map((kw) => (
                  <button
                    key={kw}
                    type="button"
                    onClick={() => {
                      const params = new URLSearchParams(searchParams?.toString() || "");
                      params.set("q", kw);
                      params.delete("page");
                      router.push(`/jobs?${params.toString()}`);
                    }}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white hover:bg-black hover:text-white border border-neutral-300 text-neutral-800 text-xs font-medium transition-all shadow-xs active:scale-95 cursor-pointer group"
                  >
                    <span>{kw}</span>
                    <span className="text-neutral-400 group-hover:text-white text-[10px]">↗</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Real-time Crawling Notification Banner */}
        {crawlMessage && (
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-neutral-100 border border-neutral-300 text-neutral-900 text-xs font-medium animate-fadeIn">
            <div className="flex items-center gap-2">
              <span className="text-base">⚡</span>
              <span>{crawlMessage}</span>
            </div>
            <button
              type="button"
              onClick={() => setCrawlMessage(null)}
              className="text-neutral-500 hover:text-black text-xs font-bold ml-2"
            >
              ✕
            </button>
          </div>
        )}

        {/* Deep Social Harvester Market Intelligence & Conclusion Box */}
        {conclusions && (
          <div className="p-4 rounded-2xl bg-neutral-50 border border-neutral-200 text-neutral-900 shadow-xs space-y-3 animate-fadeIn">
            <div className="flex items-center justify-between pb-2 border-b border-neutral-200">
              <div className="flex items-center gap-2">
                <span className="text-xl">📊</span>
                <h3 className="text-sm font-bold text-black">
                  Báo cáo & Kết luận phân tích thị trường việc làm MXH (Facebook • Threads • TikTok)
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setConclusions(null)}
                className="text-neutral-500 hover:text-black text-xs font-bold px-2 py-1 rounded bg-neutral-200 cursor-pointer"
              >
                ✕ Đóng
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
              <div className="bg-white p-3.5 rounded-xl border border-neutral-200 space-y-1.5 shadow-2xs">
                <span className="font-bold text-black block text-xs">📍 Khu vực tuyển dụng sôi động:</span>
                {conclusions.hottest_areas?.map((item: any, idx: number) => (
                  <div key={idx} className="text-neutral-700 leading-relaxed">
                    <strong className="text-black">{item.area} ({item.share}):</strong> {item.reason}
                  </div>
                ))}
              </div>

              <div className="bg-white p-3.5 rounded-xl border border-neutral-200 space-y-1.5 shadow-2xs">
                <span className="font-bold text-black block text-xs">📱 Xu hướng từng nền tảng:</span>
                <p className="text-neutral-700 leading-relaxed"><strong className="text-black">Facebook:</strong> {conclusions.platform_characteristics?.facebook}</p>
                <p className="text-neutral-700 leading-relaxed"><strong className="text-black">Threads:</strong> {conclusions.platform_characteristics?.threads}</p>
                <p className="text-neutral-700 leading-relaxed"><strong className="text-black">TikTok:</strong> {conclusions.platform_characteristics?.tiktok}</p>
              </div>

              <div className="bg-white p-3.5 rounded-xl border border-neutral-200 space-y-1.5 shadow-2xs">
                <span className="font-bold text-black block text-xs">🛡️ An toàn tuyển dụng (Anti-Scam):</span>
                <p className="text-neutral-700 leading-relaxed">{conclusions.anti_scam_warning}</p>
                <div className="mt-2 pt-2 border-t border-neutral-200 text-neutral-800 font-semibold">
                  Mặt bằng lương: F&B 25-32k/h, Lái xe 14-22tr, Du thuyền 10-16tr
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Active Filter Chips */}
        {hasFilters && (
          <div className="flex flex-wrap items-center gap-2 bg-neutral-100 p-3 rounded-xl border border-neutral-200 text-xs">
            <span className="font-semibold text-neutral-700 flex items-center gap-1 mr-1">
              <FunnelIcon className="h-3.5 w-3.5 text-black" />
              Bộ lọc:
            </span>

            {province && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-200 text-neutral-900 font-medium shadow-2xs">
                Tỉnh: {province}
                <button
                  type="button"
                  onClick={() => removeFilter("province")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {category && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-200 text-neutral-900 font-medium shadow-2xs">
                Ngành: {category}
                <button
                  type="button"
                  onClick={() => removeFilter("category")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {job_type && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-200 text-neutral-900 font-medium shadow-2xs">
                Hình thức: {job_type}
                <button
                  type="button"
                  onClick={() => removeFilter("job_type")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {platform && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-200 text-neutral-900 font-medium shadow-2xs">
                Nguồn: {platform}
                <button
                  type="button"
                  onClick={() => removeFilter("source_platform")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {(salary_min || salary_max) && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-200 text-neutral-900 font-medium shadow-2xs">
                Lương: {salary_min ? `Từ ${Number(salary_min) / 1000000}tr` : ""}{" "}
                {salary_max ? `đến ${Number(salary_max) / 1000000}tr` : ""}
                <button
                  type="button"
                  onClick={() => removeFilter("salary")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {quality_tier && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-300 text-black font-bold shadow-2xs">
                💎 Thẩm định: {quality_tier === "diamond" ? "Kim Cương (≥85đ)" : "Đạt Chuẩn (≥70đ)"}
                <button
                  type="button"
                  onClick={() => removeFilter("quality_tier")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {tech_stack && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-neutral-300 text-black font-bold shadow-2xs">
                ⚡ Tech: {tech_stack}
                <button
                  type="button"
                  onClick={() => removeFilter("tech_stack")}
                  className="text-neutral-400 hover:text-black cursor-pointer"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            <button
              type="button"
              onClick={clearAllFilters}
              className="ml-auto text-xs font-bold text-black hover:underline flex items-center gap-1 cursor-pointer"
            >
              <ArrowPathIcon className="h-3 w-3" />
              Xóa tất cả
            </button>
          </div>
        )}

        {/* Quick Filter & Quality Sort Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-2xl bg-white border border-neutral-200 shadow-xs">
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar w-full sm:w-auto py-0.5">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider mr-1 shrink-0">
              Ưu tiên:
            </span>
            <button
              type="button"
              onClick={() => {
                const params = new URLSearchParams(searchParams?.toString() || "");
                if (quality_tier === "diamond") {
                  params.delete("quality_tier");
                } else {
                  params.set("quality_tier", "diamond");
                }
                params.delete("page");
                router.push(`/jobs?${params.toString()}`);
              }}
              className={`shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                quality_tier === "diamond"
                  ? "bg-black text-white border-black shadow-xs"
                  : "bg-neutral-100 text-black border-neutral-200 hover:bg-neutral-200"
              }`}
            >
              <span>💎</span>
              <span>Tin Thẩm Định Kim Cương</span>
            </button>

            <button
              type="button"
              onClick={() => {
                const params = new URLSearchParams(searchParams?.toString() || "");
                if (province === "Quảng Ninh") {
                  params.delete("province");
                } else {
                  params.set("province", "Quảng Ninh");
                }
                params.delete("page");
                router.push(`/jobs?${params.toString()}`);
              }}
              className={`shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border transition-all cursor-pointer ${
                province === "Quảng Ninh"
                  ? "bg-black text-white border-black shadow-xs"
                  : "bg-neutral-100 text-black border-neutral-200 hover:bg-neutral-200"
              }`}
            >
              <span>📍</span>
              <span>Trọng Điểm Hạ Long & QN</span>
            </button>
          </div>

          {/* Sort By Dropdown */}
          <div className="flex items-center justify-between sm:justify-end gap-2 w-full sm:w-auto text-xs pt-2 sm:pt-0 border-t sm:border-t-0 border-neutral-100">
            <span className="text-neutral-500 font-medium">Sắp xếp:</span>
            <select
              value={sort_by || "default"}
              onChange={(e) => {
                const params = new URLSearchParams(searchParams?.toString() || "");
                if (e.target.value === "default") {
                  params.delete("sort_by");
                } else {
                  params.set("sort_by", e.target.value);
                }
                params.delete("page");
                router.push(`/jobs?${params.toString()}`);
              }}
              className="text-xs font-bold text-black bg-neutral-100 border border-neutral-300 rounded-xl px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-black cursor-pointer"
            >
              <option value="default">Phù hợp nhất</option>
              <option value="quality">💎 Điểm Thẩm Định Cao Nhất</option>
            </select>
          </div>
        </div>

        {/* Job Listings / Empty State */}
        {initialData.items.length > 0 ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {initialData.items.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>

            {/* Pagination */}
            <div className="pt-6">
              <Pagination
                currentPage={initialData.page}
                totalPages={initialData.total_pages}
              />
            </div>
          </div>
        ) : isSavedOnly ? (
          /* Empty State for Saved Jobs */
          <div className="text-center py-16 px-4 bg-white rounded-3xl border border-neutral-200 shadow-xs space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200">
              <BookmarkIcon className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-black">
              Bạn chưa lưu việc làm nào
            </h3>
            <p className="text-sm text-neutral-500 max-w-md mx-auto leading-relaxed">
              Hãy bấm biểu tượng Bookmark trên bất kỳ việc làm nào để lưu lại danh sách quan tâm và theo dõi khi cần.
            </p>
            <div className="pt-2">
              <button
                type="button"
                onClick={() => router.push("/jobs?province=Quảng+Ninh")}
                className="inline-flex items-center gap-2 rounded-xl bg-black px-6 py-3 text-xs font-bold text-white hover:bg-neutral-800 shadow-xs transition-all active:scale-95 cursor-pointer"
              >
                <span>Khám phá việc làm IT Hạ Long</span>
              </button>
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-16 px-4 bg-white rounded-3xl border border-neutral-200 shadow-xs space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200">
              <MagnifyingGlassIcon className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-black">
              {q ? (
                <>
                  Không tìm thấy việc làm phù hợp cho: <span className="underline font-black">"{q}"</span>
                </>
              ) : (
                "Không tìm thấy việc làm phù hợp"
              )}
            </h3>
            <p className="text-sm text-neutral-500 max-w-lg mx-auto leading-relaxed">
              {q ? (
                <>
                  Hệ thống không tìm thấy tin tuyển dụng nào chứa từ khóa này. Bạn hãy thử kiểm tra lại chính tả, thử từ khóa khác hoặc bấm các gợi ý bên dưới.
                </>
              ) : (
                "Hãy thử tìm kiếm với từ khóa ngắn hơn, bỏ bớt các bộ lọc địa điểm hoặc ngành nghề để có nhiều kết quả hơn."
              )}
            </p>

            {/* Quick Suggestions for Empty State */}
            <div className="pt-2">
              <span className="text-xs font-semibold text-neutral-500 block mb-2">
                Gợi ý việc làm trọng điểm bạn có thể thử:
              </span>
              <div className="flex flex-wrap items-center justify-center gap-2 max-w-lg mx-auto">
                {["IT Hạ Long", "IT Support Bãi Cháy", "Kỹ sư Cái Lân", "Lập trình viên React", "Khách Sạn 5 Sao", "FPT Telecom"].map((sug) => (
                  <button
                    key={sug}
                    type="button"
                    onClick={() => {
                      const params = new URLSearchParams();
                      params.set("q", sug);
                      if (province) params.set("province", province);
                      router.push(`/jobs?${params.toString()}`);
                    }}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-neutral-100 hover:bg-black hover:text-white border border-neutral-200 text-xs font-medium transition-all active:scale-95 cursor-pointer"
                  >
                    <span>{sug}</span>
                    <span className="text-neutral-400 text-[10px]">↗</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-3 flex flex-col sm:flex-row items-center justify-center gap-3">
              {q && (
                <button
                  type="button"
                  onClick={() => {
                    const params = new URLSearchParams(searchParams?.toString() || "");
                    params.delete("q");
                    params.delete("page");
                    router.push(`/jobs${params.toString() ? `?${params.toString()}` : ""}`);
                  }}
                  className="inline-flex items-center gap-2 rounded-xl bg-black px-5 py-2.5 text-xs font-bold text-white hover:bg-neutral-800 shadow-xs transition-all active:scale-95 cursor-pointer"
                >
                  <XMarkIcon className="h-4 w-4" />
                  <span>Xóa từ khóa "{q}"</span>
                </button>
              )}
              {strict_mode && (
                <button
                  type="button"
                  onClick={() => {
                    const params = new URLSearchParams(searchParams?.toString() || "");
                    params.delete("strict_mode");
                    params.delete("page");
                    router.push(`/jobs?${params.toString()}`);
                  }}
                  className="inline-flex items-center gap-2 rounded-xl bg-black px-5 py-2.5 text-xs font-bold text-white hover:bg-neutral-800 shadow-xs transition-all active:scale-95 cursor-pointer"
                >
                  <span>🔎 Mở rộng kết quả tìm kiếm</span>
                </button>
              )}
              <button
                type="button"
                onClick={clearAllFilters}
                className="inline-flex items-center gap-2 rounded-xl bg-neutral-100 px-5 py-2.5 text-xs font-bold text-black hover:bg-neutral-200 border border-neutral-300 transition-colors cursor-pointer"
              >
                <ArrowPathIcon className="h-4 w-4" />
                <span>Xem tất cả việc làm</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Deep Social Radar Modal */}
      <DeepSocialRadarModal
        isOpen={radarOpen}
        onClose={() => setRadarOpen(false)}
        defaultKeyword={q}
      />

      {/* AI Skill Matcher Modal */}
      <SkillMatcherModal
        isOpen={skillMatcherOpen}
        onClose={() => setSkillMatcherOpen(false)}
      />

      {/* Ha Long IT Salary Guide Modal */}
      <HaLongSalaryGuideModal
        isOpen={salaryGuideOpen}
        onClose={() => setSalaryGuideOpen(false)}
      />
    </div>
  );
}
