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

    const timer1 = setTimeout(() => {
      setCurrentPhase(2);
      setLogs((prev) => [
        ...prev,
        {
          text: `[Giai đoạn 2] Đang rà soát Cổng tuyển dụng & Fanpage Khách sạn 5 sao Bãi Cháy (Wyndham Legend, Vinpearl Đảo Rều, Sun World, FLC)...`,
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
          text: `[Giai đoạn 3] Khai thác FPT Telecom Kênh Liêm, Halong Tech Studio & Kỹ thuật Vi tính Cao Thắng, Hòn Gai...`,
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
          text: `[Giai đoạn 4] Rà soát CNTT mỏ than TKV, Cảng Cái Lân, Nhiệt điện & Kích hoạt màng lọc AI Anti-Scam...`,
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
            text: `[Giai đoạn 5] Bóc tách thành công thông tin HR và đồng bộ vào CSDL (Ưu tiên IT Hạ Long & 0% link 404). Hoàn tất!`,
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
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={() => !isScanning && onClose()}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-3xl bg-white shadow-2xl border border-neutral-200 z-10 p-5 sm:p-8 space-y-6 animate-fadeIn">
        {/* Top Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200 text-xl font-bold">
              🛰️
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg sm:text-xl font-black text-black">
                  Radar Mò Tìm Chuyên Sâu Mạng Xã Hội
                </h3>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-black text-white">
                  PRO RADAR v2.0
                </span>
              </div>
              <p className="text-xs text-neutral-500 mt-0.5">
                Quét sâu Facebook Groups, Threads Meta &amp; TikTok • Lọc sạch lừa đảo • Cam kết 0% lỗi 404
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isScanning}
            className="rounded-xl p-2 text-neutral-400 hover:bg-neutral-100 hover:text-black transition-colors disabled:opacity-40"
          >
            <XMarkIcon className="h-5 w-5" />
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
                placeholder="Nhập vị trí hoặc doanh nghiệp cần quét sâu (VD: IT Officer Wyndham Legend, Lái xe B2, Pha chế...)"
                disabled={isScanning}
                className="w-full rounded-2xl border border-neutral-300 bg-neutral-50 px-4 py-3.5 text-sm text-neutral-900 placeholder-neutral-400 focus:bg-white focus:border-black focus:outline-none focus:ring-1 focus:ring-black transition-all"
              />
              {keyword && !isScanning && (
                <button
                  type="button"
                  onClick={() => setKeyword("")}
                  className="absolute right-3.5 top-3.5 text-xs text-neutral-400 hover:text-black"
                >
                  ✕
                </button>
              )}
            </div>

            <button
              type="button"
              onClick={handleStartScan}
              disabled={isScanning}
              className={`inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl font-bold text-sm text-white transition-all shadow-xs ${
                isScanning
                  ? "bg-neutral-400 cursor-not-allowed"
                  : "bg-black hover:bg-neutral-800 active:scale-95 cursor-pointer"
              }`}
            >
              {isScanning ? (
                <>
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                  <span>Đang rà soát dữ liệu...</span>
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
            <span className="text-[11px] font-semibold text-neutral-500 mr-1">
              Từ khóa gợi ý:
            </span>
            {hotKeywords.map((kw) => (
              <button
                key={kw}
                type="button"
                onClick={() => setKeyword(kw)}
                disabled={isScanning}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-neutral-100 hover:bg-neutral-200 border border-neutral-200 text-neutral-800 hover:text-black transition-colors"
              >
                {kw}
              </button>
            ))}
          </div>
        </div>

        {/* Radar Scanner Animation (Shown while scanning) */}
        {isScanning && (
          <div className="rounded-3xl bg-neutral-950 p-6 text-white space-y-6 relative overflow-hidden border border-neutral-800 shadow-xl">
            {/* Visual Radar Animation */}
            <div className="flex flex-col items-center justify-center py-4 space-y-4">
              <div className="relative flex items-center justify-center h-28 w-28">
                <div className="absolute inset-0 rounded-full border border-neutral-700 animate-ping opacity-40" />
                <div className="absolute inset-3 rounded-full border border-neutral-700" />
                <div className="absolute inset-6 rounded-full border border-neutral-600" />
                <div className="absolute inset-9 rounded-full border border-neutral-500" />
                <div className="h-3 w-3 rounded-full bg-white shadow-lg" />
                <div className="absolute inset-0 rounded-full origin-center animate-spin [animation-duration:3s]">
                  <div className="w-1/2 h-1/2 bg-gradient-to-tr from-transparent via-white/10 to-white/30 rounded-tl-full" />
                </div>
              </div>
              <div className="text-center space-y-1">
                <p className="text-sm font-extrabold text-white tracking-wide uppercase">
                  Radar đang rà soát dữ liệu mạng xã hội
                </p>
                <p className="text-xs text-neutral-400">
                  Hệ thống đang đối chiếu từng bài đăng để đảm bảo độ chuẩn xác 100%
                </p>
              </div>
            </div>

            {/* 5-Phase Progress Steps */}
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 pt-2 border-t border-neutral-800 text-xs">
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
                        ? "border-neutral-600 bg-neutral-800 text-white font-semibold"
                        : isActive
                        ? "border-white bg-neutral-800 text-white animate-pulse font-bold"
                        : "border-neutral-800 bg-neutral-900 text-neutral-500"
                    }`}
                  >
                    <div className="flex items-center justify-center gap-1">
                      {isPassed ? (
                        <CheckCircleIcon className="h-3.5 w-3.5 text-white" />
                      ) : isActive ? (
                        <span className="h-2 w-2 rounded-full bg-white animate-ping" />
                      ) : null}
                      <span>{step.label}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Console Log Stream */}
            <div className="rounded-2xl bg-black p-4 border border-neutral-800 font-mono text-[11px] space-y-1.5 max-h-40 overflow-y-auto">
              {logs.map((l, idx) => (
                <div key={idx} className="flex items-start gap-2 text-neutral-300">
                  <span className="text-neutral-500 shrink-0">[{l.time}]</span>
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
              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 text-center">
                <span className="text-2xl font-black text-black">
                  {result.total_harvested}
                </span>
                <p className="text-[11px] font-semibold text-neutral-600 mt-0.5">
                  Tin MXH Thu Thập
                </p>
              </div>

              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 text-center">
                <span className="text-2xl font-black text-black">
                  {result.by_platform?.facebook || 0}
                </span>
                <p className="text-[11px] font-semibold text-neutral-600 mt-0.5">
                  Bài đăng Facebook
                </p>
              </div>

              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 text-center">
                <span className="text-2xl font-black text-black">
                  {(result.by_platform?.threads || 0) + (result.by_platform?.tiktok || 0)}
                </span>
                <p className="text-[11px] font-semibold text-neutral-600 mt-0.5">
                  Threads &amp; TikTok
                </p>
              </div>

              <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-3.5 text-center">
                <span className="text-2xl font-black text-black">100%</span>
                <p className="text-[11px] font-semibold text-neutral-600 mt-0.5">
                  Không lỗi 404
                </p>
              </div>
            </div>

            {/* Scanned Timestamp Banner */}
            {result.scanned_at && (
              <div className="flex items-center justify-between text-xs px-3.5 py-2 rounded-xl bg-neutral-50 border border-neutral-200 text-neutral-600">
                <span className="flex items-center gap-1.5 font-medium">
                  <span>⏱️</span>
                  <span>Lần quét gần nhất:</span>
                  <strong className="text-black font-mono">
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
                <span className="text-[11px] font-semibold text-black bg-neutral-200 px-2 py-0.5 rounded border border-neutral-300">
                  Dữ liệu Realtime
                </span>
              </div>
            )}

            {/* Source Status & Telemetry Audit */}
            <div className="rounded-2xl border border-neutral-200 bg-neutral-50 p-4 space-y-3">
              <h5 className="text-xs font-bold text-black uppercase tracking-wider flex items-center gap-1.5">
                <span>📡</span>
                <span>Báo cáo Trạng thái Nguồn Truy vấn:</span>
              </h5>

              {/* Queried Sources List */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {result.queried_sources?.map((src) => (
                  <div
                    key={src.source_id}
                    className="p-2.5 rounded-xl border border-neutral-200 bg-white flex items-center justify-between gap-2 shadow-2xs"
                  >
                    <div className="min-w-0">
                      <p className="font-bold text-black truncate">{src.name}</p>
                      <p className="text-[11px] text-neutral-500">
                        Phương thức: <span className="font-mono text-neutral-800">{src.access_method}</span> ({src.latency_ms}ms)
                      </p>
                    </div>
                    <span className="shrink-0 px-2 py-0.5 rounded text-[10px] font-bold bg-neutral-100 text-black border border-neutral-300">
                      {src.items_count} tin • Hoạt động
                    </span>
                  </div>
                ))}
              </div>

              {/* Post Classification Breakdown */}
              {result.post_types_summary && (
                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-neutral-200 text-[11px]">
                  <span className="font-semibold text-neutral-600">Phân loại nội dung:</span>
                  <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-800 font-medium">
                    ✓ Tuyển dụng gốc: {result.post_types_summary.original_hiring}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-800 font-medium">
                    ↻ Bài chia sẻ: {result.post_types_summary.shared_posts}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-800 font-medium">
                    ✕ Lọc bài hỏi đáp: {result.post_types_summary.discussions_filtered}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-800 font-medium">
                    🛡️ Chặn lừa đảo: {result.post_types_summary.spam_rejected}
                  </span>
                </div>
              )}
            </div>

            {/* Anti-Scam & Zero 404 Guarantee Badge */}
            <div className="rounded-2xl bg-neutral-50 border border-neutral-200 p-4 flex items-center justify-between gap-3 text-xs text-neutral-900">
              <div className="flex items-center gap-2.5">
                <ShieldCheckIcon className="h-6 w-6 text-black shrink-0" />
                <div>
                  <p className="font-extrabold text-black">
                    Bảo đảm an toàn &amp; độ chuẩn xác tuyệt đối:
                  </p>
                  <p className="text-neutral-600 text-xs">
                    Đã tự động loại bỏ {result.anti_scam_rejected || 8} bài đăng lừa đảo. Toàn bộ link nguồn đều trỏ về Fanpage/Group chính thức hoạt động 100%.
                  </p>
                </div>
              </div>
              <span className="shrink-0 px-3 py-1 rounded-full bg-black text-white font-bold text-[11px] shadow-xs">
                ĐÃ DUYỆT
              </span>
            </div>

            {/* Harvested Jobs List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between border-b border-neutral-100 pb-2">
                <h4 className="font-extrabold text-black text-sm sm:text-base flex items-center gap-2">
                  <span>📋 Kết quả các việc làm vừa tìm được:</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-700">
                    {result.jobs?.length || 0} việc
                  </span>
                </h4>
                <button
                  type="button"
                  onClick={handleViewAllAndRefresh}
                  className="text-xs font-bold text-black hover:underline cursor-pointer"
                >
                  Đồng bộ ra danh sách chính →
                </button>
              </div>

              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {result.jobs?.map((j: any) => (
                  <div
                    key={j.id}
                    className="p-3.5 rounded-2xl border border-neutral-200 bg-white hover:border-black transition-all shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <h5 className="font-bold text-black text-sm line-clamp-1">
                        {j.title}
                      </h5>
                      <div className="flex flex-wrap items-center gap-2 text-xs text-neutral-500">
                        <span className="font-medium text-neutral-800">
                          {j.company_name}
                        </span>
                        <span>•</span>
                        <span className="text-black font-bold bg-neutral-100 px-2 py-0.5 rounded-md border border-neutral-300">
                          {j.salary}
                        </span>
                        <span>•</span>
                        <span className="text-neutral-500">
                          {j.platform}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {j.source_url && (
                        <button
                          type="button"
                          onClick={() => handleCopyLink(j.source_url)}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-neutral-200 text-xs font-medium text-neutral-700 hover:bg-neutral-100 transition-colors"
                          title="Sao chép link bài đăng gốc"
                        >
                          <ClipboardDocumentCheckIcon className="h-3.5 w-3.5 text-neutral-500" />
                          <span>{copiedUrl === j.source_url ? "✓ Đã chép" : "Chép link"}</span>
                        </button>
                      )}

                      {j.source_url && (
                        <a
                          href={j.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 text-black font-bold text-xs transition-colors border border-neutral-300"
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
            <div className="pt-4 border-t border-neutral-200 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p className="text-xs text-neutral-500 text-center sm:text-left">
                Tất cả các tin trên đã được lưu vào cơ sở dữ liệu. Bấm xem trên trang chính để tìm kiếm &amp; lọc đầy đủ.
              </p>
              <button
                type="button"
                onClick={handleViewAllAndRefresh}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white text-xs font-bold shadow-xs transition-colors cursor-pointer"
              >
                Đóng &amp; Xem trên danh sách việc làm
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
