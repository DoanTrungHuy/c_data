"use client";

import React, { useState, useMemo } from "react";
import { Job } from "@/types/job";
import {
  XMarkIcon,
  EnvelopeIcon,
  ChatBubbleLeftRightIcon,
  ClipboardDocumentCheckIcon,
  CheckCircleIcon,
  ArrowTopRightOnSquareIcon,
  DocumentArrowDownIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";

interface QuickApplyModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
}

export default function QuickApplyModal({
  job,
  isOpen,
  onClose,
}: QuickApplyModalProps) {
  const [activeTab, setActiveTab] = useState<"email" | "zalo">("email");
  const [candidateName, setCandidateName] = useState("");
  const [candidatePhone, setCandidatePhone] = useState("");
  const [candidateExp, setCandidateExp] = useState("2 năm kinh nghiệm");
  const [copiedType, setCopiedType] = useState<string | null>(null);

  const hrPhone =
    job.evidence_proof?.recruiter_contact?.hotline ||
    job.raw_data?.mined?.phones?.[0] ||
    "0912.888.999";
  const hrZalo =
    job.evidence_proof?.recruiter_contact?.zalo ||
    job.raw_data?.mined?.phones?.[0] ||
    hrPhone;
  const hrEmail =
    job.evidence_proof?.recruiter_contact?.email ||
    job.raw_data?.mined?.hr_email ||
    "tuyendung@doanhnghiep.vn";

  const emailSubject = useMemo(() => {
    const namePart = candidateName.trim() ? candidateName.trim() : "[Họ và Tên]";
    return `[Ứng Tuyển] ${job.title} - ${namePart}`;
  }, [job.title, candidateName]);

  const emailBody = useMemo(() => {
    const name = candidateName.trim() || "[Họ và Tên của bạn]";
    const phone = candidatePhone.trim() || "[Số điện thoại của bạn]";
    const company = job.company_name || "Quý Công ty";
    const title = job.title || "vị trí tuyển dụng";
    const techs = (job.tech_stack || []).slice(0, 3).join(", ");
    const loc = job.location_district || job.location_province || job.location_full || "Việt Nam";

    return `Kính gửi: Bộ phận Tuyển dụng ${company},

Em tên là ${name}. Thông qua nền tảng tuyển dụng VịnhViệc, em được biết ${company} hiện đang mở đợt tuyển dụng cho vị trí ${title} tại khu vực ${loc}.

Với nền tảng ${candidateExp} và thế mạnh thực tế trong các kỹ năng/công cụ ${techs || "chuyên môn liên quan"}, em nhận thấy năng lực và định hướng phát triển của bản thân rất phù hợp với các tiêu chí mà Quý Công ty đang tìm kiếm.

Em xin gửi kèm CV đính kèm để Anh/Chị thuận tiện xem xét chi tiết quá trình học tập và các dự án thực tế em từng đảm nhiệm.

Em rất mong có cơ hội được tham gia buổi phỏng vấn để trao đổi chi tiết hơn về cách em có thể đóng góp hiệu quả cho mục tiêu của ${company}.

Em xin chân thành cảm ơn Anh/Chị đã dành thời gian xem hồ sơ!

Trân trọng,
${name}
Số điện thoại: ${phone}`;
  }, [job, candidateName, candidatePhone, candidateExp]);

  const zaloMessage = useMemo(() => {
    const name = candidateName.trim() || "[Họ và Tên]";
    const title = job.title || "vị trí tuyển dụng";
    const company = job.company_name || "công ty";

    return `Em chào Anh/Chị phụ trách tuyển dụng tại ${company} ạ!

Em tên là ${name}, em vừa xem thông tin tuyển dụng vị trí "${title}" của bên mình trên VịnhViệc. Em thấy năng lực và kinh nghiệm của mình rất phù hợp với yêu cầu công việc.

Em xin phép gửi Anh/Chị bản CV đính kèm để Anh/Chị xem xét. Rất mong có cơ hội được hợp tác cùng Quý Công ty ạ. Em cảm ơn Anh/Chị!`;
  }, [job, candidateName]);

  if (!isOpen) return null;

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    setTimeout(() => setCopiedType(null), 2500);
  };

  const downloadTextFile = () => {
    const content = `TIÊU ĐỀ EMAIL:\n${emailSubject}\n\nNỘI DUNG THƯ ỨNG TUYỂN:\n${emailBody}\n\n---\nTIN NHẮN ZALO NHANH:\n${zaloMessage}`;
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Don_Ung_Tuyen_${job.title.replace(/[^a-zA-Z0-9]/g, "_")}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-xs animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-white rounded-2xl sm:rounded-3xl border border-neutral-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-4 sm:p-6 border-b border-neutral-200 flex items-center justify-between bg-neutral-50 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white text-lg font-black shadow-xs">
              ⚡
            </div>
            <div>
              <h2 className="text-base sm:text-lg font-black text-black flex items-center gap-2">
                <span>Soạn Hồ Sơ Ứng Tuyển 1-Chạm</span>
                <span className="text-[10px] bg-neutral-200 text-black px-2 py-0.5 rounded-full font-bold">
                  HR Ready
                </span>
              </h2>
              <p className="text-xs text-neutral-600 mt-0.5 truncate max-w-md">
                Tự động chuẩn hóa email & tin nhắn gửi tới <strong>{job.company_name}</strong>
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-200 transition-colors cursor-pointer"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-5 text-xs">
          {/* Quick Customization Form */}
          <div className="p-3.5 sm:p-4 rounded-2xl bg-neutral-50 border border-neutral-200 space-y-3">
            <span className="font-bold text-black text-xs uppercase tracking-wider block">
              Điền thông tin của bạn (Tùy chọn để cá nhân hóa lời nhắn):
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              <div>
                <label className="text-[11px] font-semibold text-neutral-500 block mb-1">
                  Họ và Tên:
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: Nguyễn Văn An"
                  value={candidateName}
                  onChange={(e) => setCandidateName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white border border-neutral-300 text-black font-medium text-xs focus:outline-none focus:ring-1 focus:ring-black"
                />
              </div>
              <div>
                <label className="text-[11px] font-semibold text-neutral-500 block mb-1">
                  Số điện thoại:
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: 0987.654.321"
                  value={candidatePhone}
                  onChange={(e) => setCandidatePhone(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white border border-neutral-300 text-black font-medium text-xs focus:outline-none focus:ring-1 focus:ring-black"
                />
              </div>
              <div>
                <label className="text-[11px] font-semibold text-neutral-500 block mb-1">
                  Kinh nghiệm:
                </label>
                <select
                  value={candidateExp}
                  onChange={(e) => setCandidateExp(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-white border border-neutral-300 text-black font-medium text-xs focus:outline-none focus:ring-1 focus:ring-black"
                >
                  <option value="kinh nghiệm thực tập & đồ án">Mới tốt nghiệp / Fresher</option>
                  <option value="1 năm kinh nghiệm thực chiến">1 năm kinh nghiệm</option>
                  <option value="2-3 năm kinh nghiệm vững vàng">2 - 3 năm kinh nghiệm</option>
                  <option value="hơn 5 năm kinh nghiệm chuyên sâu">5+ năm kinh nghiệm (Senior)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Platform Tabs: Email vs Zalo */}
          <div className="flex border-b border-neutral-200 gap-4">
            <button
              type="button"
              onClick={() => setActiveTab("email")}
              className={`pb-2.5 font-bold text-xs sm:text-sm flex items-center gap-1.5 transition-colors cursor-pointer border-b-2 -mb-px ${
                activeTab === "email"
                  ? "border-black text-black"
                  : "border-transparent text-neutral-400 hover:text-black"
              }`}
            >
              <EnvelopeIcon className="h-4 w-4" />
              <span>Thư Email Ứng Tuyển</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("zalo")}
              className={`pb-2.5 font-bold text-xs sm:text-sm flex items-center gap-1.5 transition-colors cursor-pointer border-b-2 -mb-px ${
                activeTab === "zalo"
                  ? "border-black text-black"
                  : "border-transparent text-neutral-400 hover:text-black"
              }`}
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              <span>Tin Nhắn Zalo Tuyển Dụng</span>
            </button>
          </div>

          {/* Email Tab Content */}
          {activeTab === "email" && (
            <div className="space-y-3.5">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider">
                    Tiêu đề Email đề xuất:
                  </span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(emailSubject, "subject")}
                    className="text-[11px] font-bold text-black hover:underline cursor-pointer flex items-center gap-1"
                  >
                    {copiedType === "subject" ? "✓ Đã chép tiêu đề" : "Sao chép tiêu đề"}
                  </button>
                </div>
                <div className="p-2.5 rounded-xl bg-neutral-100 border border-neutral-300 font-mono text-black font-semibold text-xs">
                  {emailSubject}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider">
                    Nội dung thư:
                  </span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(emailBody, "body")}
                    className="text-[11px] font-bold text-black hover:underline cursor-pointer flex items-center gap-1"
                  >
                    {copiedType === "body" ? "✓ Đã chép nội dung" : "Sao chép toàn văn thư"}
                  </button>
                </div>
                <textarea
                  readOnly
                  rows={8}
                  value={emailBody}
                  className="w-full p-3 rounded-xl bg-neutral-50 border border-neutral-300 text-neutral-800 text-xs leading-relaxed focus:outline-none select-all font-mono"
                />
              </div>

              {/* Action Buttons for Email */}
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <a
                  href={`mailto:${hrEmail}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
                >
                  <EnvelopeIcon className="h-4 w-4" />
                  <span>Mở ứng dụng Email gửi ngay</span>
                  <ArrowTopRightOnSquareIcon className="h-3 w-3" />
                </a>

                <button
                  type="button"
                  onClick={() => copyToClipboard(emailBody, "body")}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-black font-bold text-xs transition-colors cursor-pointer"
                >
                  <ClipboardDocumentCheckIcon className="h-4 w-4" />
                  <span>Sao chép toàn bộ</span>
                </button>

                <button
                  type="button"
                  onClick={downloadTextFile}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-white hover:bg-neutral-50 border border-neutral-300 text-neutral-800 font-semibold text-xs transition-colors cursor-pointer"
                >
                  <DocumentArrowDownIcon className="h-4 w-4" />
                  <span>Tải file .txt</span>
                </button>
              </div>
            </div>
          )}

          {/* Zalo Tab Content */}
          {activeTab === "zalo" && (
            <div className="space-y-3.5">
              <div className="p-3.5 rounded-xl bg-neutral-100 border border-neutral-300 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-black text-xs">
                    Hotline / Zalo HR: {hrZalo}
                  </span>
                  <a
                    href={`https://zalo.me/${hrZalo}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] bg-black text-white font-bold px-2.5 py-1 rounded-lg hover:bg-neutral-800 transition-colors"
                  >
                    Mở Zalo ngay →
                  </a>
                </div>
                <p className="text-neutral-600 text-[11px]">
                  Bạn có thể sao chép đoạn lời nhắn dưới đây và dán thẳng vào tin nhắn gửi cho HR khi kết bạn Zalo.
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider">
                    Lời nhắn Zalo mẫu:
                  </span>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(zaloMessage, "zalo")}
                    className="text-[11px] font-bold text-black hover:underline cursor-pointer flex items-center gap-1"
                  >
                    {copiedType === "zalo" ? "✓ Đã sao chép" : "Sao chép lời nhắn"}
                  </button>
                </div>
                <textarea
                  readOnly
                  rows={6}
                  value={zaloMessage}
                  className="w-full p-3 rounded-xl bg-neutral-50 border border-neutral-300 text-neutral-800 text-xs leading-relaxed focus:outline-none select-all font-mono"
                />
              </div>

              {/* Action Buttons for Zalo */}
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <a
                  href={`https://zalo.me/${hrZalo}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
                >
                  <span>Mở Zalo {hrZalo}</span>
                  <ArrowTopRightOnSquareIcon className="h-3 w-3" />
                </a>

                <button
                  type="button"
                  onClick={() => copyToClipboard(zaloMessage, "zalo")}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-black font-bold text-xs transition-colors cursor-pointer"
                >
                  <ClipboardDocumentCheckIcon className="h-4 w-4" />
                  <span>Sao chép tin nhắn</span>
                </button>
              </div>
            </div>
          )}

          {/* Pre-flight Checklist */}
          <div className="p-4 rounded-2xl bg-neutral-50 border border-neutral-200 space-y-2">
            <span className="font-bold text-black text-xs uppercase tracking-wider flex items-center gap-1.5">
              <span>📋</span>
              <span>Checklist 4 điểm vàng trước khi bấm gửi:</span>
            </span>
            <ul className="space-y-1.5 text-[11px] text-neutral-700">
              <li className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 rounded-full bg-black text-white flex items-center justify-center text-[9px] font-bold shrink-0">✓</span>
                <span>Xuất file CV định dạng <strong>PDF</strong> để không bị lỗi font trên điện thoại của HR.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 rounded-full bg-black text-white flex items-center justify-center text-[9px] font-bold shrink-0">✓</span>
                <span>Đặt tên file CV chuyên nghiệp: <code>CV_ViTri_HoVaTen.pdf</code>.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 rounded-full bg-black text-white flex items-center justify-center text-[9px] font-bold shrink-0">✓</span>
                <span>Kiểm tra số điện thoại và email cá nhân đã cập nhật mới nhất.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 rounded-full bg-black text-white flex items-center justify-center text-[9px] font-bold shrink-0">✓</span>
                <span>Đã lưu lại số điện thoại hotline <strong>{hrPhone}</strong> để tiện gọi đối soát sau 24h.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-neutral-200 bg-neutral-50 flex items-center justify-between shrink-0">
          <p className="text-[11px] text-neutral-500">
            Dữ liệu tuyển dụng đã đối soát Zero-404 trên VịnhViệc
          </p>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-neutral-200 hover:bg-neutral-300 text-black font-bold text-xs transition-colors cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
}
