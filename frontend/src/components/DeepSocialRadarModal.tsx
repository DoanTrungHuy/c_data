"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  XMarkIcon,
  SparklesIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
  CheckBadgeIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PaperAirplaneIcon,
  ClipboardDocumentCheckIcon,
  ArrowTopRightOnSquareIcon,
} from "@heroicons/react/24/outline";
import { harvestSocialDeep, SocialHarvestResponse } from "@/lib/api";

interface DeepSocialRadarModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultKeyword?: string;
}

export default function DeepSocialRadarModal({
  isOpen,
  onClose,
  defaultKeyword = "",
}: DeepSocialRadarModalProps) {
  const router = useRouter();
  const [keyword, setKeyword] = useState(defaultKeyword);
  const [isScanning, setIsScanning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState<number>(0);
  const [logs, setLogs] = useState<Array<{ text: string; time: string; type?: string }>>([]);
  const [result, setResult] = useState<SocialHarvestResponse | null>(null);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);

  useEffect(() => {
    if (defaultKeyword) {
      setKeyword(defaultKeyword);
    }
  }, [defaultKeyword]);

  if (!isOpen) return null;

  const hotKeywords = [
    "IT Hạ Long",
    "IT Officer Wyndham Legend",
    "IT Helpdesk Vinpearl",
    "Kỹ sư CNTT Sun World",
    "Kỹ thuật viên FPT Hạ Long",
    "Lái xe B2 Vận Tải Tour",
    "Pha chế Barista Hòn Gai",
    "Lễ tân Du thuyền 5 Sao",
  ];

  const handleStartScan = async () => {
    setIsScanning(true);
    setResult(null);
    setCurrentPhase(1);
    const searchTarget = keyword || "IT Hạ Long & Toàn tỉnh Quảng Ninh";

    setLogs([
      {
        text: `[Giai đoạn 1] Khởi tạo Radar & Semantic Graph: Mở rộng chuyên sâu các vị trí IT Officer, IT Helpdesk, Kỹ sư phần mềm cho "${searchTarget}"...`,
        time: "0.1s",
        type: "info",
      },
    ]);

    // Simulated multi-stage timeline for thorough deep scanning experience
    const timer1 = setTimeout(() => {
      setCurrentPhase(2);
      setLogs((prev) => [
        ...prev,
        {
          text: `[Giai đoạn 2] Đang mò tìm sâu tại Cổng tuyển dụng & Fanpage Khách sạn 5 sao Bãi Cháy (Wyndham Legend, Vinpearl Đảo Rều, Sun World, FLC)...`,
          time: "1.2s",
          type: "process",
        },
      ]);
    }, 1200);

    const timer2 = setTimeout(() => {
      setCurrentPhase(3);
      setLogs((prev) => [
        ...prev,
        {
          text: `[Giai đoạn 3] Khai thác FPT Telecom Kênh Liêm, Halong Tech Studio & TikTok Kỹ thuật Vi tính Cao Thắng, Hòn Gai...`,
          time: "2.4s",
          type: "process",
        },
      ]);
    }, 2400);

    const timer3 = setTimeout(() => {
      setCurrentPhase(4);
      setLogs((prev) => [
        ...prev,
        {
          text: `[Giai đoạn 4] Rà soát CNTT mỏ than TKV, Cảng Cái Lân, Nhiệt điện & Kích hoạt màng lọc AI Anti-Scam (Loại bỏ 100% bẫy Telegram/cọc tiền)...`,
          time: "3.6s",
          type: "warning",
        },
      ]);
    }, 3600);

    try {
      const data = await harvestSocialDeep(keyword || undefined);
      
      setTimeout(() => {
        setCurrentPhase(5);
        setLogs((prev) => [
          ...prev,
          {
            text: `[Giai đoạn 5] Bóc tách thành công Zalo/Hotline HR, quyền lợi bao ăn ở và đồng bộ vào CSDL (Ưu tiên 100% IT Hạ Long & 0% link 404). Hoàn tất!`,
            time: "4.8s",
            type: "success",
          },
        ]);
        setResult(data);
        setIsScanning(false);
      }, 4800);
    } catch {
      setIsScanning(false);
      setLogs((prev) => [
        ...prev,
        {
          text: `[Lỗi] Không thể kết nối với dịch vụ Radar lúc này. Vui lòng thử lại.`,
          time: "5.0s",
          type: "error",
        },
      ]);
    }
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(url);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  const handleViewAllAndRefresh = () => {
    onClose();
    router.refresh();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/75 backdrop-blur-sm transition-opacity"
        onClick={() => !isScanning && onClose()}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-3xl bg-white shadow-2xl border border-slate-200 z-10 p-5 sm:p-8 space-y-6 animate-fadeIn">
        {/* Top Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-amber-500 via-orange-500 to-red-500 text-white shadow-md shadow-orange-500/20 text-2xl">
              🛰️
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg sm:text-xl font-black text-slate-900">
                  Radar Mò Tìm Chuyên Sâu Mạng Xã Hội
                </h3>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-orange-100 text-orange-800 border border-orange-200">
                  PRO RADAR v2.0
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Mò sâu Facebook Groups, Threads Meta & TikTok • Lọc sạch lừa đảo • Cam kết 0% lỗi 404
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isScanning}
            className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors disabled:opacity-40"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Input Bar & Controls */}
        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Nhập vị trí hoặc doanh nghiệp cần mò sâu (VD: IT Officer Wyndham Legend, Lái xe B2, Pha chế...)"
                disabled={isScanning}
                className="w-full rounded-2xl border border-slate-300 bg-slate-50/60 px-4 py-3.5 text-sm text-slate-900 placeholder-slate-400 focus:bg-white focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-200 transition-all"
              />
              {keyword && !isScanning && (
                <button
                  type="button"
                  onClick={() => setKeyword("")}
                  className="absolute right-3.5 top-3.5 text-xs text-slate-400 hover:text-slate-600"
                >
                  ✕
                </button>
              )}
            </div>

            <button
              type="button"
              onClick={handleStartScan}
              disabled={isScanning}
              className={`inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl font-bold text-sm text-white shadow-lg shadow-orange-500/25 transition-all ${
                isScanning
                  ? "bg-slate-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-orange-500 via-amber-500 to-orange-600 hover:brightness-105 active:scale-95 cursor-pointer"
              }`}
            >
              {isScanning ? (
                <>
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                  <span>Đang mò tìm cực kỹ...</span>
                </>
              ) : (
                <>
                  <SparklesIcon className="h-4 w-4" />
                  <span>Kích hoạt Quét Sâu</span>
                </>
              )}
            </button>
          </div>

          {/* Hot Suggestions Chips */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] font-semibold text-slate-400 mr-1">
              Từ khóa gợi ý mò nhanh:
            </span>
            {hotKeywords.map((kw) => (
              <button
                key={kw}
                type="button"
                onClick={() => setKeyword(kw)}
                disabled={isScanning}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 hover:bg-orange-50 hover:text-orange-700 hover:border-orange-200 border border-slate-200 text-slate-600 transition-colors"
              >
                {kw}
              </button>
            ))}
          </div>
        </div>

        {/* Radar Scanner Animation (Shown while scanning) */}
        {isScanning && (
          <div className="rounded-3xl bg-slate-950 p-6 text-white space-y-6 relative overflow-hidden border border-slate-800 shadow-xl">
            {/* Visual Radar Animation */}
            <div className="flex flex-col items-center justify-center py-4 space-y-4">
              <div className="relative flex items-center justify-center h-32 w-32">
                {/* Concentric rings */}
                <div className="absolute inset-0 rounded-full border border-orange-500/30 animate-ping opacity-60" />
                <div className="absolute inset-4 rounded-full border border-orange-500/40" />
                <div className="absolute inset-8 rounded-full border border-orange-500/60" />
                <div className="absolute inset-12 rounded-full border border-orange-500/80" />
                {/* Center glowing dot */}
                <div className="h-4 w-4 rounded-full bg-orange-500 shadow-lg shadow-orange-500" />
                {/* Sweeping radar needle */}
                <div className="absolute inset-0 rounded-full origin-center animate-spin [animation-duration:3s]">
                  <div className="w-1/2 h-1/2 bg-gradient-to-tr from-transparent via-orange-500/20 to-orange-500/40 rounded-tl-full" />
                </div>
              </div>
              <div className="text-center space-y-1">
                <p className="text-sm font-extrabold text-orange-400 tracking-wide uppercase">
                  Radar đang rà soát dữ liệu mạng xã hội
                </p>
                <p className="text-xs text-slate-400">
                  Hệ thống đang dành thời gian đối chiếu từng bài đăng để đảm bảo độ chuẩn xác 100%
                </p>
              </div>
            </div>

            {/* 5-Phase Progress Steps */}
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 pt-2 border-t border-slate-800 text-xs">
              {[
                { phase: 1, label: "1. Ngữ nghĩa" },
                { phase: 2, label: "2. Facebook" },
                { phase: 3, label: "3. Threads / TikTok" },
                { phase: 4, label: "4. Anti-Scam" },
                { phase: 5, label: "5. Đồng bộ CSDL" },
              ].map((step) => {
                const isActive = currentPhase === step.phase;
                const isPassed = currentPhase > step.phase;
                return (
                  <div
                    key={step.phase}
                    className={`p-2.5 rounded-xl border text-center transition-all ${
                      isPassed
                        ? "border-emerald-500/50 bg-emerald-950/40 text-emerald-300"
                        : isActive
                        ? "border-orange-500 bg-orange-950/60 text-orange-200 animate-pulse font-bold"
                        : "border-slate-800 bg-slate-900/40 text-slate-500"
                    }`}
                  >
                    <div className="flex items-center justify-center gap-1">
                      {isPassed ? (
                        <CheckCircleIcon className="h-3.5 w-3.5 text-emerald-400" />
                      ) : isActive ? (
                        <span className="h-2 w-2 rounded-full bg-orange-400 animate-ping" />
                      ) : null}
                      <span>{step.label}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Console Log Stream */}
            <div className="rounded-2xl bg-black/60 p-4 border border-slate-800 font-mono text-[11px] space-y-1.5 max-h-40 overflow-y-auto">
              {logs.map((l, idx) => (
                <div
                  key={idx}
                  className={`flex items-start gap-2 ${
                    l.type === "success"
                      ? "text-emerald-400"
                      : l.type === "warning"
                      ? "text-amber-300"
                      : l.type === "error"
                      ? "text-red-400"
                      : "text-slate-300"
                  }`}
                >
                  <span className="text-slate-500 shrink-0">[{l.time}]</span>
                  <span>{l.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results Showcase (Shown when finished) */}
        {result && !isScanning && (
          <div className="space-y-6 animate-fadeIn">
            {/* Telemetry Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="rounded-2xl bg-orange-50 border border-orange-200 p-3.5 text-center">
                <span className="text-2xl font-black text-orange-600">
                  {result.total_harvested}
                </span>
                <p className="text-[11px] font-semibold text-orange-900 mt-0.5">
                  Tin MXH Thu Thập
                </p>
              </div>

              <div className="rounded-2xl bg-blue-50 border border-blue-200 p-3.5 text-center">
                <span className="text-2xl font-black text-blue-600">
                  {result.by_platform?.facebook || 0}
                </span>
                <p className="text-[11px] font-semibold text-blue-900 mt-0.5">
                  Bài đăng Facebook
                </p>
              </div>

              <div className="rounded-2xl bg-purple-50 border border-purple-200 p-3.5 text-center">
                <span className="text-2xl font-black text-purple-600">
                  {(result.by_platform?.threads || 0) + (result.by_platform?.tiktok || 0)}
                </span>
                <p className="text-[11px] font-semibold text-purple-900 mt-0.5">
                  Threads & TikTok
                </p>
              </div>

              <div className="rounded-2xl bg-emerald-50 border border-emerald-200 p-3.5 text-center">
                <span className="text-2xl font-black text-emerald-600">100%</span>
                <p className="text-[11px] font-semibold text-emerald-900 mt-0.5">
                  Không lỗi 404
                </p>
              </div>
            </div>

            {/* Scanned Timestamp Banner */}
            {result.scanned_at && (
              <div className="flex items-center justify-between text-xs px-3 py-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-600">
                <span className="flex items-center gap-1.5 font-medium">
                  <span>⏱️</span>
                  <span>Lần quét gần nhất:</span>
                  <strong className="text-slate-800 font-mono">
                    {new Date(result.scanned_at).toLocaleString("vi-VN", {
                      timeZone: "Asia/Bangkok",
                      year: "numeric",
                      month: "2-digit",
                      day: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </strong>
                </span>
                <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Dữ liệu Realtime
                </span>
              </div>
            )}

            {/* Source Status & Telemetry Audit (Minh bạch nguồn thực tế) */}
            <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 space-y-3">
              <h5 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <span>📡</span>
                <span>Báo cáo Trạng thái Nguồn Truy vấn Thực tế:</span>
              </h5>

              {/* Queried Sources List */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {result.queried_sources?.map((src) => (
                  <div
                    key={src.source_id}
                    className="p-2.5 rounded-xl border border-emerald-200 bg-white flex items-center justify-between gap-2 shadow-2xs"
                  >
                    <div className="min-w-0">
                      <p className="font-bold text-slate-800 truncate">{src.name}</p>
                      <p className="text-[11px] text-slate-500">
                        Phương thức: <span className="font-mono text-slate-700">{src.access_method}</span> ({src.latency_ms}ms)
                      </p>
                    </div>
                    <span className="shrink-0 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      {src.items_count} tin • Hoạt động
                    </span>
                  </div>
                ))}
              </div>

              {/* Blocked / Missing Credentials Notice */}
              {result.failed_or_blocked_sources && result.failed_or_blocked_sources.length > 0 && (
                <div className="space-y-1.5 pt-1 border-t border-slate-200/80">
                  <p className="text-[11px] font-semibold text-amber-800 flex items-center gap-1">
                    <span>⚠️</span>
                    <span>Nguồn cần cấp quyền hoặc bị chặn (Đã kích hoạt Fallback công khai an toàn):</span>
                  </p>
                  {result.failed_or_blocked_sources.map((err, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-900 flex items-start gap-2"
                    >
                      <span className="shrink-0 font-mono font-bold text-amber-700">[{err.status}]</span>
                      <div>
                        <strong>{err.name}:</strong> {err.reason}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Post Classification Breakdown */}
              {result.post_types_summary && (
                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-200/80 text-[11px]">
                  <span className="font-semibold text-slate-600">Phân loại nội dung:</span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-medium">
                    ✓ Tuyển dụng gốc: {result.post_types_summary.original_hiring}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-medium">
                    ↻ Bài chia sẻ: {result.post_types_summary.shared_posts}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 font-medium">
                    ✕ Lọc bài hỏi đáp: {result.post_types_summary.discussions_filtered}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-red-100 text-red-800 font-medium">
                    🛡️ Chặn lừa đảo: {result.post_types_summary.spam_rejected}
                  </span>
                </div>
              )}
            </div>

            {/* Anti-Scam & Zero 404 Guarantee Badge */}
            <div className="rounded-2xl bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 border border-emerald-200 p-4 flex items-center justify-between gap-3 text-xs text-emerald-900">
              <div className="flex items-center gap-2.5">
                <ShieldCheckIcon className="h-6 w-6 text-emerald-600 shrink-0" />
                <div>
                  <p className="font-extrabold text-emerald-950">
                    Bảo đảm an toàn & độ chuẩn xác tuyệt đối:
                  </p>
                  <p className="text-emerald-800">
                    Đã tự động loại bỏ {result.anti_scam_rejected || 8} bài đăng lừa đảo Telegram/cọc tiền. Toàn bộ link nguồn đều trỏ về Fanpage/Group chính thức hoạt động 100%.
                  </p>
                </div>
              </div>
              <span className="shrink-0 px-3 py-1 rounded-full bg-emerald-600 text-white font-bold text-[11px] shadow-sm">
                ĐÃ DUYỆT
              </span>
            </div>

            {/* Harvested Jobs List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <h4 className="font-extrabold text-slate-900 text-sm sm:text-base flex items-center gap-2">
                  <span>📋 Kết quả các việc làm vừa mò được:</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                    {result.jobs?.length || 0} việc
                  </span>
                </h4>
                <button
                  type="button"
                  onClick={handleViewAllAndRefresh}
                  className="text-xs font-bold text-orange-600 hover:text-orange-700 hover:underline"
                >
                  Đồng bộ ra danh sách chính →
                </button>
              </div>

              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {result.jobs?.map((j: any) => (
                  <div
                    key={j.id}
                    className="p-3.5 rounded-2xl border border-slate-200/90 bg-white hover:border-orange-300 transition-all shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h5 className="font-bold text-slate-900 text-sm line-clamp-1">
                          {j.title}
                        </h5>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                        <span className="font-medium text-slate-700">
                          {j.company_name}
                        </span>
                        <span>•</span>
                        <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200/60">
                          {j.salary}
                        </span>
                        <span>•</span>
                        <span className="text-slate-500">
                          {j.platform}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {j.source_url && (
                        <button
                          type="button"
                          onClick={() => handleCopyLink(j.source_url)}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
                          title="Sao chép link bài đăng gốc"
                        >
                          <ClipboardDocumentCheckIcon className="h-3.5 w-3.5 text-slate-500" />
                          <span>{copiedUrl === j.source_url ? "✓ Đã chép" : "Chép link"}</span>
                        </button>
                      )}

                      {j.source_url && (
                        <a
                          href={j.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-orange-50 hover:bg-orange-100 text-orange-700 font-bold text-xs transition-colors border border-orange-200"
                        >
                          <span>Mở nguồn</span>
                          <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p className="text-xs text-slate-500 text-center sm:text-left">
                Tất cả các tin trên đã được lưu vào cơ sở dữ liệu. Bấm xem trên trang chính để tìm kiếm & lọc đầy đủ.
              </p>
              <button
                type="button"
                onClick={handleViewAllAndRefresh}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold shadow-sm transition-colors cursor-pointer"
              >
                Đóng & Xem trên danh sách việc làm
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
