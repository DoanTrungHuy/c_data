"use client";

import React, { useState } from "react";
import {
  XMarkIcon,
  CurrencyDollarIcon,
  BuildingOffice2Icon,
  CheckBadgeIcon,
  SparklesIcon,
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
    bonus: "+ Phí dịch vụ (Service Charge 2 - 5tr) + Bao ăn ca + Đồng phục",
    barPercent: 42,
    color: "from-blue-500 to-cyan-500",
    skills: ["Opera PMS", "Smile Hotel", "WiFi Mesh (Aruba/Ruckus)", "Khóa từ Vingcard", "Tổng đài VoIP"],
    advice: "Ưu tiên ứng viên có tiếng Anh giao tiếp cơ bản và tinh thần sẵn sàng trực ca kíp / On-call linh hoạt.",
  },
  {
    role: "Chuyên viên CNTT Y tế số / Bệnh viện đa khoa",
    location: "Hạ Long, Bãi Cháy, Cột 5",
    range: "12 - 22 triệu VNĐ/tháng",
    bonus: "+ Phụ cấp ngành y tế + Thưởng quý theo ca khám chữa bệnh",
    barPercent: 55,
    color: "from-teal-500 to-emerald-500",
    skills: ["Phần mềm HIS / LIS / PACS", "Bảo mật dữ liệu y tế HL7", "Active Directory", "Máy in mã vạch"],
    advice: "Hệ thống vận hành 24/7 đòi hỏi sự cẩn trọng cao độ, sao lưu định kỳ và phản ứng tức thì khi có sự cố.",
  },
  {
    role: "Kỹ sư IT & SCADA Tự động hóa Cảng CICT & KCN",
    location: "Cảng Cái Lân, KCN Việt Hưng, KCN Đông Mai",
    range: "16 - 30 triệu VNĐ/tháng",
    bonus: "+ Thưởng năng suất bốc dỡ container + Phụ cấp độc hại công nghiệp",
    barPercent: 75,
    color: "from-amber-500 to-orange-500",
    skills: ["Hệ thống điều hành cảng TOS", "SCADA / PLC Siemens", "Camera OCR biển số", "Mạng cáp quang"],
    advice: "Môi trường công nghiệp nặng yêu cầu kiến thức vững về thiết bị mạng chịu thời tiết biển và an toàn lao động.",
  },
  {
    role: "Quản trị Hệ thống CNTT & SCADA Ngành Than - Điện",
    location: "Cẩm Phả, Hạ Long, Hoành Bồ",
    range: "16 - 32 triệu VNĐ/tháng",
    bonus: "+ Thưởng an toàn lao động ngành Than + Chế độ nghỉ dưỡng hàng năm",
    barPercent: 80,
    color: "from-indigo-500 to-purple-500",
    skills: ["SCADA trạm điện", "Hệ thống giám sát trắc địa", "Cơ sở dữ liệu Oracle/SQL", "Tường lửa"],
    advice: "Ưu tiên ứng viên tốt nghiệp chuyên ngành CNTT, Tự động hóa hoặc Đo lường điều khiển.",
  },
  {
    role: "Lập trình viên Web / Mobile & Kỹ sư Cloud",
    location: "FPT Telecom, VNPT Quảng Ninh, Remote",
    range: "15 - 35 triệu VNĐ/tháng",
    bonus: "+ Thưởng dự án + Chứng chỉ quốc tế + Máy tính MacBook",
    barPercent: 88,
    color: "from-primary-600 to-blue-600",
    skills: ["React / Next.js", "Node.js / Python", "Docker / AWS / GCP", "API RESTful"],
    advice: "Nhu cầu chuyển đổi số tại Quảng Ninh mở ra cơ hội lớn cho developer địa phương làm việc kết hợp hybrid.",
  },
  {
    role: "Trưởng phòng CNTT / IT Manager Hạ Long",
    location: "Tập đoàn lớn, Khách sạn 5 sao quốc tế",
    range: "28 - 55+ triệu VNĐ/tháng",
    bonus: "+ Xe đưa đón + Thưởng KPI năm + Thẻ thành viên VIP tập đoàn",
    barPercent: 100,
    color: "from-rose-500 to-red-600",
    skills: ["Quản trị ngân sách IT", "Tiêu chuẩn an ninh ISO 27001", "Quản lý đội ngũ kỹ sư", "Tiếng Anh thành thạo"],
    advice: "Đòi hỏi kinh nghiệm từ 5 năm trở lên tại các khách sạn 5 sao hoặc tập đoàn hạ tầng du lịch.",
  },
];

export default function HaLongSalaryGuideModal({
  isOpen,
  onClose,
}: HaLongSalaryGuideModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-4xl rounded-3xl bg-white shadow-2xl border border-slate-200 p-6 sm:p-8 z-10 space-y-6 max-h-[92vh] overflow-y-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-md shadow-emerald-600/20 text-xl font-bold">
              📊
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-black text-slate-900 flex items-center gap-2">
                <span>Báo Cáo Mức Lương & Thang Bậc IT Tại TP. Hạ Long</span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full uppercase">
                  Dữ Liệu Khảo Sát 2026
                </span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Dựa trên tổng hợp thực tế từ các doanh nghiệp, khách sạn 5 sao, bệnh viện và cảng biển tại Quảng Ninh.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Quick Highlights Summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-4 rounded-2xl bg-blue-50/70 border border-blue-200/80">
            <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
              Mức lương IT phổ biến
            </span>
            <p className="text-xl font-black text-blue-900 mt-1">12 - 25 Triệu</p>
            <p className="text-xs text-blue-700 mt-0.5">Cao hơn 15% so với mức trung bình các tỉnh lân cận</p>
          </div>
          <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200/80">
            <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider block">
              Đãi ngộ độc quyền Hạ Long
            </span>
            <p className="text-xl font-black text-emerald-900 mt-1">+ Service Charge</p>
            <p className="text-xs text-emerald-700 mt-0.5">Các khách sạn 5* thưởng thêm 2 - 5tr/tháng phí phục vụ</p>
          </div>
          <div className="p-4 rounded-2xl bg-purple-50/70 border border-purple-200/80">
            <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider block">
              Tỷ lệ cạnh tranh
            </span>
            <p className="text-xl font-black text-purple-900 mt-1">Cực kỳ rộng mở</p>
            <p className="text-xs text-purple-700 mt-0.5">Khát nhân lực IT trực tiếp có kinh nghiệm vận hành thực tế</p>
          </div>
        </div>

        {/* Detailed Roles Breakdown */}
        <div className="space-y-4 pt-2">
          <h4 className="text-xs font-extrabold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
            <CurrencyDollarIcon className="h-4 w-4 text-emerald-600" />
            <span>Chi tiết thang lương theo từng khối ngành nghề tại Hạ Long:</span>
          </h4>

          <div className="space-y-3.5">
            {SALARY_TIERS.map((tier) => (
              <div
                key={tier.role}
                className="p-4 sm:p-5 rounded-2xl border border-slate-200/90 bg-white hover:border-primary-300 hover:shadow-xs transition-all space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h5 className="font-extrabold text-slate-900 text-sm sm:text-base flex items-center gap-2">
                      <span>{tier.role}</span>
                    </h5>
                    <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1.5">
                      <span>📍 Khu vực: {tier.location}</span>
                    </p>
                  </div>
                  <div className="sm:text-right">
                    <span className="font-black text-emerald-700 text-base sm:text-lg block">
                      {tier.range}
                    </span>
                    <span className="text-[11px] text-emerald-600 font-semibold block">
                      {tier.bonus}
                    </span>
                  </div>
                </div>

                {/* Progress bar visual */}
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${tier.color}`}
                    style={{ width: `${tier.barPercent}%` }}
                  />
                </div>

                {/* Skills tags & Advice */}
                <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Kỹ năng cốt lõi:</span>
                    {tier.skills.map((s) => (
                      <span
                        key={s}
                        className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-semibold"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
                <p className="text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-200/70 italic flex items-start gap-1.5">
                  <LightBulbIcon className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                  <span><strong>Lời khuyên ứng tuyển:</strong> {tier.advice}</span>
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Advice */}
        <div className="p-4 rounded-2xl bg-gradient-to-r from-primary-50 via-blue-50 to-indigo-50 border border-primary-200 text-xs text-slate-700 space-y-1.5 leading-relaxed">
          <p className="font-black text-primary-900 text-sm flex items-center gap-1.5">
            <AcademicCapIcon className="h-4 w-4 text-primary-600" />
            <span>Kinh nghiệm phỏng vấn IT tại Quảng Ninh</span>
          </p>
          <p>
            Các doanh nghiệp và khách sạn tại Hạ Long đánh giá rất cao <strong>tính ổn định, định hướng gắn bó lâu dài tại địa phương</strong>, sự chủ động xử lý sự cố ngoài giờ và thái độ phục vụ thân thiện với các bộ phận vận hành.
          </p>
        </div>
      </div>
    </div>
  );
}
