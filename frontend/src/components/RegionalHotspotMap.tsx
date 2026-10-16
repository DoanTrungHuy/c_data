"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  MapPinIcon,
  BuildingOffice2Icon,
  ArrowRightIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  CheckBadgeIcon,
} from "@heroicons/react/24/outline";

export interface HotspotZone {
  id: string;
  name: string;
  subTitle: string;
  icon: string;
  filterParam: string;
  jobCountText: string;
  avgSalaryText: string;
  keyEmployers: string[];
  advantages: string[];
  badgeColor: string;
}

export const HOTSPOT_ZONES: HotspotZone[] = [
  {
    id: "bai-chay",
    name: "Cụm Bãi Cháy (Du Lịch & Khách Sạn 5 Sao)",
    subTitle: "Trung tâm du lịch ven bờ Vịnh Hạ Long",
    icon: "🏖️",
    filterParam: "Bãi Cháy",
    jobCountText: "65+ Vị trí",
    avgSalaryText: "12 - 25 Triệu",
    keyEmployers: ["Wyndham Legend", "Novotel Ha Long", "Sun World Complex", "FLC Grand"],
    advantages: ["Phụ cấp buồng phòng / ca", "Môi trường quốc tế 5 sao", "Thưởng mùa vụ du lịch"],
    badgeColor: "bg-neutral-100 text-black border-neutral-300",
  },
  {
    id: "cai-lan",
    name: "KCN Cái Lân & Cảng Biển CICT",
    subTitle: "Công nghiệp nặng, Cảng container & Lắp ráp công nghệ",
    icon: "🚢",
    filterParam: "Cái Lân",
    jobCountText: "48+ Vị trí",
    avgSalaryText: "14 - 35 Triệu",
    keyEmployers: ["Cảng CICT", "CALOFIC Dầu Thực Vật", "Foxconn Quảng Ninh", "Đóng tàu Hạ Long"],
    advantages: ["Hệ số phụ cấp cảng biển", "Bảo hiểm PVI cao cấp", "Đưa đón xe công ty"],
    badgeColor: "bg-neutral-100 text-black border-neutral-300",
  },
  {
    id: "hon-gai",
    name: "Hòn Gai & Cột 5 (Tài Chính - Y Tế)",
    subTitle: "Trung tâm hành chính tỉnh, Ngân hàng & Bệnh viện",
    icon: "🏛️",
    filterParam: "Hòn Gai",
    jobCountText: "52+ Vị trí",
    avgSalaryText: "13 - 30 Triệu",
    keyEmployers: ["Vietcombank Quảng Ninh", "Bệnh Viện Đa Khoa Tỉnh", "Vinmec Hạ Long", "MB Bank"],
    advantages: ["Môi trường hành chính văn phòng", "Chế độ phúc lợi bền vững", "Giờ giấc ổn định"],
    badgeColor: "bg-neutral-100 text-black border-neutral-300",
  },
  {
    id: "cam-pha",
    name: "Cẩm Phả & Quang Hanh (Khai Khoáng & Khoáng Nóng)",
    subTitle: "Tập đoàn TKV mỏ than, Nhiệt điện & Yoko Onsen",
    icon: "⛏️",
    filterParam: "Cẩm Phả",
    jobCountText: "40+ Vị trí",
    avgSalaryText: "15 - 40 Triệu",
    keyEmployers: ["Tập Đoàn Than TKV", "Yoko Onsen Quang Hanh", "Nhiệt Điện Quảng Ninh", "Đèo Nai"],
    advantages: ["Lương thưởng mỏ than hấp dẫn", "Ăn ca miễn phí", "Nghỉ dưỡng khoáng nóng"],
    badgeColor: "bg-neutral-100 text-black border-neutral-300",
  },
  {
    id: "van-don",
    name: "Khu Kinh Tế Sân Bay Vân Đồn",
    subTitle: "Hàng không, Logistics & Siêu đô thị nghỉ dưỡng",
    icon: "✈️",
    filterParam: "Vân Đồn",
    jobCountText: "25+ Vị trí",
    avgSalaryText: "14 - 35 Triệu",
    keyEmployers: ["Sân Bay Quốc Tế Vân Đồn", "Sun Group Vân Đồn", "Cảng Cái Rồng", "Logistics Vân Đồn"],
    advantages: ["Môi trường hàng không quốc tế", "Ký túc xá nhân viên tiện nghi", "Đặc khu kinh tế tương lai"],
    badgeColor: "bg-neutral-100 text-black border-neutral-300",
  },
  {
    id: "quang-yen",
    name: "KCN Amata Sông Khoai & Quảng Yên",
    subTitle: "Cứ điểm sản xuất điện tử FDI công nghệ cao",
    icon: "🏭",
    filterParam: "Quảng Yên",
    jobCountText: "30+ Vị trí",
    avgSalaryText: "11 - 28 Triệu",
    keyEmployers: ["Tập Đoàn Amata", "KCN Đông Mai", "Jinko Solar", "Yaskawa Electric"],
    advantages: ["Chuyên gia nước ngoài đào tạo", "Cơ hội thăng tiến quản lý", "Môi trường sản xuất sạch"],
    badgeColor: "bg-neutral-100 text-black border-neutral-300",
  },
];

export default function RegionalHotspotMap() {
  const router = useRouter();
  const [activeZoneId, setActiveZoneId] = useState<string>("bai-chay");

  const activeZone = HOTSPOT_ZONES.find((z) => z.id === activeZoneId) || HOTSPOT_ZONES[0];

  const handleSelectZone = (zone: HotspotZone) => {
    setActiveZoneId(zone.id);
  };

  const handleFilterNow = (zone: HotspotZone) => {
    router.push(`/jobs?q=${encodeURIComponent(zone.filterParam)}&province=Qu%E1%BA%A3ng+Ninh`);
  };

  return (
    <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white text-lg font-black shadow-xs">
            🗺️
          </div>
          <div>
            <h2 className="text-base sm:text-xl font-black text-black flex items-center gap-2">
              <span>Bản Đồ Tuyển Dụng Địa Bàn Số</span>
              <span className="text-[10px] bg-neutral-100 text-black border border-neutral-300 font-bold px-2 py-0.5 rounded-full uppercase">
                6 Phân Khu
              </span>
            </h2>
            <p className="text-xs text-neutral-600 mt-0.5">
              Khám phá cụm việc làm theo tọa độ kinh tế trọng điểm tại TP. Hạ Long & Tỉnh Quảng Ninh
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => handleFilterNow(activeZone)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer self-start sm:self-auto"
        >
          <span>Xem việc tại {activeZone.filterParam}</span>
          <ArrowRightIcon className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Grid of 6 Zones Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {HOTSPOT_ZONES.map((zone) => {
          const isSelected = activeZoneId === zone.id;
          return (
            <button
              key={zone.id}
              type="button"
              onClick={() => handleSelectZone(zone)}
              className={`p-3 rounded-2xl border text-left transition-all duration-200 cursor-pointer flex flex-col justify-between h-24 ${
                isSelected
                  ? "bg-black text-white border-black shadow-md scale-[1.02]"
                  : "bg-neutral-50 hover:bg-neutral-100 text-neutral-800 border-neutral-200"
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <span className="text-xl">{zone.icon}</span>
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.2 rounded-md ${
                    isSelected ? "bg-white text-black" : "bg-neutral-200 text-black"
                  }`}
                >
                  {zone.jobCountText.split(" ")[0]}
                </span>
              </div>
              <div>
                <span className="font-bold text-xs block leading-tight line-clamp-1">
                  {zone.filterParam}
                </span>
                <span
                  className={`text-[10px] truncate block ${
                    isSelected ? "text-neutral-300" : "text-neutral-500"
                  }`}
                >
                  {zone.avgSalaryText}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Zone Deep Dive Card */}
      <div className="p-4 sm:p-6 rounded-2xl bg-neutral-50 border border-neutral-200 space-y-4 animate-fadeIn">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-3.5">
          <div className="flex items-center gap-3">
            <span className="text-3xl shrink-0">{activeZone.icon}</span>
            <div>
              <h3 className="font-black text-black text-base sm:text-lg">
                {activeZone.name}
              </h3>
              <p className="text-xs text-neutral-600 mt-0.5">
                {activeZone.subTitle}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="bg-white px-3 py-1.5 rounded-xl border border-neutral-200 font-medium">
              <span className="text-neutral-500 text-[10px] block uppercase font-bold">Số lượng tuyển dụng:</span>
              <strong className="text-black text-sm">{activeZone.jobCountText}</strong>
            </div>
            <div className="bg-white px-3 py-1.5 rounded-xl border border-neutral-200 font-medium">
              <span className="text-neutral-500 text-[10px] block uppercase font-bold">Khung lương phổ biến:</span>
              <strong className="text-black text-sm">{activeZone.avgSalaryText}</strong>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Key Employers */}
          <div className="bg-white p-3.5 sm:p-4 rounded-xl sm:rounded-2xl border border-neutral-200 space-y-2">
            <span className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider block flex items-center gap-1.5">
              <BuildingOffice2Icon className="h-4 w-4 text-black" />
              <span>Doanh nghiệp & Tập đoàn tuyển dụng trọng điểm:</span>
            </span>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {activeZone.keyEmployers.map((emp) => (
                <span
                  key={emp}
                  className="px-2.5 py-1 rounded-lg bg-neutral-100 text-black border border-neutral-300 font-bold text-xs"
                >
                  🏢 {emp}
                </span>
              ))}
            </div>
          </div>

          {/* Advantages */}
          <div className="bg-white p-3.5 sm:p-4 rounded-xl sm:rounded-2xl border border-neutral-200 space-y-2">
            <span className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider block flex items-center gap-1.5">
              <SparklesIcon className="h-4 w-4 text-black" />
              <span>Đặc thù đãi ngộ & Lợi thế làm việc tại khu vực:</span>
            </span>
            <ul className="space-y-1 text-neutral-700 text-[11px]">
              {activeZone.advantages.map((adv, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-black inline-block" />
                  <span>{adv}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="flex items-center justify-between pt-1">
          <p className="text-[11px] text-neutral-500 italic">
            💡 Dữ liệu việc làm các phân khu được cập nhật tự động định kỳ 30 phút qua hệ thống đối soát Zero-404.
          </p>
          <button
            type="button"
            onClick={() => handleFilterNow(activeZone)}
            className="text-xs font-bold text-black hover:underline flex items-center gap-1 cursor-pointer"
          >
            <span>Lọc toàn bộ danh sách {activeZone.filterParam} →</span>
          </button>
        </div>
      </div>
    </div>
  );
}
