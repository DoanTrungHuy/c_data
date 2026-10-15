"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  SparklesIcon,
  BuildingOffice2Icon,
  ShieldCheckIcon,
  BoltIcon,
  ArrowRightIcon,
  MapPinIcon,
  BanknotesIcon,
  CheckCircleIcon,
  CpuChipIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";
import SkillMatcherModal from "@/components/SkillMatcherModal";
import HaLongSalaryGuideModal from "@/components/HaLongSalaryGuideModal";

interface SectorItem {
  id: string;
  name: string;
  shortName: string;
  icon: string;
  query: string;
  count: number;
  salary: string;
  companies: string[];
  color: string;
  badgeClass: string;
}

const HALONG_SECTORS: SectorItem[] = [
  {
    id: "hotel",
    name: "Khách Sạn & Resort 5 Sao",
    shortName: "🏨 Khách Sạn 5*",
    icon: "🏨",
    query: "Khách Sạn",
    count: 8,
    salary: "11 - 20 Triệu",
    companies: ["Wyndham Legend", "FLC Grand", "Vinpearl Đảo Rều", "Sun World", "Novotel"],
    color: "from-blue-600 to-indigo-600",
    badgeClass: "bg-blue-50 text-blue-700 border-blue-200",
  },
  {
    id: "healthcare",
    name: "Y Tế & Bệnh Viện Số",
    shortName: "🏥 Y Tế & Bệnh Viện",
    icon: "🏥",
    query: "Bệnh Viện",
    count: 3,
    salary: "11 - 19 Triệu",
    companies: ["BV Quốc Tế Vinmec", "BV Bãi Cháy", "BV Đa Khoa Tỉnh"],
    color: "from-emerald-600 to-teal-600",
    badgeClass: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  {
    id: "port",
    name: "Cảng Biển & Nhà Máy KCN",
    shortName: "🚢 Cảng Biển & KCN",
    icon: "🚢",
    query: "Cái Lân",
    count: 4,
    salary: "14 - 25 Triệu",
    companies: ["Cảng CICT Cái Lân", "Dầu CALOFIC", "Đóng Tàu Hạ Long", "Foxconn QN"],
    color: "from-cyan-600 to-blue-700",
    badgeClass: "bg-cyan-50 text-cyan-700 border-cyan-200",
  },
  {
    id: "mining",
    name: "Ngành Than & Tự Động Hóa",
    shortName: "⚡ Than & SCADA",
    icon: "⚡",
    query: "Tự Động Hóa",
    count: 2,
    salary: "15 - 26 Triệu",
    companies: ["Tập Đoàn TKV Vinacomin", "Nhiệt Điện Quảng Ninh"],
    color: "from-amber-600 to-orange-600",
    badgeClass: "bg-amber-50 text-amber-700 border-amber-200",
  },
  {
    id: "telecom",
    name: "Viễn Thông & Cloud Hạ Tầng",
    shortName: "📡 Viễn Thông & Mạng",
    icon: "📡",
    query: "Viễn Thông",
    count: 3,
    salary: "10 - 25 Triệu",
    companies: ["FPT Telecom", "Viettel Quảng Ninh", "VNPT Vinaphone"],
    color: "from-purple-600 to-violet-600",
    badgeClass: "bg-purple-50 text-purple-700 border-purple-200",
  },
  {
    id: "software",
    name: "Lập Trình Web/App & AI",
    shortName: "💻 Lập Trình Phần Mềm",
    icon: "💻",
    query: "Frontend",
    count: 2,
    salary: "14 - 28 Triệu",
    companies: ["FPT Software QN", "Hạ Long Tech Digital"],
    color: "from-rose-600 to-pink-600",
    badgeClass: "bg-rose-50 text-rose-700 border-rose-200",
  },
  {
    id: "banking",
    name: "Ngân Hàng, Sân Bay & POS",
    shortName: "💳 Ngân Hàng & POS",
    icon: "💳",
    query: "Vietcombank",
    count: 3,
    salary: "10 - 25 Triệu",
    companies: ["Vietcombank CN Quảng Ninh", "Go! Hạ Long", "Sân Bay Vân Đồn"],
    color: "from-emerald-700 to-teal-800",
    badgeClass: "bg-teal-50 text-teal-700 border-teal-200",
  },
];

export default function HaLongITHub() {
  const router = useRouter();
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [skillMatcherOpen, setSkillMatcherOpen] = useState(false);
  const [salaryGuideOpen, setSalaryGuideOpen] = useState(false);

  const handleSelectSector = (sector: SectorItem) => {
    setSelectedSector(sector.id);
    router.push(`/jobs?q=${encodeURIComponent(sector.query)}&province=${encodeURIComponent("Quảng Ninh")}`);
  };

  return (
    <div className="relative overflow-hidden rounded-3xl bg-neutral-950 p-6 sm:p-8 lg:p-10 text-white shadow-xl border border-neutral-800">
      {/* Top Header Badge & Radar Status */}
      <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-neutral-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neutral-900 border border-neutral-700 text-neutral-300 text-xs font-bold mb-3">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-40"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
            </span>
            <span>RADAR CNTT CHUYÊN SÂU • TP. HẠ LONG &amp; QUẢNG NINH</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
            Trung Tâm Việc Làm IT Hạ Long
          </h2>
          <p className="mt-1 text-sm text-neutral-400 max-w-2xl leading-relaxed">
            Hệ thống Harvester quét tự động định kỳ 30 phút, cam kết Zero-404, chỉ giữ tin ĐANG TUYỂN DỤNG thực tế từ các tập đoàn và doanh nghiệp hàng đầu.
          </p>
        </div>

        {/* Live Harvester Daemon Badge & AI Tools */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          <button
            type="button"
            onClick={() => setSkillMatcherOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-2xl bg-neutral-900 hover:bg-neutral-800 text-white font-bold text-xs sm:text-sm border border-neutral-700 transition-all active:scale-95 cursor-pointer shadow-sm"
            title="So khớp kỹ năng cá nhân với tất cả việc làm Hạ Long"
          >
            <SparklesIcon className="h-4 w-4 text-white" />
            <span>AI So Khớp CV</span>
          </button>

          <button
            type="button"
            onClick={() => setSalaryGuideOpen(true)}
            className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-2xl bg-neutral-900 hover:bg-neutral-800 text-white font-bold text-xs sm:text-sm border border-neutral-700 transition-all active:scale-95 cursor-pointer shadow-sm"
            title="Xem báo cáo mức lương IT chi tiết tại TP. Hạ Long"
          >
            <ChartBarIcon className="h-4 w-4 text-white" />
            <span>Bảng Lương IT</span>
          </button>

          <Link
            href="/jobs?province=Quảng Ninh"
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-2xl bg-white text-black hover:bg-neutral-200 font-bold text-xs sm:text-sm active:scale-95 transition-all shadow-md"
          >
            <span>Tất cả việc làm</span>
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* 4 Quick Stat Highlights */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 my-6">
        <div className="p-3.5 rounded-2xl bg-neutral-900 border border-neutral-800">
          <div className="text-xs text-neutral-400 flex items-center gap-1">
            <CpuChipIcon className="h-4 w-4 text-white" />
            <span>Vị trí CNTT tuyển gấp</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-white mt-1">25+ Việc làm</div>
          <div className="text-[11px] text-neutral-400 font-medium mt-0.5">100% Đang mở đơn</div>
        </div>

        <div className="p-3.5 rounded-2xl bg-neutral-900 border border-neutral-800">
          <div className="text-xs text-neutral-400 flex items-center gap-1">
            <BanknotesIcon className="h-4 w-4 text-white" />
            <span>Mức lương bình quân</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-white mt-1">14 - 26 Tr/th</div>
          <div className="text-[11px] text-neutral-400 mt-0.5">Thưởng Service Charge</div>
        </div>

        <div className="p-3.5 rounded-2xl bg-neutral-900 border border-neutral-800">
          <div className="text-xs text-neutral-400 flex items-center gap-1">
            <BuildingOffice2Icon className="h-4 w-4 text-white" />
            <span>Doanh nghiệp đối tác</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-white mt-1">18 Tập đoàn lớn</div>
          <div className="text-[11px] text-neutral-400 mt-0.5">Wyndham, Vinmec, CICT, TKV</div>
        </div>

        <div className="p-3.5 rounded-2xl bg-neutral-900 border border-neutral-800">
          <div className="text-xs text-neutral-400 flex items-center gap-1">
            <BoltIcon className="h-4 w-4 text-white" />
            <span>Chu kỳ Harvester</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-white mt-1">Mỗi 30 Phút</div>
          <div className="text-[11px] text-neutral-400 mt-0.5">Tự động quét &amp; đối soát</div>
        </div>
      </div>

      {/* 7 Special IT Sectors in Ha Long (Interactive Pills Grid) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">
            Lọc theo 7 nhóm chuyên ngành CNTT trọng điểm tại Hạ Long:
          </span>
          <span className="text-xs text-neutral-400 hidden sm:inline">
            Bấm chọn để lọc việc làm tức thì
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {HALONG_SECTORS.map((sector) => (
            <button
              key={sector.id}
              type="button"
              onClick={() => handleSelectSector(sector)}
              className="group text-left p-4 rounded-2xl bg-neutral-900 hover:bg-neutral-850 border border-neutral-800 hover:border-neutral-500 transition-all duration-200 cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl">{sector.icon}</span>
                  <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-300 border border-neutral-700">
                    {sector.count} việc
                  </span>
                </div>
                <h3 className="font-bold text-sm text-white mt-2 group-hover:underline transition-colors">
                  {sector.name}
                </h3>
                <p className="text-xs text-neutral-400 mt-1 line-clamp-1">
                  {sector.companies.join(", ")}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-neutral-800 flex items-center justify-between text-xs font-semibold">
                <span className="text-white font-bold">{sector.salary}</span>
                <span className="text-neutral-400 group-hover:text-white group-hover:translate-x-1 transition-transform">
                  →
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Quick Search Tags */}
      <div className="mt-6 pt-5 border-t border-neutral-800 flex flex-wrap items-center gap-2 text-xs">
        <span className="text-neutral-400 font-semibold flex items-center gap-1">
          <MapPinIcon className="h-3.5 w-3.5 text-neutral-300" />
          Khu vực hot:
        </span>
        {[
          { label: "Bãi Cháy (Resort/Khách sạn)", query: "Bãi Cháy" },
          { label: "Cái Lân (Cảng biển / KCN)", query: "Cái Lân" },
          { label: "Hòn Gai (Ngân hàng / BV Đa khoa)", query: "Hồng Gai" },
          { label: "Bạch Đằng (FPT / Viễn thông)", query: "Bạch Đằng" },
          { label: "Tuần Châu (Du thuyền 5 Sao)", query: "Tuần Châu" },
          { label: "Vân Đồn (Sân bay Quốc tế)", query: "Vân Đồn" },
        ].map((area) => (
          <Link
            key={area.label}
            href={`/jobs?q=${encodeURIComponent(area.query)}&province=${encodeURIComponent("Quảng Ninh")}`}
            className="px-2.5 py-1 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white border border-neutral-800 transition-colors"
          >
            {area.label}
          </Link>
        ))}
      </div>

      <SkillMatcherModal
        isOpen={skillMatcherOpen}
        onClose={() => setSkillMatcherOpen(false)}
      />
      <HaLongSalaryGuideModal
        isOpen={salaryGuideOpen}
        onClose={() => setSalaryGuideOpen(false)}
      />
    </div>
  );
}
