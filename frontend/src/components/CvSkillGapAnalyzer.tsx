"use client";

import React, { useState, useMemo } from "react";
import { Job } from "@/types/job";
import { removeVietnameseTones } from "@/lib/clientSearch";
import {
  SparklesIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  DocumentTextIcon,
  ArrowRightIcon,
  LightBulbIcon,
} from "@heroicons/react/24/outline";

interface CvSkillGapAnalyzerProps {
  job: Job;
}

export default function CvSkillGapAnalyzer({ job }: CvSkillGapAnalyzerProps) {
  const [cvText, setCvText] = useState("");
  const [isAnalyzed, setIsAnalyzed] = useState(false);

  // Extract key required keywords from job
  const targetKeywords = useMemo(() => {
    const list = new Set<string>();
    (job.tech_stack || []).forEach((t) => list.add(t));
    if (job.title) {
      job.title.split(/[\s/,]+/).forEach((w) => {
        if (w.length >= 3 && !["tuyển", "gấp", "nhân", "viên"].includes(w.toLowerCase())) {
          list.add(w);
        }
      });
    }
    // Common requirements keywords
    if (job.requirements) {
      ["tiếng anh", "giao tiếp", "tin học văn phòng", "excel", "bằng lái", "kinh nghiệm", "kế toán", "quản trị"].forEach((k) => {
        if (job.requirements && job.requirements.toLowerCase().includes(k)) {
          list.add(k);
        }
      });
    }
    return Array.from(list);
  }, [job]);

  const analysis = useMemo(() => {
    if (!cvText.trim()) return null;

    const normCv = removeVietnameseTones(cvText);
    const matched: string[] = [];
    const missing: string[] = [];

    targetKeywords.forEach((kw) => {
      const normKw = removeVietnameseTones(kw);
      if (normCv.includes(normKw)) {
        matched.push(kw);
      } else {
        missing.push(kw);
      }
    });

    const score = targetKeywords.length > 0
      ? Math.round((matched.length / targetKeywords.length) * 100)
      : 80;

    return {
      score: Math.min(100, Math.max(25, score)),
      matched,
      missing,
    };
  }, [cvText, targetKeywords]);

  const handleQuickPasteSample = () => {
    const sample = `Kinh nghiệm 2 năm làm việc tại vị trí tương đương. Nắm vững tin học văn phòng, Excel nâng cao, kỹ năng giao tiếp tốt. Có kinh nghiệm sử dụng ${job.tech_stack?.[0] || "hệ thống phần mềm chuyên môn"}. Tiếng Anh đọc hiểu tài liệu tốt.`;
    setCvText(sample);
    setIsAnalyzed(true);
  };

  return (
    <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white text-lg font-black shadow-xs">
            ✨
          </div>
          <div>
            <h3 className="text-base sm:text-xl font-black text-black flex items-center gap-2">
              <span>Trình So Khớp CV & Phân Tích Lỗ Hổng Kỹ Năng ATS</span>
              <span className="text-[10px] bg-neutral-100 text-black border border-neutral-300 font-bold px-2 py-0.5 rounded-full uppercase">
                ATS Scanner
              </span>
            </h3>
            <p className="text-xs text-neutral-600 mt-0.5">
              Dán đoạn trích CV hoặc kỹ năng của bạn để đối soát mức độ tương thích trước khi nộp hồ sơ
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleQuickPasteSample}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-black font-bold text-xs transition-colors cursor-pointer self-start sm:self-auto"
        >
          <DocumentTextIcon className="h-4 w-4" />
          <span>Dán mẫu thử nghiệm</span>
        </button>
      </div>

      {/* Input area */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-black flex items-center justify-between">
          <span>Dán đoạn tóm tắt kinh nghiệm hoặc danh sách kỹ năng từ CV của bạn:</span>
          <span className="text-neutral-400 font-normal text-[11px]">Bảo mật 100% trên trình duyệt</span>
        </label>
        <textarea
          rows={3}
          value={cvText}
          onChange={(e) => {
            setCvText(e.target.value);
            setIsAnalyzed(true);
          }}
          placeholder="Ví dụ: Đã có 2 năm kinh nghiệm quản trị mạng, thành thạo Cisco, Linux, Docker, kỹ năng giải quyết sự cố và tiếng Anh giao tiếp..."
          className="w-full p-3.5 rounded-2xl bg-neutral-50 border border-neutral-300 text-black text-xs leading-relaxed focus:outline-none focus:ring-1 focus:ring-black placeholder:text-neutral-400 font-medium"
        />
      </div>

      {/* Analysis Result Display */}
      {analysis && isAnalyzed && (
        <div className="p-4 sm:p-5 rounded-2xl bg-neutral-50 border border-neutral-200 space-y-4 animate-fadeIn">
          {/* Match Score Gauge */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-3.5">
            <div>
              <span className="text-[10px] uppercase font-bold text-neutral-500 tracking-wider block">
                Điểm tương thích hồ sơ ATS:
              </span>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className="text-2xl sm:text-3xl font-black text-black">
                  {analysis.score}%
                </span>
                <span className="text-xs font-semibold text-neutral-700">
                  {analysis.score >= 80
                    ? "Rất xuất sắc! Hồ sơ có độ trùng khớp cao với yêu cầu tuyển dụng."
                    : analysis.score >= 55
                    ? "Khá tốt! Nên bổ sung thêm các từ khóa chuyên ngành còn thiếu vào CV."
                    : "Độ khớp trung bình. Hãy nhấn mạnh các kỹ năng thế mạnh liên quan."}
                </span>
              </div>
            </div>

            <div className="h-3 w-36 bg-neutral-200 rounded-full overflow-hidden p-0.5 self-start sm:self-auto">
              <div
                className="h-full bg-black rounded-full transition-all duration-500"
                style={{ width: `${analysis.score}%` }}
              />
            </div>
          </div>

          {/* 2-Column Comparison: Matched vs Gaps */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {/* Matched Skills */}
            <div className="p-3.5 rounded-xl sm:rounded-2xl bg-white border border-neutral-200 space-y-2">
              <span className="font-bold text-black text-xs flex items-center gap-1.5">
                <CheckCircleIcon className="h-4 w-4 text-black" />
                <span>Kỹ năng đã có trong CV ({analysis.matched.length}):</span>
              </span>
              {analysis.matched.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {analysis.matched.map((sk) => (
                    <span
                      key={sk}
                      className="px-2 py-0.5 rounded-md bg-neutral-100 text-black border border-neutral-300 font-bold text-[11px]"
                    >
                      ✓ {sk}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-neutral-500 text-[11px] italic">
                  Chưa phát hiện từ khóa trùng khớp trong văn bản CV đã dán.
                </p>
              )}
            </div>

            {/* Missing Skills / Gaps */}
            <div className="p-3.5 rounded-xl sm:rounded-2xl bg-white border border-neutral-200 space-y-2">
              <span className="font-bold text-black text-xs flex items-center gap-1.5">
                <ExclamationCircleIcon className="h-4 w-4 text-neutral-600" />
                <span>Kỹ năng JD yêu cầu nhưng chưa thấy ({analysis.missing.length}):</span>
              </span>
              {analysis.missing.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {analysis.missing.map((sk) => (
                    <span
                      key={sk}
                      className="px-2 py-0.5 rounded-md bg-neutral-50 text-neutral-700 border border-neutral-200 font-medium text-[11px]"
                    >
                      + {sk}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-neutral-800 text-[11px] font-bold">
                  🎉 Hoàn hảo! Bạn đã bao phủ toàn bộ các từ khóa cốt lõi của JD!
                </p>
              )}
            </div>
          </div>

          {/* Actionable Advice */}
          <div className="flex items-start gap-2 pt-1 text-[11px] text-neutral-600">
            <LightBulbIcon className="h-4 w-4 text-black shrink-0 mt-0.5" />
            <span>
              <strong>Mẹo tối ưu hồ sơ:</strong> Khi nộp CV cho <strong>{job.company_name}</strong>, hãy đảm bảo các từ khóa chuyên môn xuất hiện tự nhiên trong mục <em>"Kinh nghiệm làm việc"</em> hoặc <em>"Dự án tiêu biểu"</em> thay vì chỉ liệt kê ở phần kỹ năng.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
