"use client";

import React from "react";

interface CompanyOrPlatformLogoProps {
  companyName?: string | null;
  logoUrl?: string | null;
  sourcePlatform?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

export default function CompanyOrPlatformLogo({
  companyName = "",
  logoUrl,
  sourcePlatform = "",
  size = "md",
  className = "",
}: CompanyOrPlatformLogoProps) {
  const comp = (companyName || "").toLowerCase();
  const plat = (sourcePlatform || "").toLowerCase();

  // Size mappings
  const sizeClasses = {
    sm: "w-9 h-9 text-xs rounded-xl",
    md: "w-11 h-11 text-sm rounded-xl",
    lg: "w-14 h-14 text-base rounded-2xl",
    xl: "w-16 h-16 text-lg rounded-2xl",
  }[size];

  // 1. If an actual logo image URL is provided, display it
  if (logoUrl) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center overflow-hidden border border-slate-200 bg-white shadow-2xs ${sizeClasses} ${className}`}
      >
        <img
          src={logoUrl}
          alt={companyName || "Company logo"}
          className="h-full w-full object-contain p-1"
          onError={(e) => {
            // Hide image on error to fallback
            (e.target as HTMLElement).style.display = "none";
          }}
        />
      </div>
    );
  }

  // 2. Recognized Company Brand Logos
  // --- Wyndham Legend / Radisson ---
  if (comp.includes("wyndham") || comp.includes("radisson")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#002D62] text-amber-300 font-serif font-black shadow-2xs border border-[#1A4B88] ${sizeClasses} ${className}`}
        title="Khách sạn 5 sao Wyndham Legend Hạ Long"
      >
        <div className="flex flex-col items-center justify-center leading-none">
          <span className="text-base sm:text-lg font-black tracking-tight text-white">W</span>
          <span className="text-[6px] font-sans tracking-widest text-amber-300 uppercase scale-90">HOTEL</span>
        </div>
      </div>
    );
  }

  // --- Vinpearl / Vingroup / VinFast / Vinmec ---
  if (comp.includes("vinpearl") || comp.includes("vingroup") || comp.includes("vinfast") || comp.includes("vinmec")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-gradient-to-br from-emerald-800 via-teal-900 to-amber-900 text-amber-300 font-extrabold shadow-2xs border border-emerald-700/60 ${sizeClasses} ${className}`}
        title={companyName || "Tập đoàn Vingroup"}
      >
        <svg viewBox="0 0 24 24" className="w-6 h-6 fill-amber-300" aria-hidden="true">
          <path d="M12 2L15 9L22 9L16.5 13.5L18.5 20.5L12 16L5.5 20.5L7.5 13.5L2 9L9 9Z" />
        </svg>
      </div>
    );
  }

  // --- Sun World / Sun Group ---
  if (comp.includes("sun world") || comp.includes("sun group") || comp.includes("sungroup") || comp.includes("yoko onsen")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-gradient-to-tr from-orange-600 via-amber-500 to-yellow-400 text-white font-extrabold shadow-2xs border border-orange-400 ${sizeClasses} ${className}`}
        title="Sun Group / Sun World"
      >
        <svg viewBox="0 0 24 24" className="w-6 h-6 fill-white" aria-hidden="true">
          <circle cx="12" cy="12" r="5" />
          <path d="M12 1v3m0 16v3M1 12h3m16 0h3M4.22 4.22l2.12 2.12m11.32 11.32l2.12 2.12M4.22 19.78l2.12-2.12m11.32-11.32l2.12-2.12" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      </div>
    );
  }

  // --- FPT / FPT Telecom / FPT Software ---
  if (comp.includes("fpt")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-white border border-slate-200 shadow-2xs ${sizeClasses} ${className}`}
        title="FPT Telecom / Tập đoàn FPT"
      >
        <div className="flex items-center gap-0.5 font-black text-xs sm:text-sm tracking-tighter">
          <span className="text-[#00529C]">F</span>
          <span className="text-[#F37021]">P</span>
          <span className="text-[#00923F]">T</span>
        </div>
      </div>
    );
  }

  // --- Vinacomin / TKV (Than Khoáng Sản) ---
  if (comp.includes("vinacomin") || comp.includes("tkv") || comp.includes("than ") || comp.includes("mỏ ")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-slate-900 text-amber-400 border border-slate-700 shadow-2xs ${sizeClasses} ${className}`}
        title="Tập đoàn Than - Khoáng sản Việt Nam (TKV)"
      >
        <div className="flex flex-col items-center leading-none">
          <span className="text-sm font-black text-amber-400 tracking-tight">TKV</span>
          <span className="text-[6px] tracking-widest text-slate-300 scale-90">COAL</span>
        </div>
      </div>
    );
  }

  // --- Vietcombank ---
  if (comp.includes("vietcombank")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#005B38] text-white font-extrabold shadow-2xs border border-emerald-700 ${sizeClasses} ${className}`}
        title="Ngân hàng Vietcombank"
      >
        <span className="text-xs font-black tracking-tight text-white">VCB</span>
      </div>
    );
  }

  // --- BIDV ---
  if (comp.includes("bidv")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#004B87] text-white font-black shadow-2xs border border-blue-800 ${sizeClasses} ${className}`}
        title="Ngân hàng BIDV"
      >
        <span className="text-xs font-black tracking-tight text-white">BIDV</span>
      </div>
    );
  }

  // --- Techcombank ---
  if (comp.includes("techcombank")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-white text-[#ED1C24] font-black border border-red-200 shadow-2xs ${sizeClasses} ${className}`}
        title="Ngân hàng Techcombank"
      >
        <span className="text-xs font-black tracking-tight text-[#ED1C24]">TCB</span>
      </div>
    );
  }

  // --- KATINAT ---
  if (comp.includes("katinat")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#3B281B] text-[#D8B182] font-serif font-black shadow-2xs border border-amber-900 ${sizeClasses} ${className}`}
        title="KATINAT Saigon Kafe"
      >
        <span className="text-xs font-serif font-bold tracking-widest">K</span>
      </div>
    );
  }

  // --- BIM Group ---
  if (comp.includes("bim group") || comp.includes("bim land")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#0A3D73] text-cyan-300 font-extrabold shadow-2xs border border-blue-900 ${sizeClasses} ${className}`}
        title="Tập đoàn BIM Group"
      >
        <span className="text-xs font-black tracking-tight">BIM</span>
      </div>
    );
  }

  // --- Mường Thanh ---
  if (comp.includes("mường thanh") || comp.includes("muong thanh")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#8B1E22] text-amber-300 font-serif font-black shadow-2xs border border-red-900 ${sizeClasses} ${className}`}
        title="Khách sạn Mường Thanh"
      >
        <span className="text-xs font-serif font-bold">MT</span>
      </div>
    );
  }

  // --- GHTK (Giao Hàng Tiết Kiệm) ---
  if (comp.includes("ghtk") || comp.includes("giao hàng tiết kiệm")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#006A32] text-white font-extrabold shadow-2xs border border-emerald-800 ${sizeClasses} ${className}`}
        title="Giao Hàng Tiết Kiệm (GHTK)"
      >
        <span className="text-[10px] font-black">GHTK</span>
      </div>
    );
  }

  // --- Cảng Quốc Tế Cái Lân (CICT) ---
  if (comp.includes("cái lân") || comp.includes("cict")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#073B4C] text-[#06D6A0] font-extrabold shadow-2xs border border-[#0B5267] ${sizeClasses} ${className}`}
        title="Công Ty CP Cảng Cái Lân (CICT)"
      >
        <div className="flex flex-col items-center justify-center leading-none">
          <span className="text-xs font-black tracking-tight text-white">CICT</span>
          <span className="text-[6px] font-bold tracking-widest text-emerald-300 uppercase scale-90">PORT</span>
        </div>
      </div>
    );
  }

  // --- Nhiệt Điện Quảng Ninh (QNPT) ---
  if (comp.includes("nhiệt điện") || comp.includes("qnpt")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-gradient-to-br from-slate-900 to-blue-950 text-amber-400 font-extrabold shadow-2xs border border-amber-500/40 ${sizeClasses} ${className}`}
        title="Công Ty Cổ Phần Nhiệt Điện Quảng Ninh"
      >
        <div className="flex flex-col items-center justify-center leading-none">
          <span className="text-xs font-black tracking-tight text-amber-300">QNPT</span>
          <span className="text-[6px] font-bold tracking-widest text-slate-300 uppercase scale-90">POWER</span>
        </div>
      </div>
    );
  }

  // =========================================================================
  // 3. "Còn không có thì job tìm ở đâu thì logo tìm ở đó" (Platform Fallback)
  // =========================================================================

  // --- CareerViet ---
  if (plat.includes("career") || plat.includes("careerviet")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-gradient-to-tr from-[#FF5A00] to-[#FF8A00] text-white font-sans font-black shadow-xs border border-orange-400 ${sizeClasses} ${className}`}
        title="Nguồn tìm kiếm: CareerViet"
      >
        <div className="flex flex-col items-center justify-center leading-none">
          <span className="text-xs font-black tracking-tighter text-white">CV</span>
          <span className="text-[7px] font-extrabold tracking-widest text-orange-100 uppercase scale-90">CAREER</span>
        </div>
      </div>
    );
  }

  // --- Facebook ---
  if (plat.includes("facebook") || plat.includes("fb")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#1877F2] text-white shadow-xs border border-blue-400 ${sizeClasses} ${className}`}
        title="Nguồn tìm kiếm: Facebook Group / Fanpage"
      >
        <svg viewBox="0 0 24 24" className="w-5 h-5 fill-white" aria-hidden="true">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      </div>
    );
  }

  // --- Meta Threads ---
  if (plat.includes("threads")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-black text-white shadow-xs border border-neutral-700 ${sizeClasses} ${className}`}
        title="Nguồn tìm kiếm: Meta Threads"
      >
        <span className="text-base sm:text-lg font-black text-white leading-none">@</span>
      </div>
    );
  }

  // --- TikTok ---
  if (plat.includes("tiktok")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-black text-white shadow-xs border border-neutral-800 ${sizeClasses} ${className}`}
        title="Nguồn tìm kiếm: TikTok Tuyển Dụng"
      >
        <svg viewBox="0 0 24 24" className="w-5 h-5 fill-white" aria-hidden="true">
          <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64c.29 0 .58.04.86.12V9.41a6.33 6.33 0 0 0-.86-.06 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.34-6.34V8.71a8.21 8.21 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.14z" />
        </svg>
      </div>
    );
  }

  // --- TopCV ---
  if (plat.includes("topcv")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#00B14F] text-white shadow-xs border border-emerald-400 font-black ${sizeClasses} ${className}`}
        title="Nguồn tìm kiếm: TopCV"
      >
        <div className="flex flex-col items-center leading-none">
          <span className="text-[10px] font-black tracking-tight text-white">TOP</span>
          <span className="text-[8px] font-black tracking-widest text-emerald-100">CV</span>
        </div>
      </div>
    );
  }

  // --- VietnamWorks ---
  if (plat.includes("vietnamworks")) {
    return (
      <div
        className={`relative flex shrink-0 items-center justify-center bg-[#0A58CA] text-white shadow-xs border border-blue-500 font-black ${sizeClasses} ${className}`}
        title="Nguồn tìm kiếm: VietnamWorks"
      >
        <span className="text-xs font-black tracking-tight">VW</span>
      </div>
    );
  }

  // --- Generic Fallback: Initial letter with attractive corporate badge ---
  const initial = companyName ? companyName.trim().charAt(0).toUpperCase() : "C";
  return (
    <div
      className={`relative flex shrink-0 items-center justify-center bg-neutral-100 text-black font-extrabold border border-neutral-300 shadow-2xs ${sizeClasses} ${className}`}
      title={companyName || "Doanh nghiệp"}
    >
      <span>{initial}</span>
    </div>
  );
}
