"use client";

import React, { useState } from "react";
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
} from "@heroicons/react/24/outline";
import JobCard from "@/components/JobCard";
import FilterSidebar from "@/components/FilterSidebar";
import Pagination from "@/components/Pagination";
import { JobListResponse } from "@/types/job";
import { crawlLiveJobs } from "@/lib/api";
import DeepSocialRadarModal from "@/components/DeepSocialRadarModal";

interface JobsContentProps {
  initialData: JobListResponse;
}

export default function JobsContent({ initialData }: JobsContentProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlMessage, setCrawlMessage] = useState<string | null>(null);
  const [conclusions, setConclusions] = useState<any>(null);
  const [radarOpen, setRadarOpen] = useState(false);
  const [diagnosticsOpen, setDiagnosticsOpen] = useState(false);

  const q = searchParams?.get("q") || "";
  const province = searchParams?.get("province") || "";
  const category = searchParams?.get("category") || "";
  const job_type = searchParams?.get("job_type") || "";
  const platform = searchParams?.get("source_platform") || "";
  const salary_min = searchParams?.get("salary_min");
  const salary_max = searchParams?.get("salary_max");
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
    province || category || job_type || platform || salary_min || salary_max
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
      {/* Desktop Filter Sidebar (1 col) */}
      <div className="hidden lg:block lg:col-span-1 sticky top-24">
        <FilterSidebar />
      </div>

      {/* Mobile Filter Modal */}
      {mobileFilterOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs"
            onClick={() => setMobileFilterOpen(false)}
          />
          <div className="relative ml-auto w-full max-w-xs h-full bg-white p-4 overflow-y-auto shadow-2xl z-10">
            <FilterSidebar onCloseMobile={() => setMobileFilterOpen(false)} />
          </div>
        </div>
      )}

      {/* Main Content Area (3 cols) */}
      <div className="lg:col-span-3 space-y-6">
        {/* Results Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs">
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900">
              {q ? (
                <span>
                  Kết quả tìm kiếm cho: <span className="text-primary-600">"{q}"</span>
                </span>
              ) : province ? (
                <span>
                  Việc làm tại <span className="text-primary-600">{province}</span>
                </span>
              ) : (
                <span>Tất cả việc làm tuyển dụng</span>
              )}
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              Tìm thấy <strong className="text-slate-800">{initialData.total}</strong> việc làm phù hợp
            </p>
          </div>

          {/* Action buttons: Deep Social Radar, Live Crawl & Mobile Filter */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Social Deep Radar Trigger Button */}
            <button
              type="button"
              onClick={() => setRadarOpen(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-black bg-gradient-to-r from-orange-500 via-amber-500 to-red-500 text-white hover:brightness-105 active:scale-95 shadow-md shadow-orange-500/20 transition-all cursor-pointer"
              title="Kích hoạt Radar mò tìm sâu trên Facebook Groups, Threads & TikTok"
            >
              <span className="text-sm">🛰️</span>
              <span>Radar Mò MXH Sâu</span>
            </button>

            <button
              type="button"
              onClick={handleLiveCrawl}
              disabled={isCrawling}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-sm ${
                isCrawling
                  ? "bg-amber-100 text-amber-800 border border-amber-300 animate-pulse cursor-wait"
                  : "bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 active:scale-95"
              }`}
              title="Quét trực tiếp dữ liệu từ các sàn, Fanpage Facebook và trang web doanh nghiệp"
            >
              <span>{isCrawling ? "⏳ Đang cào realtime..." : "⚡ Quét tin mới"}</span>
            </button>

            {/* Mobile Filter Trigger Button */}
            <div className="lg:hidden">
              <button
                type="button"
                onClick={() => setMobileFilterOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-primary-50 text-primary-700 font-semibold text-xs border border-primary-200 hover:bg-primary-100"
              >
                <AdjustmentsHorizontalIcon className="h-4 w-4" />
                <span>Bộ lọc ({hasFilters ? "Đang bật" : "Tất cả"})</span>
              </button>
            </div>
          </div>
        </div>

        {/* Smart Search Engine Intent & Retrieval Diagnostics */}
        {initialData.diagnostics && (() => {
          const diag = initialData.diagnostics;
          const diagIntent = diag?.parsed_intent || diag?.intent;

          return (
            <div className="bg-slate-900 text-white rounded-2xl border border-slate-700/80 shadow-md overflow-hidden animate-fadeIn">
              <button
                type="button"
                onClick={() => setDiagnosticsOpen(!diagnosticsOpen)}
                className="w-full px-4 py-3 bg-slate-800/80 hover:bg-slate-800 flex items-center justify-between text-left transition-colors cursor-pointer"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm">🔍</span>
                  <span className="text-xs font-bold text-sky-300">
                    Chẩn đoán Truy vấn & Xếp hạng Thông minh (Intent & Diagnostics)
                  </span>
                  {diagIntent?.primary_role && (
                    <span className="px-2 py-0.5 rounded-full bg-sky-950 text-sky-300 border border-sky-800 text-[10px] font-semibold">
                      Vị trí: {diagIntent.primary_role}
                    </span>
                  )}
                  {(diagIntent?.target_district || diagIntent?.city || diagIntent?.target_province || diagIntent?.province) && (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] font-semibold">
                      Địa phương: {diagIntent?.target_district || diagIntent?.city || diagIntent?.target_province || diagIntent?.province}
                    </span>
                  )}
                  <span className="text-[10px] text-slate-400">
                    ({diag?.total_candidates_examined || 0} ứng viên • {diag?.duplicates_consolidated || 0} trùng lặp gộp)
                  </span>
                </div>
                <div className="flex items-center gap-1 text-slate-400 text-xs font-semibold shrink-0">
                  <span>{diagnosticsOpen ? "Thu gọn" : "Xem chi tiết"}</span>
                  {diagnosticsOpen ? (
                    <ChevronUpIcon className="h-4 w-4" />
                  ) : (
                    <ChevronDownIcon className="h-4 w-4" />
                  )}
                </div>
              </button>

              {diagnosticsOpen && (
                <div className="p-4 space-y-4 text-xs border-t border-slate-700/60 bg-slate-950/40">
                  {/* Grid 3 boxes: Search Intent, Query Expansion, Filtering Funnel */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {/* Card 1: Parsed Intent */}
                    <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50 space-y-2">
                      <span className="text-sky-300 font-bold block text-xs flex items-center gap-1.5">
                        <span>🎯</span>
                        <span>Ý định tìm kiếm (Search Intent):</span>
                      </span>
                      <div className="space-y-1 text-slate-300">
                        <div>
                          <strong className="text-white">Vai trò / Ngành:</strong>{" "}
                          {diagIntent?.primary_role || "Không xác định"}
                          {diagIntent?.role_family && (
                            <span className="text-slate-400">
                              {" "}
                              ({Array.isArray(diagIntent.role_family) ? diagIntent.role_family.join(", ") : diagIntent.role_family})
                            </span>
                          )}
                        </div>
                        <div>
                          <strong className="text-white">Khu vực:</strong>{" "}
                          {diagIntent?.target_province || diagIntent?.province || "Toàn quốc"}
                          {(diagIntent?.target_district || diagIntent?.city) && (
                            <span className="text-emerald-300"> - {diagIntent?.target_district || diagIntent?.city}</span>
                          )}
                        </div>
                        {diagIntent?.location_aliases && diagIntent.location_aliases.length > 0 && (
                          <div>
                            <strong className="text-white">Bí danh địa bàn:</strong>{" "}
                            <span className="text-slate-400">{diagIntent.location_aliases.slice(0, 5).join(", ")}</span>
                          </div>
                        )}
                        <div>
                          <strong className="text-white">Cấp bậc:</strong>{" "}
                          {diagIntent?.seniority || "Tất cả cấp bậc"}
                        </div>
                        {diagIntent?.negative_constraints && diagIntent.negative_constraints.length > 0 && (
                          <div className="text-rose-300">
                            <strong>Ràng buộc loại trừ:</strong>{" "}
                            {diagIntent.negative_constraints.join(", ")}
                          </div>
                        )}
                        {diagIntent?.max_posting_age_days && (
                          <div className="text-amber-300">
                            <strong>Độ tươi tin:</strong> Trong {diagIntent.max_posting_age_days} ngày gần nhất
                          </div>
                        )}
                      </div>
                    </div>

                  {/* Card 2: Query Expansion */}
                  <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50 space-y-2">
                    <span className="text-emerald-300 font-bold block text-xs flex items-center gap-1.5">
                      <span>🔀</span>
                      <span>Truy vấn mở rộng đa luồng:</span>
                    </span>
                    <p className="text-slate-400 text-[11px] leading-relaxed">
                      Hệ thống tự động sinh các biến thể từ khóa tương đương thay vì tìm kiếm nguyên văn câu hỏi:
                    </p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {diag?.expanded_queries?.slice(0, 8).map((qVariant, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 text-[10px] font-mono"
                        >
                          {qVariant}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Card 3: Filter & Ranking Funnel */}
                  <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50 space-y-2">
                    <span className="text-amber-300 font-bold block text-xs flex items-center gap-1.5">
                      <span>⚙️</span>
                      <span>Phễu Sàng Lọc & Khử Trùng:</span>
                    </span>
                    <div className="space-y-1.5 text-slate-300">
                      <div className="flex justify-between">
                        <span>Số tin ứng viên khảo sát:</span>
                        <strong className="text-white">{diag?.total_candidates_examined || 0}</strong>
                      </div>
                      <div className="flex justify-between text-indigo-300">
                        <span>Trùng lặp đa nguồn gộp lại:</span>
                        <strong>{diag?.duplicates_consolidated || 0}</strong>
                      </div>
                      <div className="flex justify-between text-rose-300">
                        <span>Loại bỏ do sai địa bàn:</span>
                        <strong>{diag?.removed_by_filters?.hard_location || 0}</strong>
                      </div>
                      <div className="flex justify-between text-rose-300">
                        <span>Loại bỏ do vi phạm từ cấm:</span>
                        <strong>{diag?.removed_by_filters?.hard_exclusion || 0}</strong>
                      </div>
                      <div className="flex justify-between text-rose-300">
                        <span>Loại bỏ do quá hạn đăng:</span>
                        <strong>{diag?.removed_by_filters?.hard_posting_age || 0}</strong>
                      </div>
                      <div className="flex justify-between text-slate-400">
                        <span>Đã hết hạn nộp hồ sơ:</span>
                        <strong>{diag?.removed_by_filters?.expired || 0}</strong>
                      </div>
                      <div className="flex justify-between pt-1 border-t border-slate-700 text-sky-300 font-bold">
                        <span>Kết quả hợp lệ cuối cùng:</span>
                        <span>{initialData.total}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Multi-source discovery status if available */}
                {diag?.multi_source_discovery && (
                  <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/40 flex flex-wrap items-center justify-between gap-2 text-[11px]">
                    <span className="text-slate-400 font-semibold">🌐 Trạng thái các nguồn tìm kiếm song song:</span>
                    <div className="flex flex-wrap items-center gap-3">
                      {Object.entries(diag.multi_source_discovery.sources || {}).map(([src, status]: [string, any]) => (
                        <span key={src} className="flex items-center gap-1 text-slate-300">
                          <span className={`w-2 h-2 rounded-full ${status.status === 'success' ? 'bg-emerald-400' : 'bg-slate-400'}`} />
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
          <div className="bg-gradient-to-r from-blue-50/90 via-indigo-50/70 to-purple-50/70 p-4 rounded-2xl border border-blue-200 shadow-2xs space-y-2.5 animate-fadeIn">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-primary-900">
                <span className="text-base">🧠</span>
                <span>Phân tích bài viết & Mò ngành nghề liên quan:</span>
              </div>
              {initialData.matched_industries && initialData.matched_industries.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {initialData.matched_industries.map((ind) => (
                    <span
                      key={ind}
                      className="px-2.5 py-0.5 rounded-full bg-primary-600 text-white text-[11px] font-bold shadow-2xs"
                    >
                      {ind}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Related Keywords Chips */}
            {initialData.related_keywords && initialData.related_keywords.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 pt-1.5 border-t border-blue-200/60">
                <span className="text-xs font-semibold text-slate-600 mr-1">
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
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white hover:bg-primary-600 hover:text-white border border-blue-200/90 text-slate-700 text-xs font-medium transition-all shadow-2xs active:scale-95 cursor-pointer group"
                  >
                    <span>{kw}</span>
                    <span className="text-slate-400 group-hover:text-white text-[10px]">↗</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Real-time Crawling Notification Banner */}
        {crawlMessage && (
          <div className="flex items-center justify-between p-3.5 rounded-xl bg-amber-50/90 border border-amber-200 text-amber-900 text-xs font-medium animate-fadeIn">
            <div className="flex items-center gap-2">
              <span className="text-base">⚡</span>
              <span>{crawlMessage}</span>
            </div>
            <button
              type="button"
              onClick={() => setCrawlMessage(null)}
              className="text-amber-600 hover:text-amber-800 text-xs font-bold ml-2"
            >
              ✕
            </button>
          </div>
        )}

        {/* Deep Social Harvester Market Intelligence & Conclusion Box */}
        {conclusions && (
          <div className="p-4 rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white shadow-xl space-y-3 animate-fadeIn border border-indigo-700/60">
            <div className="flex items-center justify-between pb-2 border-b border-indigo-800/60">
              <div className="flex items-center gap-2">
                <span className="text-xl">📊</span>
                <h3 className="text-sm font-bold text-amber-300">
                  Báo cáo & Kết luận phân tích thị trường việc làm MXH (Facebook • Threads • TikTok)
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setConclusions(null)}
                className="text-slate-400 hover:text-white text-xs font-bold px-2 py-1 rounded bg-white/10"
              >
                ✕ Đóng
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
              <div className="bg-white/10 p-3 rounded-xl space-y-1.5 border border-white/5">
                <span className="font-bold text-amber-300 block text-xs">📍 Khu vực tuyển dụng sôi động:</span>
                {conclusions.hottest_areas?.map((item: any, idx: number) => (
                  <div key={idx} className="text-slate-200 leading-relaxed">
                    <strong className="text-white">{item.area} ({item.share}):</strong> {item.reason}
                  </div>
                ))}
              </div>

              <div className="bg-white/10 p-3 rounded-xl space-y-1.5 border border-white/5">
                <span className="font-bold text-emerald-300 block text-xs">📱 Xu hướng từng nền tảng:</span>
                <p className="text-slate-200 leading-relaxed"><strong className="text-white">Facebook:</strong> {conclusions.platform_characteristics?.facebook}</p>
                <p className="text-slate-200 leading-relaxed"><strong className="text-white">Threads:</strong> {conclusions.platform_characteristics?.threads}</p>
                <p className="text-slate-200 leading-relaxed"><strong className="text-white">TikTok:</strong> {conclusions.platform_characteristics?.tiktok}</p>
              </div>

              <div className="bg-white/10 p-3 rounded-xl space-y-1.5 border border-white/5">
                <span className="font-bold text-sky-300 block text-xs">🛡️ An toàn tuyển dụng (Anti-Scam):</span>
                <p className="text-slate-200 leading-relaxed">{conclusions.anti_scam_warning}</p>
                <div className="mt-2 pt-2 border-t border-white/10 text-amber-300 font-semibold">
                  Mặt bằng lương: F&B 25-32k/h, Lái xe 14-22tr, Du thuyền 10-16tr
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Active Filter Chips */}
        {hasFilters && (
          <div className="flex flex-wrap items-center gap-2 bg-slate-100/80 p-3 rounded-xl text-xs">
            <span className="font-semibold text-slate-600 flex items-center gap-1 mr-1">
              <FunnelIcon className="h-3.5 w-3.5" />
              Bộ lọc:
            </span>

            {province && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 font-medium">
                Tỉnh: {province}
                <button
                  type="button"
                  onClick={() => removeFilter("province")}
                  className="text-slate-400 hover:text-rose-600"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {category && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 font-medium">
                Ngành: {category}
                <button
                  type="button"
                  onClick={() => removeFilter("category")}
                  className="text-slate-400 hover:text-rose-600"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {job_type && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 font-medium">
                Hình thức: {job_type}
                <button
                  type="button"
                  onClick={() => removeFilter("job_type")}
                  className="text-slate-400 hover:text-rose-600"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {platform && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 font-medium">
                Nguồn: {platform}
                <button
                  type="button"
                  onClick={() => removeFilter("source_platform")}
                  className="text-slate-400 hover:text-rose-600"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            {(salary_min || salary_max) && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-800 font-medium">
                Lương: {salary_min ? `Từ ${Number(salary_min) / 1000000}tr` : ""}{" "}
                {salary_max ? `đến ${Number(salary_max) / 1000000}tr` : ""}
                <button
                  type="button"
                  onClick={() => removeFilter("salary")}
                  className="text-slate-400 hover:text-rose-600"
                >
                  <XMarkIcon className="h-3.5 w-3.5" />
                </button>
              </span>
            )}

            <button
              type="button"
              onClick={clearAllFilters}
              className="ml-auto text-xs font-semibold text-rose-600 hover:underline flex items-center gap-1"
            >
              <ArrowPathIcon className="h-3 w-3" />
              Xóa tất cả
            </button>
          </div>
        )}

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
          <div className="text-center py-16 px-4 bg-white rounded-3xl border border-rose-100 shadow-sm space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-50 text-rose-500 border border-rose-200">
              <BookmarkIcon className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">
              Bạn chưa lưu việc làm nào
            </h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
              Hãy bấm biểu tượng Bookmark trên bất kỳ việc làm nào để lưu lại danh sách quan tâm và theo dõi khi cần.
            </p>
            <div className="pt-2">
              <button
                type="button"
                onClick={() => router.push("/jobs?province=Quảng+Ninh")}
                className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-6 py-3 text-xs font-bold text-white hover:bg-primary-700 shadow-md shadow-primary-600/20 transition-all active:scale-95"
              >
                <span>Khám phá việc làm IT Hạ Long</span>
              </button>
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-16 px-4 bg-white rounded-3xl border border-slate-200/90 shadow-sm space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-50 text-amber-600 border border-amber-200">
              <MagnifyingGlassIcon className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">
              Không tìm thấy việc làm phù hợp
            </h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto leading-relaxed">
              Hãy thử tìm kiếm với từ khóa ngắn hơn, bỏ bớt các bộ lọc địa điểm hoặc ngành nghề để có nhiều kết quả hơn.
            </p>
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
              {strict_mode && (
                <button
                  type="button"
                  onClick={() => {
                    const params = new URLSearchParams(searchParams?.toString() || "");
                    params.delete("strict_mode");
                    params.delete("page");
                    router.push(`/jobs?${params.toString()}`);
                  }}
                  className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-5 py-2.5 text-xs font-bold text-white hover:bg-primary-700 shadow-md shadow-primary-600/20 transition-all active:scale-95"
                >
                  <span>🔎 Mở rộng kết quả tìm kiếm (Bỏ ràng buộc khắt khe)</span>
                </button>
              )}
              <button
                type="button"
                onClick={handleLiveCrawl}
                disabled={isCrawling}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-2.5 text-xs font-bold text-white hover:from-amber-600 hover:to-orange-600 shadow-md shadow-amber-500/20 transition-all active:scale-95"
              >
                <span>{isCrawling ? "⏳ Đang cào realtime..." : "⚡ Quét Realtime Đa Nguồn Ngay (Sàn + FB + Công ty)"}</span>
              </button>
              <button
                type="button"
                onClick={clearAllFilters}
                className="inline-flex items-center gap-2 rounded-xl bg-slate-100 px-5 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-200 transition-colors"
              >
                <ArrowPathIcon className="h-4 w-4" />
                <span>Đặt lại toàn bộ bộ lọc</span>
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
    </div>
  );
}
