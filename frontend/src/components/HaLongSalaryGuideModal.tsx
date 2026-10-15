"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import {
  XMarkIcon,
  CurrencyDollarIcon,
  LightBulbIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";

interface HaLongSalaryGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SALARY_TIERS = [
  {
    role: "IT Support / Helpdesk Khách sạn 5* & Resort",
    location: "Bãi Cháy, Tuần Châu, Hòn Gai",
    range: "10 - 18 triệu VNĐ/tháng",
    bonus: "+ Phí dịch vụ (Service Charge 2 - 5tr) + Ăn ca",
    barPercent: 42,
    skills: ["Opera PMS", "Smile Hotel", "WiFi Mesh", "Khóa từ Vingcard", "VoIP"],
    advice: "Ưu tiên ứng viên có tiếng Anh giao tiếp cơ bản và tinh thần sẵn sàng trực ca kíp / On-call linh hoạt.",
  },
  {
    role: "Chuyên viên CNTT Y tế số / Bệnh viện đa khoa",
    location: "Hạ Long, Bãi Cháy, Cột 5",
    range: "12 - 22 triệu VNĐ/tháng",
    bonus: "+ Phụ cấp ngành y tế + Thưởng quý",
    barPercent: 55,
    skills: ["HIS / LIS / PACS", "Bảo mật y tế", "Active Directory", "Máy in mã vạch"],
    advice: "Hệ thống vận hành 24/7 đòi hỏi sự cẩn trọng cao độ, sao lưu định kỳ và phản ứng tức thì khi có sự cố.",
  },
  {
    role: "Kỹ sư IT & SCADA Tự động hóa Cảng CICT & KCN",
    location: "Cảng Cái Lân, KCN Việt Hưng, KCN Đông Mai",
    range: "16 - 30 triệu VNĐ/tháng",
    bonus: "+ Thưởng năng suất cảng biển + Phụ cấp độc hại",
    barPercent: 75,
    skills: ["Phần mềm cảng TOS", "SCADA / PLC Siemens", "Camera OCR", "Mạng cáp quang"],
    advice: "Môi trường công nghiệp nặng yêu cầu kiến thức vững về thiết bị mạng chịu thời tiết biển và an toàn lao động.",
  },
  {
    role: "Quản trị Hệ thống CNTT & SCADA Ngành Than - Điện",
    location: "Cẩm Phả, Hạ Long, Hoành Bồ",
    range: "16 - 32 triệu VNĐ/tháng",
    bonus: "+ Thưởng an toàn ngành Than + Nghỉ dưỡng năm",
    barPercent: 80,
    skills: ["SCADA trạm điện", "Giám sát mỏ", "Oracle / SQL", "Tường lửa"],
    advice: "Ưu tiên ứng viên tốt nghiệp chuyên ngành CNTT, Tự động hóa hoặc Đo lường điều khiển.",
  },
  {
    role: "Lập trình viên Web / Mobile & Kỹ sư Cloud",
    location: "FPT Telecom, VNPT Quảng Ninh, Remote",
    range: "15 - 35 triệu VNĐ/tháng",
    bonus: "+ Thưởng dự án + Chứng chỉ quốc tế",
    barPercent: 88,
    skills: ["React / Next.js", "Node.js / Python", "Docker / Cloud", "RESTful API"],
    advice: "Nhu cầu chuyển đổi số tại Quảng Ninh mở ra cơ hội lớn cho developer làm việc kết hợp hybrid.",
  },
  {
    role: "Trưởng phòng CNTT / IT Manager Hạ Long",
    location: "Tập đoàn lớn, Khách sạn 5 sao quốc tế",
    range: "28 - 55+ triệu VNĐ/tháng",
    bonus: "+ Xe đưa đón + Thưởng KPI năm + Thẻ VIP",
    barPercent: 100,
    skills: ["Quản trị ngân sách IT", "Tiêu chuẩn ISO 27001", "Quản lý đội ngũ", "Tiếng Anh"],
    advice: "Đòi hỏi kinh nghiệm từ 5 năm trở lên tại các khách sạn 5 sao hoặc tập đoàn hạ tầng du lịch.",
  },
];

export default function HaLongSalaryGuideModal({
  isOpen,
  onClose,
}: HaLongSalaryGuideModalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!isOpen || !mounted) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 md:p-6 overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-3xl rounded-2xl sm:rounded-3xl bg-white shadow-2xl border border-neutral-200 z-10 flex flex-col max-h-[85vh] overflow-hidden animate-fadeIn">
        {/* Fixed Header */}
        <div className="shrink-0 px-4 sm:px-6 py-3.5 sm:py-4 border-b border-neutral-200 bg-white flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
            <div className="flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-neutral-100 text-black border border-neutral-200 text-lg font-bold">
              📊
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="text-base sm:text-lg font-black text-black truncate">
                  Báo Cáo Lương IT Hạ Long 2026
                </h3>
                <span className="text-[10px] bg-neutral-100 text-neutral-800 border border-neutral-300 font-bold px-1.5 py-0.5 rounded-md uppercase shrink-0">
                  Thực tế
                </span>
              </div>
              <p className="text-xs text-neutral-500 truncate mt-0.5">
                Tổng hợp từ khách sạn 5 sao, bệnh viện, cảng biển và KCN Quảng Ninh
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
            title="Đóng"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4 [scrollbar-width:thin] [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-neutral-300 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-neutral-400">
          {/* Quick Highlights Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            <div className="p-3 rounded-2xl bg-neutral-50 border border-neutral-200">
              <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider block">
                Mức lương phổ biến
              </span>
              <p className="text-lg font-black text-black mt-0.5">12 - 25 Triệu</p>
              <p className="text-[11px] text-neutral-600 mt-0.5">Cao hơn 15% mặt bằng lân cận</p>
            </div>
            <div className="p-3 rounded-2xl bg-neutral-50 border border-neutral-200">
              <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider block">
                Đãi ngộ độc quyền
              </span>
              <p className="text-lg font-black text-black mt-0.5">+ Service Charge</p>
              <p className="text-[11px] text-neutral-600 mt-0.5">Khách sạn 5* thưởng thêm 2 - 5tr</p>
            </div>
            <div className="p-3 rounded-2xl bg-neutral-50 border border-neutral-200">
              <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider block">
                Nhu cầu tuyển dụng
              </span>
              <p className="text-lg font-black text-black mt-0.5">Rộng mở &amp; Khát việc</p>
              <p className="text-[11px] text-neutral-600 mt-0.5">Cần nhân lực IT gắn bó lâu dài</p>
            </div>
          </div>

          {/* Detailed Roles Breakdown */}
          <div className="space-y-3">
            <h4 className="text-[11px] font-extrabold text-neutral-700 uppercase tracking-wider flex items-center gap-1.5">
              <CurrencyDollarIcon className="h-3.5 w-3.5 text-black" />
              <span>Thang lương chi tiết theo khối ngành tại Hạ Long:</span>
            </h4>

            <div className="space-y-2.5">
              {SALARY_TIERS.map((tier) => (
                <div
                  key={tier.role}
                  className="p-3.5 rounded-2xl border border-neutral-200 bg-white hover:border-black transition-all space-y-2"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <div>
                      <h5 className="font-bold text-black text-sm">
                        {tier.role}
                      </h5>
                      <p className="text-[11px] text-neutral-500">
                        📍 {tier.location}
                      </p>
                    </div>
                    <div className="sm:text-right">
                      <span className="font-black text-black text-sm sm:text-base block">
                        {tier.range}
                      </span>
                      <span className="text-[10px] text-neutral-600 font-medium block">
                        {tier.bonus}
                      </span>
                    </div>
                  </div>

                  {/* Progress bar visual */}
                  <div className="w-full bg-neutral-100 rounded-full h-1.5 overflow-hidden border border-neutral-200">
                    <div
                      className="h-full rounded-full bg-black"
                      style={{ width: `${tier.barPercent}%` }}
                    />
                  </div>

                  {/* Skills tags */}
                  <div className="flex flex-wrap items-center gap-1 text-[11px]">
                    <span className="text-[10px] font-bold text-neutral-400 uppercase">Kỹ năng:</span>
                    {tier.skills.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded-md bg-neutral-100 text-neutral-800 text-[10px] font-semibold border border-neutral-200"
                      >
                        {s}
                      </span>
                    ))}
                  </div>

                  <p className="text-[11px] text-neutral-700 bg-neutral-50 p-2 rounded-xl border border-neutral-200 flex items-start gap-1.5 leading-snug">
                    <LightBulbIcon className="h-3.5 w-3.5 text-black shrink-0 mt-0.5" />
                    <span><strong>Lời khuyên:</strong> {tier.advice}</span>
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Advice */}
          <div className="p-3 rounded-2xl bg-neutral-50 border border-neutral-200 text-xs text-neutral-800 space-y-1">
            <p className="font-bold text-black text-xs flex items-center gap-1.5">
              <AcademicCapIcon className="h-3.5 w-3.5 text-black" />
              <span>Kinh nghiệm phỏng vấn IT tại Quảng Ninh</span>
            </p>
            <p className="text-[11px] text-neutral-600 leading-relaxed">
              Các doanh nghiệp và khách sạn tại Hạ Long đánh giá rất cao <strong>tính ổn định, định hướng gắn bó lâu dài tại địa phương</strong>, sự chủ động xử lý sự cố ngoài giờ và thái độ phục vụ thân thiện với các bộ phận vận hành.
            </p>
          </div>
        </div>

        {/* Fixed Footer */}
        <div className="shrink-0 px-4 sm:px-6 py-3 border-t border-neutral-200 bg-white flex items-center justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
          >
            Đóng bảng lương
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
