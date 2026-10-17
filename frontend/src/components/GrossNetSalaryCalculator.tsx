"use client";

import React, { useState, useMemo } from "react";
import {
  CurrencyDollarIcon,
  CalculatorIcon,
  InformationCircleIcon,
  ShieldCheckIcon,
  BuildingOffice2Icon,
  UserIcon,
} from "@heroicons/react/24/outline";
import {
  calculateGrossToNet,
  calculateNetToGross,
  SalaryBreakdown,
  REGIONAL_MINIMUM_WAGE,
  BASE_SALARY,
} from "@/lib/salaryCalculator";

interface GrossNetSalaryCalculatorProps {
  initialSalary?: number;
  initialMode?: "gross_to_net" | "net_to_gross";
}

export default function GrossNetSalaryCalculator({
  initialSalary = 15000000,
  initialMode = "gross_to_net",
}: GrossNetSalaryCalculatorProps) {
  const [mode, setMode] = useState<"gross_to_net" | "net_to_gross">(initialMode);
  const [salaryInput, setSalaryInput] = useState<number>(initialSalary);
  const [dependents, setDependents] = useState<number>(0);
  const [region, setRegion] = useState<number>(2); // Default Vùng 2: Hạ Long & Quảng Ninh

  const breakdown: SalaryBreakdown = useMemo(() => {
    if (mode === "gross_to_net") {
      return calculateGrossToNet(salaryInput, dependents, region);
    } else {
      return calculateNetToGross(salaryInput, dependents, region);
    }
  }, [salaryInput, dependents, region, mode]);

  const formatVND = (val: number) => {
    return new Intl.NumberFormat("vi-VN").format(Math.round(val)) + " đ";
  };

  const QUICK_PRESETS = [10000000, 15000000, 20000000, 25000000, 35000000, 50000000];

  return (
    <div className="space-y-4">
      {/* Control Panel */}
      <div className="bg-neutral-50 rounded-2xl p-4 border border-neutral-200 space-y-3.5">
        {/* Toggle Mode */}
        <div className="flex items-center gap-1.5 p-1 bg-white border border-neutral-200 rounded-xl">
          <button
            type="button"
            onClick={() => setMode("gross_to_net")}
            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-bold transition-all ${
              mode === "gross_to_net"
                ? "bg-black text-white shadow-xs"
                : "text-neutral-600 hover:text-black"
            }`}
          >
            Tính Gross ➔ Net (Thực lĩnh)
          </button>
          <button
            type="button"
            onClick={() => setMode("net_to_gross")}
            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-bold transition-all ${
              mode === "net_to_gross"
                ? "bg-black text-white shadow-xs"
                : "text-neutral-600 hover:text-black"
            }`}
          >
            Tính Net ➔ Gross (Lương hợp đồng)
          </button>
        </div>

        {/* Salary Input & Presets */}
        <div>
          <label className="block text-xs font-bold text-neutral-800 mb-1.5 flex items-center justify-between">
            <span>
              {mode === "gross_to_net" ? "Mức lương thỏa thuận (Gross):" : "Mức lương mong muốn thực nhận (Net):"}
            </span>
            <span className="text-black font-extrabold text-sm">
              {formatVND(salaryInput)}
            </span>
          </label>
          <div className="relative">
            <input
              type="number"
              step="500000"
              min="0"
              max="200000000"
              value={salaryInput || ""}
              onChange={(e) => setSalaryInput(Math.max(0, Number(e.target.value) || 0))}
              placeholder="Ví dụ: 15000000"
              className="w-full px-3.5 py-2.5 rounded-xl border border-neutral-300 bg-white font-bold text-sm text-black focus:outline-none focus:ring-2 focus:ring-black"
            />
            <span className="absolute right-3.5 top-2.5 text-xs font-bold text-neutral-400">
              VNĐ/tháng
            </span>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            <span className="text-[11px] text-neutral-500 font-semibold mr-1">Gợi ý nhanh:</span>
            {QUICK_PRESETS.map((amt) => (
              <button
                key={amt}
                type="button"
                onClick={() => setSalaryInput(amt)}
                className={`text-[11px] px-2 py-0.5 rounded-md border font-semibold transition-all ${
                  salaryInput === amt
                    ? "bg-black text-white border-black"
                    : "bg-white text-neutral-700 border-neutral-200 hover:bg-neutral-100"
                }`}
              >
                {amt / 1000000}tr
              </button>
            ))}
          </div>
        </div>

        {/* Region & Dependents row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div>
            <label className="block text-[11px] font-bold text-neutral-700 mb-1">
              Vùng làm việc (Tính trần BHTN):
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border border-neutral-300 bg-white text-xs font-bold text-black focus:outline-none focus:ring-1 focus:ring-black cursor-pointer"
            >
              <option value={2}>📍 Vùng 2 - Hạ Long, Cẩm Phả, Uông Bí, QN (4.41tr)</option>
              <option value={1}>🏢 Vùng 1 - Hà Nội, TP.HCM, Hải Phòng (4.96tr)</option>
              <option value={3}>🌾 Vùng 3 - Các huyện còn lại Quảng Ninh (3.86tr)</option>
              <option value={4}>🏞️ Vùng 4 - Vùng sâu xa (3.45tr)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-bold text-neutral-700 mb-1">
              Số người phụ thuộc (Giảm trừ 4.4tr/người):
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="0"
                max="10"
                value={dependents}
                onChange={(e) => setDependents(Math.max(0, Number(e.target.value) || 0))}
                className="w-20 px-3 py-2 rounded-xl border border-neutral-300 bg-white text-xs font-bold text-black focus:outline-none focus:ring-1 focus:ring-black"
              />
              <span className="text-[11px] text-neutral-500">
                (Giảm trừ {formatVND(dependents * 4400000)})
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Result Banner */}
      <div className="p-4 rounded-2xl bg-black text-white shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <span className="text-xs text-neutral-300 uppercase tracking-wider font-semibold">
            {mode === "gross_to_net" ? "Lương Thực Lĩnh Cầm Về Tay (Net):" : "Mức Lương Hợp Đồng Cần Ký (Gross):"}
          </span>
          <p className="text-2xl sm:text-3xl font-black text-white mt-0.5 tracking-tight">
            {formatVND(mode === "gross_to_net" ? breakdown.net : breakdown.gross)}
          </p>
          <p className="text-[11px] text-neutral-300 mt-1">
            {mode === "gross_to_net"
              ? `Tương đương ${((breakdown.net / (breakdown.gross || 1)) * 100).toFixed(1)}% mức Gross ký hợp đồng`
              : `Bao gồm ${formatVND(breakdown.insuranceEmployee.total)} bảo hiểm và ${formatVND(breakdown.personalIncomeTax)} thuế TNCN`}
          </p>
        </div>
        <div className="sm:text-right border-t sm:border-t-0 pt-2 sm:pt-0 border-neutral-800">
          <span className="text-[11px] text-neutral-400 block font-medium">Chi phí doanh nghiệp trả:</span>
          <span className="text-sm sm:text-base font-bold text-white block">
            {formatVND(breakdown.totalEmployerCost)}
          </span>
          <span className="text-[10px] text-neutral-400">
            (Gross + 21.5% bảo hiểm công ty)
          </span>
        </div>
      </div>

      {/* Detailed 3-Box Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        {/* Box 1: Employee Insurance */}
        <div className="bg-white rounded-xl border border-neutral-200 p-3.5 space-y-2 shadow-2xs">
          <div className="flex items-center gap-1.5 pb-1 border-b border-neutral-100 font-bold text-neutral-900">
            <ShieldCheckIcon className="h-4 w-4 text-black" />
            <span>Bảo hiểm người lao động (10.5%)</span>
          </div>
          <div className="space-y-1.5 text-neutral-600 text-[11px]">
            <div className="flex justify-between">
              <span>BHXH (8%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployee.social)}</strong>
            </div>
            <div className="flex justify-between">
              <span>BHYT (1.5%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployee.health)}</strong>
            </div>
            <div className="flex justify-between">
              <span>BHTN (1%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployee.unemployment)}</strong>
            </div>
            <div className="flex justify-between pt-1 border-t border-neutral-100 font-bold text-black">
              <span>Tổng bảo hiểm trừ:</span>
              <span>{formatVND(breakdown.insuranceEmployee.total)}</span>
            </div>
          </div>
        </div>

        {/* Box 2: Tax Calculation */}
        <div className="bg-white rounded-xl border border-neutral-200 p-3.5 space-y-2 shadow-2xs">
          <div className="flex items-center gap-1.5 pb-1 border-b border-neutral-100 font-bold text-neutral-900">
            <UserIcon className="h-4 w-4 text-black" />
            <span>Thuế thu nhập cá nhân (TNCN)</span>
          </div>
          <div className="space-y-1.5 text-neutral-600 text-[11px]">
            <div className="flex justify-between">
              <span>Thu nhập chịu thuế:</span>
              <strong className="text-black">{formatVND(breakdown.taxableIncome)}</strong>
            </div>
            <div className="flex justify-between">
              <span>Giảm trừ gia cảnh:</span>
              <strong className="text-black">-{formatVND(breakdown.totalDeduction)}</strong>
            </div>
            <div className="flex justify-between">
              <span>Thu nhập tính thuế:</span>
              <strong className="text-black">{formatVND(breakdown.assessableIncome)}</strong>
            </div>
            <div className="flex justify-between pt-1 border-t border-neutral-100 font-bold text-black">
              <span>Thuế TNCN tạm nộp:</span>
              <span>{formatVND(breakdown.personalIncomeTax)}</span>
            </div>
          </div>
        </div>

        {/* Box 3: Employer Cost */}
        <div className="bg-white rounded-xl border border-neutral-200 p-3.5 space-y-2 shadow-2xs">
          <div className="flex items-center gap-1.5 pb-1 border-b border-neutral-100 font-bold text-neutral-900">
            <BuildingOffice2Icon className="h-4 w-4 text-black" />
            <span>Doanh nghiệp đóng thêm (21.5%)</span>
          </div>
          <div className="space-y-1.5 text-neutral-600 text-[11px]">
            <div className="flex justify-between">
              <span>BHXH (17%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployer.social)}</strong>
            </div>
            <div className="flex justify-between">
              <span>BHTNLĐ-BNN (0.5%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployer.accident)}</strong>
            </div>
            <div className="flex justify-between">
              <span>BHYT (3%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployer.health)}</strong>
            </div>
            <div className="flex justify-between">
              <span>BHTN (1%):</span>
              <strong className="text-black">{formatVND(breakdown.insuranceEmployer.unemployment)}</strong>
            </div>
            <div className="flex justify-between pt-1 border-t border-neutral-100 font-bold text-black">
              <span>Tổng bảo hiểm DN:</span>
              <span>{formatVND(breakdown.insuranceEmployer.total)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Legal Reference Note */}
      <div className="p-3 rounded-xl bg-neutral-100 border border-neutral-200 text-[11px] text-neutral-600 flex items-start gap-2 leading-relaxed">
        <InformationCircleIcon className="h-4 w-4 text-black shrink-0 mt-0.5" />
        <span>
          <strong>Căn cứ pháp lý:</strong> Áp dụng mức lương cơ sở <strong>2.340.000đ</strong> (NĐ 73/2024), lương tối thiểu Vùng 2 Quảng Ninh <strong>4.410.000đ</strong> (NĐ 74/2024), giảm trừ bản thân 11.000.000đ và người phụ thuộc 4.400.000đ.
        </span>
      </div>
    </div>
  );
}
