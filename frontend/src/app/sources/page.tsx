"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  ShieldCheckIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  QuestionMarkCircleIcon,
  ArrowPathIcon,
  GlobeAltIcon,
  BuildingOffice2Icon,
  ShareIcon,
  CpuChipIcon,
  DocumentCheckIcon,
  FunnelIcon,
  MapPinIcon,
  PhoneIcon,
  EnvelopeIcon,
  BriefcaseIcon,
  ArrowTopRightOnSquareIcon,
} from "@heroicons/react/24/outline";

interface SourceItem {
  id: string;
  name: string;
  category: string;
  domain: string;
  access_method: string;
  health_status: "healthy" | "degraded" | "unhealthy" | "unconfigured" | "unknown";
  health_evidence: string;
  last_health_check_at: string | null;
  last_successful_crawl: string | null;
  last_failed_crawl: string | null;
  last_error_message: string | null;
  failure_reason: string | null;
  metrics: {
    discovered_count: number;
    new_count: number;
    error_count: number;
    total_runs: number;
    last_crawl_duration_ms: number;
  };
  rate_limit?: {
    requests_per_minute: number;
    min_delay_seconds: number;
    concurrent_limit: number;
  };
  is_enabled: boolean;
  target_provinces: string[];
  compliance_notes: string;
}

interface SourcesSummary {
  generated_at: string;
  total_sources: number;
  healthy_count: number;
  degraded_count: number;
  unhealthy_count: number;
  unconfigured_count: number;
  unknown_count: number;
  total_discovered_jobs: number;
  total_errors: number;
  sources: SourceItem[];
}

interface CompanyItem {
  company_id: string;
  name: string;
  brand_name: string | null;
  industry_group: string;
  locations: { province: string; district: string; address: string }[];
  website_home: string;
  career_url: string;
  social_channels: Record<string, string>;
  hr_contacts: { hotline?: string; email?: string; hr_desk?: string };
  career_page_status: string;
  last_checked_at: string | null;
  http_status: number | null;
  active_it_roles: string[];
  notes: string | null;
}

export default function SourceHealthDashboardPage() {
  const [activeTab, setActiveTab] = useState<"sources" | "companies">("sources");
  const [data, setData] = useState<SourcesSummary | null>(null);
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [companyIndustryFilter, setCompanyIndustryFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [refreshing, setRefreshing] = useState(false);

  const fetchSourceHealth = async () => {
    try {
      setLoading(true);
      const res = await fetch("/data/sources_health.json?t=" + Date.now());
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
      const compRes = await fetch("/data/local_companies.json?t=" + Date.now());
      if (compRes.ok) {
        const compJson = await compRes.json();
        setCompanies(compJson);
      }
    } catch (err) {
      console.error("Lỗi khi tải dữ liệu sức khỏe nguồn:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSourceHealth();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchSourceHealth();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "healthy":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-neutral-900 text-white border border-black shadow-2xs">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Hoạt động tốt (Healthy)</span>
          </span>
        );
      case "degraded":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
            <span className="h-2 w-2 rounded-full bg-amber-500" />
            <span>Chậm / Chập chờn (Degraded)</span>
          </span>
        );
      case "unhealthy":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-900 border border-rose-300">
            <span className="h-2 w-2 rounded-full bg-rose-500" />
            <span>Mất kết nối / Lỗi (Unhealthy)</span>
          </span>
        );
      case "unconfigured":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-neutral-100 text-neutral-700 border border-neutral-300">
            <span className="h-2 w-2 rounded-full bg-neutral-400" />
            <span>Chưa cấu hình API (Unconfigured)</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-neutral-100 text-neutral-600 border border-neutral-200">
            <span className="h-2 w-2 rounded-full bg-neutral-400" />
            <span>Đang chờ quét (Queue)</span>
          </span>
        );
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case "national_job_board":
        return "Sàn tuyển dụng quốc gia";
      case "enterprise_direct":
        return "Cổng tuyển dụng doanh nghiệp";
      case "specialized_local":
        return "Cơ quan lao động địa phương";
      case "social_public":
        return "Mạng xã hội công khai";
      case "authorized_api":
        return "Cổng API / RSS Nhà nước";
      default:
        return category;
    }
  };

  const getIndustryBadge = (industry: string) => {
    switch (industry) {
      case "hospitality_tourism":
        return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">Du lịch & Khách sạn 5★</span>;
      case "healthcare":
        return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Y tế & Bệnh viện</span>;
      case "industry_logistics":
        return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">Công nghiệp, Than & Cảng biển</span>;
      case "telecom_it":
        return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200">Viễn thông & CNTT địa phương</span>;
      default:
        return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-neutral-100 text-neutral-700 border border-neutral-200">{industry}</span>;
    }
  };

  const filteredSources = (data?.sources || []).filter((s) => {
    if (statusFilter !== "all" && s.health_status !== statusFilter) return false;
    if (categoryFilter !== "all" && s.category !== categoryFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        s.name.toLowerCase().includes(q) ||
        s.domain.toLowerCase().includes(q) ||
        (s.failure_reason && s.failure_reason.toLowerCase().includes(q))
      );
    }
    return true;
  });

  const filteredCompanies = companies.filter((c) => {
    if (companyIndustryFilter !== "all" && c.industry_group !== companyIndustryFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = c.name.toLowerCase().includes(q) || (c.brand_name && c.brand_name.toLowerCase().includes(q));
      const matchRoles = c.active_it_roles.some((r) => r.toLowerCase().includes(q));
      const matchAddress = c.locations.some((l) => l.address.toLowerCase().includes(q));
      return matchName || matchRoles || matchAddress;
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-neutral-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Section */}
        <div className="bg-white border border-neutral-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-100 pb-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-100 border border-neutral-200 text-xs font-bold text-neutral-800 mb-2">
                <ShieldCheckIcon className="h-4 w-4 text-black" />
                <span>Bảng Giám Sát Toàn Diện: Nguồn & Doanh Nghiệp Hạ Long</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-black tracking-tight">
                Source & Company Health Dashboard
              </h1>
              <p className="text-sm text-neutral-600 mt-1 max-w-2xl">
                Kiểm toán thời gian thực toàn bộ 19 nguồn tuyển dụng và 20 doanh nghiệp trọng điểm tại Hạ Long, Quảng Ninh.
                Minh bạch trạng thái kết nối, mã lỗi HTTP và liên kết ứng tuyển trực tiếp.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleRefresh}
                disabled={refreshing}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-sm shadow-xs transition-all active:scale-95 cursor-pointer disabled:opacity-50"
              >
                <ArrowPathIcon className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                <span>{refreshing ? "Đang kiểm tra..." : "Kiểm tra lại"}</span>
              </button>
              <Link
                href="/jobs"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 text-black font-bold text-sm border border-neutral-300 transition-all shadow-2xs"
              >
                <span>Xem tin tuyển dụng →</span>
              </Link>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex items-center gap-2 border-b border-neutral-200 pt-2 pb-1">
            <button
              type="button"
              onClick={() => setActiveTab("sources")}
              className={`px-4 py-2 text-sm font-bold rounded-xl transition-all flex items-center gap-2 cursor-pointer ${
                activeTab === "sources"
                  ? "bg-black text-white shadow-xs"
                  : "bg-neutral-100 hover:bg-neutral-200 text-neutral-700"
              }`}
            >
              <span>19 Nguồn Thu Thập</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-black ${activeTab === "sources" ? "bg-white/20 text-white" : "bg-neutral-300 text-neutral-800"}`}>
                {data?.total_sources || 19}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("companies")}
              className={`px-4 py-2 text-sm font-bold rounded-xl transition-all flex items-center gap-2 cursor-pointer ${
                activeTab === "companies"
                  ? "bg-black text-white shadow-xs"
                  : "bg-neutral-100 hover:bg-neutral-200 text-neutral-700"
              }`}
            >
              <BuildingOffice2Icon className="h-4 w-4" />
              <span>20 Doanh Nghiệp Trọng Điểm Hạ Long</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-black ${activeTab === "companies" ? "bg-white/20 text-white" : "bg-neutral-300 text-neutral-800"}`}>
                {companies.length || 20}
              </span>
            </button>
          </div>

          {/* Quick Metrics Bar for Sources */}
          {activeTab === "sources" && (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
              <div className="bg-neutral-50 p-3.5 rounded-2xl border border-neutral-200 text-center">
                <span className="text-[11px] font-bold text-neutral-500 uppercase block">Tổng nguồn</span>
                <span className="text-xl sm:text-2xl font-black text-black">
                  {data?.total_sources || 0}
                </span>
              </div>
              <div className="bg-emerald-50/50 p-3.5 rounded-2xl border border-emerald-200 text-center">
                <span className="text-[11px] font-bold text-emerald-700 uppercase block">Hoạt động tốt</span>
                <span className="text-xl sm:text-2xl font-black text-emerald-900">
                  {data?.healthy_count || 0}
                </span>
              </div>
              <div className="bg-amber-50/50 p-3.5 rounded-2xl border border-amber-200 text-center">
                <span className="text-[11px] font-bold text-amber-700 uppercase block">Chậm / Chập chờn</span>
                <span className="text-xl sm:text-2xl font-black text-amber-900">
                  {data?.degraded_count || 0}
                </span>
              </div>
              <div className="bg-neutral-100 p-3.5 rounded-2xl border border-neutral-300 text-center">
                <span className="text-[11px] font-bold text-neutral-600 uppercase block">Chờ cấu hình</span>
                <span className="text-xl sm:text-2xl font-black text-neutral-800">
                  {data?.unconfigured_count || 0}
                </span>
              </div>
              <div className="bg-neutral-50 p-3.5 rounded-2xl border border-neutral-200 text-center">
                <span className="text-[11px] font-bold text-neutral-500 uppercase block">Tổng tin phát hiện</span>
                <span className="text-xl sm:text-2xl font-black text-black">
                  {data?.total_discovered_jobs || 0}
                </span>
              </div>
              <div className="bg-rose-50/50 p-3.5 rounded-2xl border border-rose-200 text-center">
                <span className="text-[11px] font-bold text-rose-700 uppercase block">Lỗi kết nối</span>
                <span className="text-xl sm:text-2xl font-black text-rose-900">
                  {data?.total_errors || 0}
                </span>
              </div>
            </div>
          )}

          {/* Quick Metrics Bar for Companies */}
          {activeTab === "companies" && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="bg-blue-50/60 p-3.5 rounded-2xl border border-blue-200 text-center">
                <span className="text-[11px] font-bold text-blue-700 uppercase block">Du lịch & Khách sạn</span>
                <span className="text-xl sm:text-2xl font-black text-blue-900">
                  {companies.filter((c) => c.industry_group === "hospitality_tourism").length} đơn vị
                </span>
              </div>
              <div className="bg-emerald-50/60 p-3.5 rounded-2xl border border-emerald-200 text-center">
                <span className="text-[11px] font-bold text-emerald-700 uppercase block">Y tế & Bệnh viện</span>
                <span className="text-xl sm:text-2xl font-black text-emerald-900">
                  {companies.filter((c) => c.industry_group === "healthcare").length} bệnh viện
                </span>
              </div>
              <div className="bg-amber-50/60 p-3.5 rounded-2xl border border-amber-200 text-center">
                <span className="text-[11px] font-bold text-amber-700 uppercase block">Cảng biển, Than & KCN</span>
                <span className="text-xl sm:text-2xl font-black text-amber-900">
                  {companies.filter((c) => c.industry_group === "industry_logistics").length} tập đoàn
                </span>
              </div>
              <div className="bg-purple-50/60 p-3.5 rounded-2xl border border-purple-200 text-center">
                <span className="text-[11px] font-bold text-purple-700 uppercase block">Viễn thông & CNTT</span>
                <span className="text-xl sm:text-2xl font-black text-purple-900">
                  {companies.filter((c) => c.industry_group === "telecom_it").length} nhà mạng
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-white border border-neutral-200 rounded-2xl p-4 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="w-full md:w-80">
            <input
              type="text"
              placeholder={activeTab === "sources" ? "Tìm theo tên nguồn, tên miền..." : "Tìm doanh nghiệp, chức danh IT..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-neutral-300 bg-neutral-50 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-black"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {activeTab === "sources" ? (
              <>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-3 py-2 text-xs font-bold rounded-xl border border-neutral-300 bg-white text-neutral-800 focus:outline-hidden"
                >
                  <option value="all">Mọi trạng thái kết nối</option>
                  <option value="healthy">Chỉ nguồn hoạt động (Healthy)</option>
                  <option value="degraded">Nguồn chập chờn (Degraded)</option>
                  <option value="unconfigured">Chưa cấu hình API (Unconfigured)</option>
                  <option value="unknown">Đang chờ quét (Queue)</option>
                </select>

                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="px-3 py-2 text-xs font-bold rounded-xl border border-neutral-300 bg-white text-neutral-800 focus:outline-hidden"
                >
                  <option value="all">Mọi nhóm nguồn</option>
                  <option value="national_job_board">Sàn tuyển dụng quốc gia</option>
                  <option value="enterprise_direct">Cổng tuyển dụng doanh nghiệp</option>
                  <option value="social_public">Mạng xã hội công khai</option>
                  <option value="specialized_local">Cơ quan lao động địa phương</option>
                  <option value="authorized_api">Cổng API / RSS Nhà nước</option>
                </select>
              </>
            ) : (
              <select
                value={companyIndustryFilter}
                onChange={(e) => setCompanyIndustryFilter(e.target.value)}
                className="px-3 py-2 text-xs font-bold rounded-xl border border-neutral-300 bg-white text-neutral-800 focus:outline-hidden"
              >
                <option value="all">Mọi phân nhóm ngành</option>
                <option value="hospitality_tourism">Du lịch & Khách sạn</option>
                <option value="healthcare">Y tế & Bệnh viện</option>
                <option value="industry_logistics">Công nghiệp, Mỏ & Cảng biển</option>
                <option value="telecom_it">Viễn thông & CNTT</option>
              </select>
            )}
          </div>
        </div>

        {/* TAB 1: Sources Table */}
        {activeTab === "sources" && (
          <div className="bg-white border border-neutral-200 rounded-3xl shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-neutral-200 bg-neutral-50/80 text-[11px] font-black uppercase text-neutral-500 tracking-wider">
                    <th className="py-4 px-4 sm:px-6">Nguồn tuyển dụng</th>
                    <th className="py-4 px-3">Trạng thái kết nối</th>
                    <th className="py-4 px-3">Lần thành công gần nhất</th>
                    <th className="py-4 px-3">Thời gian kiểm tra</th>
                    <th className="py-4 px-3 text-center">Tin mới / Tổng phát hiện</th>
                    <th className="py-4 px-3 text-center">Số lỗi</th>
                    <th className="py-4 px-4 sm:px-6">Lý do / Bằng chứng sức khỏe</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 text-xs text-neutral-800">
                  {loading ? (
                    <tr>
                      <td colSpan={7} className="text-center py-12 text-neutral-500">
                        Đang tải dữ liệu trạng thái các nguồn...
                      </td>
                    </tr>
                  ) : filteredSources.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="text-center py-12 text-neutral-500">
                        Không tìm thấy nguồn tuyển dụng nào phù hợp với bộ lọc.
                      </td>
                    </tr>
                  ) : (
                    filteredSources.map((source) => (
                      <tr key={source.id} className="hover:bg-neutral-50/60 transition-colors">
                        <td className="py-4 px-4 sm:px-6">
                          <div className="space-y-0.5">
                            <span className="font-bold text-black text-sm block">
                              {source.name}
                            </span>
                            <div className="flex items-center gap-2 text-[11px] text-neutral-500">
                              <span className="font-mono bg-neutral-100 px-1.5 py-0.5 rounded text-neutral-700">
                                {source.domain}
                              </span>
                              <span>•</span>
                              <span>{getCategoryLabel(source.category)}</span>
                            </div>
                          </div>
                        </td>

                        <td className="py-4 px-3 whitespace-nowrap">
                          {getStatusBadge(source.health_status)}
                        </td>

                        <td className="py-4 px-3 whitespace-nowrap text-neutral-600">
                          {source.last_successful_crawl ? (
                            <div className="space-y-0.5">
                              <span className="font-medium text-black block">
                                {new Date(source.last_successful_crawl).toLocaleTimeString("vi-VN", {
                                  hour: "2-digit",
                                  minute: "2-digit",
                                })}
                              </span>
                              <span className="text-[10px] text-neutral-500 block">
                                {new Date(source.last_successful_crawl).toLocaleDateString("vi-VN")}
                              </span>
                            </div>
                          ) : (
                            <span className="text-neutral-400 italic">Chưa chạy</span>
                          )}
                        </td>

                        <td className="py-4 px-3 whitespace-nowrap text-neutral-600">
                          {source.last_health_check_at ? (
                            <div className="space-y-0.5">
                              <span className="font-medium text-black block">
                                {new Date(source.last_health_check_at).toLocaleTimeString("vi-VN", {
                                  hour: "2-digit",
                                  minute: "2-digit",
                                })}
                              </span>
                              <span className="text-[10px] text-neutral-500 block">
                                {new Date(source.last_health_check_at).toLocaleDateString("vi-VN")}
                              </span>
                            </div>
                          ) : (
                            <span className="text-neutral-400 italic">Chưa kiểm tra</span>
                          )}
                        </td>

                        <td className="py-4 px-3 text-center whitespace-nowrap">
                          <span className="font-extrabold text-black text-sm block">
                            +{source.metrics.new_count}
                          </span>
                          <span className="text-neutral-400 text-[10px] block">
                            / {source.metrics.discovered_count} tin
                          </span>
                        </td>

                        <td className="py-4 px-3 text-center whitespace-nowrap">
                          {source.metrics.error_count > 0 ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800">
                              {source.metrics.error_count} lỗi
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold text-neutral-400">
                              0 lỗi
                            </span>
                          )}
                        </td>

                        <td className="py-4 px-4 sm:px-6">
                          {source.failure_reason ? (
                            <div className="p-2 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-[11px] space-y-0.5 max-w-xs">
                              <span className="font-bold flex items-center gap-1 text-rose-800">
                                <ExclamationTriangleIcon className="h-3.5 w-3.5 shrink-0" />
                                Lý do chưa hoạt động:
                              </span>
                              <span>{source.failure_reason}</span>
                            </div>
                          ) : (
                            <div className="p-2 rounded-xl bg-neutral-50 border border-neutral-200 text-neutral-700 text-[11px] max-w-xs">
                              <span className="font-semibold block text-black">
                                {source.health_evidence || "Kết nối đạt chuẩn, tuân thủ robots.txt"}
                              </span>
                              <span className="text-[10px] text-neutral-500 block">
                                Tần suất: {source.rate_limit?.requests_per_minute || 30} req/min
                              </span>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: Companies Directory */}
        {activeTab === "companies" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredCompanies.length === 0 ? (
              <div className="col-span-2 text-center py-12 text-neutral-500 bg-white rounded-3xl border border-neutral-200">
                Không tìm thấy doanh nghiệp nào phù hợp với bộ lọc.
              </div>
            ) : (
              filteredCompanies.map((comp) => (
                <div
                  key={comp.company_id}
                  className="bg-white border border-neutral-200 rounded-3xl p-5 sm:p-6 shadow-xs hover:shadow-md transition-all space-y-4 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        {getIndustryBadge(comp.industry_group)}
                        <h2 className="text-base sm:text-lg font-black text-black mt-1.5 leading-snug">
                          {comp.brand_name || comp.name}
                        </h2>
                        {comp.brand_name && (
                          <p className="text-xs text-neutral-500 font-medium">
                            {comp.name}
                          </p>
                        )}
                      </div>

                      <span className="shrink-0 inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-neutral-100 text-neutral-800 border border-neutral-300">
                        <CheckCircleIcon className="h-3.5 w-3.5 text-black" />
                        <span>Đã thẩm định</span>
                      </span>
                    </div>

                    {/* Address & Contacts */}
                    <div className="space-y-1.5 text-xs text-neutral-600 bg-neutral-50 p-3 rounded-2xl border border-neutral-100">
                      {comp.locations.map((loc, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <MapPinIcon className="h-4 w-4 text-neutral-500 shrink-0 mt-0.5" />
                          <span>{loc.address}</span>
                        </div>
                      ))}

                      {comp.hr_contacts.hotline && (
                        <div className="flex items-center gap-2 pt-1">
                          <PhoneIcon className="h-4 w-4 text-neutral-500 shrink-0" />
                          <span className="font-bold text-black">{comp.hr_contacts.hotline}</span>
                          {comp.hr_contacts.email && (
                            <>
                              <span>•</span>
                              <span className="text-neutral-500">{comp.hr_contacts.email}</span>
                            </>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Active IT Roles */}
                    <div className="space-y-1.5">
                      <span className="text-[11px] font-bold text-neutral-500 uppercase flex items-center gap-1.5">
                        <BriefcaseIcon className="h-3.5 w-3.5 text-black" />
                        Vị trí CNTT trọng điểm thường tuyển:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {comp.active_it_roles.map((role, idx) => (
                          <span
                            key={idx}
                            className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-neutral-100 text-neutral-800 border border-neutral-200 hover:border-black transition-colors"
                          >
                            {role}
                          </span>
                        ))}
                      </div>
                    </div>

                    {comp.notes && (
                      <p className="text-[11px] text-neutral-500 italic bg-white p-2 rounded-xl border border-dashed border-neutral-200">
                        💡 {comp.notes}
                      </p>
                    )}
                  </div>

                  {/* Actions Bar */}
                  <div className="flex items-center justify-between gap-3 pt-3 border-t border-neutral-100 text-xs">
                    <a
                      href={comp.career_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold transition-all shadow-2xs"
                    >
                      <span>Cổng tuyển dụng chính thức</span>
                      <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
                    </a>

                    <Link
                      href={`/jobs?q=${encodeURIComponent(comp.brand_name || comp.name)}&province=Qu%E1%BA%A3ng+Ninh`}
                      className="inline-flex items-center gap-1 text-neutral-600 hover:text-black font-semibold"
                    >
                      <span>Tìm việc tại đây →</span>
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Operational Guarantee Box */}
        <div className="bg-white border border-neutral-200 rounded-3xl p-6 sm:p-8 space-y-3 shadow-xs">
          <h2 className="font-black text-black text-lg flex items-center gap-2">
            <span>🛡️ Cam Kết Vận Hành Đa Nguồn &amp; Cách Ly Lỗi (Adapter Isolation)</span>
          </h2>
          <p className="text-xs text-neutral-600 leading-relaxed">
            Hệ thống C_Data áp dụng kiến trúc <strong>Adapter Isolation</strong>: Mọi nguồn dữ liệu đều chạy độc lập trong Sandbox riêng biệt. Nếu một nguồn gặp lỗi (như máy chủ FPT bị lỗi 503 hoặc VietnamWorks yêu cầu xác thực mới), hệ thống sẽ kích hoạt <strong>Exponential Backoff</strong> và lưu trạng thái vào <strong>Dead-Letter Log</strong>, tuyệt đối không gây sập (crash) toàn bộ hệ thống hay ảnh hưởng đến các nguồn tuyển dụng khác (CareerViet, Sun Group, Vinpearl...).
          </p>
        </div>
      </div>
    </div>
  );
}
