"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import {
  XMarkIcon,
  SparklesIcon,
  ClipboardDocumentCheckIcon,
  ClipboardDocumentIcon,
  EnvelopeIcon,
  ChatBubbleLeftRightIcon,
  CheckBadgeIcon,
} from "@heroicons/react/24/outline";
import { Job } from "@/types/job";

interface CoverLetterModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

export default function CoverLetterModal({
  job,
  isOpen,
  onClose,
}: CoverLetterModalProps) {
  const [candidateName, setCandidateName] = useState("Đoàn Trung Huy");
  const [candidatePhone, setCandidatePhone] = useState("0988xxxxxx");
  const [experienceLevel, setExperienceLevel] = useState("1_2_years");
  const [copied, setCopied] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!isOpen || !mounted) return null;

  const hrEmail = job.raw_data?.mined?.hr_email || "";
  const hrPhone = job.raw_data?.mined?.phones?.[0] || "";

  // Dynamic letter generation based on parameters
  const generateEmailSubject = () => {
    return `[Ứng Tuyển] ${job.title} - ${candidateName} - SĐT: ${candidatePhone}`;
  };

  const generateLetterBody = () => {
    const greeting = hrEmail
      ? `Kính gửi: Bộ phận Tuyển dụng / Ban Giám đốc Công ty ${job.company_name},`
      : `Kính gửi: Bộ phận Tuyển dụng ${job.company_name},`;

    let expIntro = "";
    if (experienceLevel === "fresher") {
      expIntro = `Tôi vừa tốt nghiệp chuyên ngành Công nghệ thông tin / Điện tử viễn thông và đã trang bị nền tảng kiến thức vững chắc cùng tinh thần học hỏi cao, sẵn sàng làm quen nhanh chóng với hạ tầng kỹ thuật thực tế của quý công ty.`;
    } else if (experienceLevel === "1_2_years") {
      expIntro = `Tôi đã có hơn 1 - 2 năm kinh nghiệm thực chiến trong lĩnh vực hỗ trợ kỹ thuật IT, quản trị mạng nội bộ LAN/WAN, xử lý sự cố phần cứng, camera và vận hành hệ thống phần mềm nghiệp vụ.`;
    } else {
      expIntro = `Tôi đã có trên 3 năm kinh nghiệm chuyên sâu trong vai trò quản trị hệ thống, triển khai hạ tầng mạng, đảm bảo an toàn an ninh dữ liệu và tối ưu hóa quy trình vận hành CNTT cho doanh nghiệp.`;
    }

    let sectorHighlight = "";
    const titleLower = (job.title || "").toLowerCase();
    const descLower = (job.description || "").toLowerCase();

    if (titleLower.includes("khách sạn") || descLower.includes("opera") || descLower.includes("resort")) {
      sectorHighlight = `Đặc biệt với môi trường khách sạn / resort tại Hạ Long, tôi am hiểu tính chất phục vụ 24/7, luôn sẵn sàng trực ca, xử lý sự cố hệ thống PMS (Opera/Smile), hệ thống WiFi công cộng, tổng đài và khóa từ để đảm bảo trải nghiệm tốt nhất cho khách hàng.`;
    } else if (titleLower.includes("bệnh viện") || descLower.includes("y tế") || descLower.includes("his")) {
      sectorHighlight = `Tôi ý thức sâu sắc tầm quan trọng của tính liên tục và an toàn bảo mật dữ liệu y tế trong hệ thống quản lý bệnh viện (HIS/LIS/PACS), đảm bảo hệ thống luôn sẵn sàng 100% phục vụ công tác khám chữa bệnh.`;
    } else if (titleLower.includes("cảng") || descLower.includes("scada") || descLower.includes("plc")) {
      sectorHighlight = `Tôi có năng lực vận hành hạ tầng mạng công nghiệp, hệ thống camera giám sát biển số container và phối hợp bảo trì hệ thống điều khiển tự động hóa SCADA/PLC phục vụ hoạt động cảng biển và sản xuất.`;
    } else {
      sectorHighlight = `Tôi luôn chủ động kiểm tra định kỳ, phòng ngừa sự cố hạ tầng CNTT, hỗ trợ cán bộ nhân viên nhanh chóng và duy trì sự ổn định tối đa cho hoạt động sản xuất kinh doanh của quý công ty.`;
    }

    return `${greeting}

Tên tôi là ${candidateName} (SĐT: ${candidatePhone}). Qua nền tảng việc làm VịnhViệc, tôi được biết Quý công ty hiện đang có nhu cầu tuyển dụng vị trí: "${job.title}" tại khu vực ${job.location_province || "Hạ Long, Quảng Ninh"}.

Nhận thấy bản thân có định hướng gắn bó lâu dài tại Hạ Long cùng các kỹ năng kỹ thuật phù hợp với yêu cầu tuyển dụng, tôi xin gửi hồ sơ ứng tuyển vào vị trí này.

${expIntro}

${sectorHighlight}

Tôi tự tin với tinh thần trách nhiệm cao, tác phong làm việc cẩn thận, kỷ luật và kỹ năng giao tiếp tốt, tôi sẽ đóng góp tích cực vào đội ngũ kỹ thuật của ${job.company_name}.

Tôi xin gửi kèm CV tóm tắt quá trình học tập và kinh nghiệm công tác để Quý công ty xem xét. Tôi rất mong có cơ hội được tham gia phỏng vấn trực tiếp để trao đổi chi tiết hơn về sự phù hợp của bản thân với vị trí này.

Xin trân trọng cảm ơn Quý công ty và chúc ${job.company_name} ngày càng phát triển vững mạnh!

Người ứng tuyển,
${candidateName}
Số điện thoại: ${candidatePhone}
Email: ${candidateName.toLowerCase().replace(/\s+/g, "")}@gmail.com`;
  };

  const emailSubject = generateEmailSubject();
  const letterBody = generateLetterBody();

  const handleCopy = () => {
    const fullText = `Tiêu đề: ${emailSubject}\n\n${letterBody}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleOpenMailto = () => {
    const mailtoUrl = `mailto:${hrEmail}?subject=${encodeURIComponent(
      emailSubject
    )}&body=${encodeURIComponent(letterBody)}`;
    window.location.href = mailtoUrl;
  };

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-3xl rounded-3xl bg-white shadow-2xl border border-neutral-200 p-6 sm:p-8 z-10 space-y-6 max-h-[92vh] overflow-y-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200">
              <SparklesIcon className="h-6 w-6 text-black" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-black text-black flex items-center gap-2">
                <span>Trợ Lý Soạn Thư Ứng Tuyển &amp; Email Gửi HR</span>
                <span className="text-[10px] bg-neutral-100 text-neutral-800 border border-neutral-300 font-bold px-2 py-0.5 rounded-full uppercase">
                  Tự Động 1 Chạm
                </span>
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Ứng tuyển vị trí <strong>{job.title}</strong> tại <strong>{job.company_name}</strong>
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Input Parameters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-neutral-50 p-4 rounded-2xl border border-neutral-200 text-xs">
          <div>
            <label className="font-bold text-neutral-700 block mb-1">Tên bạn:</label>
            <input
              type="text"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              className="w-full rounded-xl border border-neutral-300 bg-white px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:border-black font-semibold"
            />
          </div>
          <div>
            <label className="font-bold text-neutral-700 block mb-1">Số điện thoại:</label>
            <input
              type="text"
              value={candidatePhone}
              onChange={(e) => setCandidatePhone(e.target.value)}
              className="w-full rounded-xl border border-neutral-300 bg-white px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:border-black font-semibold"
            />
          </div>
          <div>
            <label className="font-bold text-neutral-700 block mb-1">Kinh nghiệm của bạn:</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full rounded-xl border border-neutral-300 bg-white px-3 py-2 text-xs focus:ring-1 focus:ring-black focus:border-black font-semibold"
            >
              <option value="fresher">Mới tốt nghiệp / Dưới 1 năm</option>
              <option value="1_2_years">1 - 2 năm kinh nghiệm</option>
              <option value="3_plus_years">Trên 3 năm kinh nghiệm</option>
            </select>
          </div>
        </div>

        {/* Email Preview Area */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-neutral-700 flex items-center gap-1.5">
              <span>Tiêu đề Email đề xuất:</span>
            </span>
            <span className="text-neutral-400">Chuẩn mực nhân sự</span>
          </div>
          <div className="p-3 bg-neutral-100 rounded-xl text-xs font-mono text-neutral-900 select-all border border-neutral-200">
            {emailSubject}
          </div>

          <div className="pt-2 flex items-center justify-between text-xs">
            <span className="font-bold text-neutral-700">Nội dung thư ứng tuyển:</span>
            {copied && (
              <span className="text-black font-bold flex items-center gap-1 animate-pulse">
                <CheckBadgeIcon className="h-4 w-4" /> Đã sao chép vào bộ nhớ tạm!
              </span>
            )}
          </div>
          <div className="p-4 bg-neutral-50 rounded-2xl text-xs text-neutral-900 leading-relaxed font-sans whitespace-pre-line border border-neutral-200 max-h-60 overflow-y-auto select-all shadow-inner">
            {letterBody}
          </div>
        </div>

        {/* Footer Buttons */}
        <div className="pt-3 border-t border-neutral-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {hrEmail ? (
              <button
                type="button"
                onClick={handleOpenMailto}
                className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95"
              >
                <EnvelopeIcon className="h-4 w-4" />
                <span>Mở Email gửi ngay cho HR ({hrEmail})</span>
              </button>
            ) : null}

            {hrPhone ? (
              <a
                href={`https://zalo.me/${hrPhone}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 text-neutral-900 font-bold text-xs border border-neutral-300 transition-all active:scale-95"
              >
                <ChatBubbleLeftRightIcon className="h-4 w-4" />
                <span>Nhắn Zalo HR ({hrPhone})</span>
              </a>
            ) : null}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
            >
              {copied ? (
                <>
                  <ClipboardDocumentCheckIcon className="h-4 w-4 text-white" />
                  <span>Đã sao chép!</span>
                </>
              ) : (
                <>
                  <ClipboardDocumentIcon className="h-4 w-4" />
                  <span>Sao chép toàn bộ thư</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}
