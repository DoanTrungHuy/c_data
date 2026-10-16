"use client";

import React, { useMemo } from "react";
import { Job } from "@/types/job";
import {
  ArrowTrendingUpIcon,
  AcademicCapIcon,
  SparklesIcon,
  CheckCircleIcon,
  FlagIcon,
} from "@heroicons/react/24/outline";

interface CareerPathRoadmapProps {
  job: Job;
}

export default function CareerPathRoadmap({ job }: CareerPathRoadmapProps) {
  const careerData = useMemo(() => {
    const title = job.title || "Vị trí tuyển dụng";
    const category = (job.category || "").toLowerCase();
    const minSalary = job.salary_min ? Math.round(job.salary_min / 1000000) : 12;
    const maxSalary = job.salary_max ? Math.round(job.salary_max / 1000000) : 18;

    let certs: string[] = ["Chứng chỉ nghiệp vụ chuyên ngành", "Tiếng Anh giao tiếp TOEIC / IELTS", "Kỹ năng quản trị thời gian"];
    let phase1Title = `Chuyên viên ${title} (Nắm vững vận hành)`;
    let phase2Title = `Senior ${title} / Trưởng nhóm chuyên môn`;
    let phase3Title = `Trưởng bộ phận / Quản lý chuyên môn cao cấp`;

    if (category.includes("it") || category.includes("công nghệ") || title.toLowerCase().includes("it")) {
      certs = ["Chứng chỉ AWS Certified Solutions Architect", "Cisco CCNA / CCNP Quản trị mạng", "ITIL v4 Service Management"];
      phase1Title = `${title} (L1 - L2 Operations)`;
      phase2Title = `Senior Engineer / System Lead`;
      phase3Title = `IT Manager / Head of Infrastructure`;
    } else if (category.includes("kế toán") || title.toLowerCase().includes("kế toán")) {
      certs = ["Chứng chỉ Kế toán trưởng Bộ Tài Chính", "Chứng chỉ CPA Việt Nam / ACCA", "Phần mềm MISA / FAST / SAP ERP"];
      phase1Title = `${title} thực chiến`;
      phase2Title = `Kế toán trưởng / Kiểm soát viên tài chính`;
      phase3Title = `Giám đốc Tài chính (CFO) / Kế toán trưởng Tập đoàn`;
    } else if (category.includes("khách sạn") || category.includes("du lịch") || title.toLowerCase().includes("lễ tân")) {
      certs = ["Chứng chỉ Quản trị Tiền sảnh Quốc tế (FOM)", "Ngoại ngữ Tiếng Anh / Tiếng Trung Du Lịch", "Chứng chỉ Quản lý Khách sạn 5 sao"];
      phase1Title = `Nhân viên chuyên nghiệp ${title}`;
      phase2Title = `Giám sát sảnh (Front Office Supervisor)`;
      phase3Title = `Trưởng bộ phận Lưu trú (Front Office Manager)`;
    }

    return {
      certs,
      phases: [
        {
          stage: "Giai đoạn 1",
          timeframe: "0 - 18 Tháng đầu",
          title: phase1Title,
          salaryRange: `${minSalary} - ${maxSalary} Triệu VNĐ`,
          goal: "Nắm vững toàn diện quy trình làm việc, hoàn thành 100% KPI được giao và hòa nhập văn hóa doanh nghiệp.",
          milestones: [
            "Làm chủ hệ thống và công cụ tác nghiệp hàng ngày",
            "Xử lý độc lập các sự cố thường nhật không cần giám sát",
            "Nhận đánh giá tốt trong kỳ thử việc và soát xét định kỳ",
          ],
        },
        {
          stage: "Giai đoạn 2",
          timeframe: "Năm 2 - 3",
          title: phase2Title,
          salaryRange: `${Math.round(maxSalary * 1.35)} - ${Math.round(maxSalary * 1.8)} Triệu VNĐ`,
          goal: "Chủ trì các dự án quan trọng, kèm cặp nhân sự mới và đề xuất cải tiến quy trình nâng cao hiệu suất.",
          milestones: [
            "Đảm nhận nhiệm vụ phức tạp đòi hỏi độ chính xác cao",
            "Đóng vai trò Mentor hướng dẫn nhân sự cấp dưới",
            "Tăng trưởng thu nhập +40% - +60% so với khởi điểm",
          ],
        },
        {
          stage: "Giai đoạn 3",
          timeframe: "Năm 4 - 5+",
          title: phase3Title,
          salaryRange: `${Math.round(maxSalary * 2.0)} - ${Math.round(maxSalary * 3.0)}+ Triệu VNĐ`,
          goal: "Hoạch định chiến lược cho bộ phận, tham mưu cho ban giám đốc và dẫn dắt đội ngũ lớn.",
          milestones: [
            "Đạt các chứng chỉ cấp chuyên gia hàng đầu trong ngành",
            "Chịu trách nhiệm về ngân sách và kết quả kinh doanh chung",
            "Gia nhập hàng ngũ quản lý chủ chốt của doanh nghiệp",
          ],
        },
      ],
    };
  }, [job]);

  return (
    <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white text-lg font-black shadow-xs">
            🚀
          </div>
          <div>
            <h3 className="text-base sm:text-xl font-black text-black flex items-center gap-2">
              <span>Lộ Trình Thăng Tiến & Phát Triển Sự Nghiệp (5 Năm)</span>
              <span className="text-[10px] bg-neutral-100 text-black border border-neutral-300 font-bold px-2 py-0.5 rounded-full uppercase">
                Career Roadmap
              </span>
            </h3>
            <p className="text-xs text-neutral-600 mt-0.5">
              Dự phóng quỹ đạo thu nhập và các mốc thăng tiến từ vị trí <strong>{job.title}</strong>
            </p>
          </div>
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-neutral-100 border border-neutral-300 text-xs font-bold text-black self-start sm:self-auto">
          <ArrowTrendingUpIcon className="h-4 w-4 text-black" />
          <span>Tăng trưởng x2.5 thu nhập</span>
        </div>
      </div>

      {/* 3-Stage Progression Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 relative">
        {careerData.phases.map((phase, idx) => (
          <div
            key={phase.stage}
            className={`p-4 sm:p-5 rounded-2xl border flex flex-col justify-between space-y-4 ${
              idx === 0
                ? "bg-neutral-50 border-neutral-300"
                : idx === 1
                ? "bg-white border-neutral-300 shadow-2xs"
                : "bg-black text-white border-black shadow-md"
            }`}
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${
                    idx === 2
                      ? "bg-neutral-800 text-white"
                      : "bg-neutral-200 text-black"
                  }`}
                >
                  {phase.stage} • {phase.timeframe}
                </span>
                <span className="text-xs font-black font-mono">
                  {phase.salaryRange}
                </span>
              </div>

              <h4
                className={`font-black text-sm sm:text-base leading-snug ${
                  idx === 2 ? "text-white" : "text-black"
                }`}
              >
                {phase.title}
              </h4>

              <p
                className={`text-xs leading-relaxed ${
                  idx === 2 ? "text-neutral-300" : "text-neutral-600"
                }`}
              >
                {phase.goal}
              </p>
            </div>

            <div
              className={`pt-3 border-t space-y-1.5 text-[11px] ${
                idx === 2 ? "border-neutral-800 text-neutral-300" : "border-neutral-200 text-neutral-700"
              }`}
            >
              <span
                className={`font-bold block text-[10px] uppercase tracking-wider ${
                  idx === 2 ? "text-neutral-400" : "text-neutral-500"
                }`}
              >
                Mục tiêu trọng tâm:
              </span>
              {phase.milestones.map((m, mIdx) => (
                <div key={mIdx} className="flex items-start gap-1.5">
                  <CheckCircleIcon
                    className={`h-3.5 w-3.5 shrink-0 mt-0.5 ${
                      idx === 2 ? "text-white" : "text-black"
                    }`}
                  />
                  <span>{m}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Recommended Certifications Box */}
      <div className="p-4 sm:p-5 rounded-2xl bg-neutral-50 border border-neutral-200 space-y-3">
        <div className="flex items-center gap-2">
          <AcademicCapIcon className="h-5 w-5 text-black" />
          <h4 className="font-bold text-black text-xs sm:text-sm">
            Chứng chỉ & Kỹ năng gia tăng giá trị cạnh tranh cho vị trí này:
          </h4>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {careerData.certs.map((cert) => (
            <div
              key={cert}
              className="p-3 rounded-xl bg-white border border-neutral-200 text-xs font-bold text-black flex items-center gap-2"
            >
              <span>🎓</span>
              <span className="truncate">{cert}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
