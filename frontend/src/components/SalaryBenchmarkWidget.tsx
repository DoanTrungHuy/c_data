"use client";

import React, { useMemo } from "react";
import { Job } from "@/types/job";
import {
  CurrencyDollarIcon,
  ChartBarIcon,
  HomeModernIcon,
  ArrowTrendingUpIcon,
  CheckBadgeIcon,
} from "@heroicons/react/24/outline";

interface SalaryBenchmarkWidgetProps {
  job: Job;
}

export default function SalaryBenchmarkWidget({ job }: SalaryBenchmarkWidgetProps) {
  const benchmarkData = useMemo(() => {
    const min = job.salary_min || 0;
    const max = job.salary_max || 0;
    const loc = job.location_province || "Quảng Ninh";

    // Estimated mid point
    let midSalary = 12; // default 12m
    if (min > 0 && max > 0) {
      midSalary = Math.round((min + max) / 2 / 1000000);
    } else if (min > 0) {
      midSalary = Math.round(min / 1000000);
    } else if (max > 0) {
      midSalary = Math.round(max / 1000000);
    }

    // Benchmark comparison against Ha Long average (11.5M VNĐ)
    const halongAvg = 11.5;
    const diffPct = Math.round(((midSalary - halongAvg) / halongAvg) * 100);

    let percentile = 50;
    let tierText = "Mức lương tiêu chuẩn thị trường";
    if (midSalary >= 30) {
      percentile = 95;
      tierText = "Top 5% thu nhập cao nhất tại Quảng Ninh";
    } else if (midSalary >= 20) {
      percentile = 85;
      tierText = "Top 15% thu nhập hấp dẫn tại địa bàn";
    } else if (midSalary >= 15) {
      percentile = 70;
      tierText = "Top 30% mức lương cạnh tranh tại Hạ Long";
    } else if (midSalary >= 12) {
      percentile = 55;
      tierText = "Cao hơn mức trung bình khu vực (+15%)";
    } else {
      percentile = 40;
      tierText = "Mức lương khởi điểm phù hợp năng lực";
    }

    // Estimated living cost savings vs Hanoi/HCMC (Rent ~2.5M vs ~5.5M)
    const estimatedRentSavings = 3.0; // 3 million/month
    const yearlySavings = Math.round(estimatedRentSavings * 12);

    return {
      midSalary,
      diffPct,
      percentile,
      tierText,
      yearlySavings,
      salaryDisplay: job.salary_text || `${min > 0 ? min / 1000000 : 10} - ${max > 0 ? max / 1000000 : 18} triệu VNĐ`,
    };
  }, [job]);

  return (
    <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-5">
      {/* Title */}
      <div className="flex items-center justify-between border-b border-neutral-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white text-lg font-black shadow-xs">
            📊
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-black text-black flex items-center gap-2">
              <span>Định Vị Thu Nhập & So Sánh Thị Trường</span>
              <span className="text-[10px] bg-neutral-100 text-black border border-neutral-300 font-bold px-2 py-0.5 rounded-full">
                Hạ Long 2026
              </span>
            </h3>
            <p className="text-xs text-neutral-600 mt-0.5">
              Phân tích tương quan mức lương và chi phí sinh hoạt thực tế tại địa phương
            </p>
          </div>
        </div>

        <span className="shrink-0 hidden sm:inline-block px-3 py-1 rounded-full bg-neutral-100 border border-neutral-300 text-black text-xs font-bold">
          {benchmarkData.tierText}
        </span>
      </div>

      {/* Visual Benchmark Gauge */}
      <div className="p-4 sm:p-5 rounded-2xl bg-neutral-50 border border-neutral-200 space-y-3">
        <div className="flex items-center justify-between text-xs font-bold text-black">
          <span>Khung thu nhập công bố:</span>
          <span className="text-sm sm:text-base font-black text-black">
            {benchmarkData.salaryDisplay}
          </span>
        </div>

        {/* Progress Bar Gauge */}
        <div className="space-y-1.5">
          <div className="h-3 w-full bg-neutral-200 rounded-full overflow-hidden p-0.5 flex items-center">
            <div
              className="h-full bg-black rounded-full transition-all duration-700 ease-out"
              style={{ width: `${Math.min(100, Math.max(15, benchmarkData.percentile))}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-neutral-500 font-medium">
            <span>Khởi điểm (7 - 9M)</span>
            <span>Mặt bằng chung (11.5M)</span>
            <span>Chuyên gia / Quản lý (25M+)</span>
          </div>
        </div>

        <div className="pt-1 flex items-center gap-2 text-xs font-semibold text-neutral-800">
          <ArrowTrendingUpIcon className="h-4 w-4 text-black shrink-0" />
          <span>
            {benchmarkData.diffPct >= 0
              ? `Vị trí này có mức thu nhập cao hơn khoảng +${benchmarkData.diffPct}% so với mặt bằng trung bình tại địa phương.`
              : `Mức thu nhập tương đương mức chuẩn ngành, phù hợp tích lũy kinh nghiệm ban đầu.`}
          </span>
        </div>
      </div>

      {/* Local Advantage Cards: 3 Column Metric */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-white border border-neutral-200 space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-neutral-500 text-[11px] uppercase tracking-wider">
            <HomeModernIcon className="h-4 w-4 text-black" />
            <span>Chi phí nhà ở:</span>
          </div>
          <span className="text-sm font-black text-black block">
            ~2.5 - 3.5 Triệu / tháng
          </span>
          <p className="text-[11px] text-neutral-600 leading-relaxed">
            Thuê căn hộ/phòng tiện nghi tại Hạ Long tiết kiệm 45% so với Cầu Giấy / Q.1.
          </p>
        </div>

        <div className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-white border border-neutral-200 space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-neutral-500 text-[11px] uppercase tracking-wider">
            <span>⏱️</span>
            <span>Thời gian di chuyển:</span>
          </div>
          <span className="text-sm font-black text-black block">
            10 - 15 Phút đi lại
          </span>
          <p className="text-[11px] text-neutral-600 leading-relaxed">
            Hạ tầng thông thoáng, ven bờ biển, không tắc đường giờ cao điểm, giảm áp lực di chuyển.
          </p>
        </div>

        <div className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-white border border-neutral-200 space-y-1">
          <div className="flex items-center gap-1.5 font-bold text-neutral-500 text-[11px] uppercase tracking-wider">
            <span>💰</span>
            <span>Tiết kiệm ròng ước tính:</span>
          </div>
          <span className="text-sm font-black text-black block">
            +{benchmarkData.yearlySavings} Triệu / năm
          </span>
          <p className="text-[11px] text-neutral-600 leading-relaxed">
            Khoản dôi dư tài chính tích lũy được nhờ chi phí sinh hoạt hợp lý tại Quảng Ninh.
          </p>
        </div>
      </div>
    </div>
  );
}
