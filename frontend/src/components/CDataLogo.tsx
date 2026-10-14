import React from "react";

interface CDataLogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
  theme?: "light" | "dark";
}

export default function CDataLogo({
  className = "",
  size = "md",
  showTagline = true,
  theme = "light",
}: CDataLogoProps) {
  const iconSizes = {
    sm: "h-8 w-8 rounded-lg",
    md: "h-10 w-10 md:h-10 md:w-10 rounded-xl",
    lg: "h-12 w-12 rounded-2xl",
  };

  const textSizes = {
    sm: "text-lg",
    md: "text-xl md:text-2xl",
    lg: "text-2xl md:text-3xl",
  };

  const isDark = theme === "dark";

  return (
    <div className={`flex items-center gap-2.5 sm:gap-3 select-none ${className}`}>
      {/* Biểu tượng Logo Đẳng Cấp & Tinh Tế (Cyber Wave C + Emerald Beacon) */}
      <div
        className={`relative flex ${iconSizes[size]} shrink-0 items-center justify-center transition-transform duration-200 group-hover:scale-105 drop-shadow-sm`}
      >
        <svg
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full"
        >
          <defs>
            <linearGradient id="cdata-bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0A0F1A" />
              <stop offset="100%" stopColor="#111827" />
            </linearGradient>
            <linearGradient id="cdata-arc-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="50%" stopColor="#2563EB" />
              <stop offset="100%" stopColor="#8B5CF6" />
            </linearGradient>
            <linearGradient id="cdata-spark-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#34D399" />
              <stop offset="50%" stopColor="#10B981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
            <linearGradient id="cdata-border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.45" />
              <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.18" />
            </linearGradient>
          </defs>

          {/* Nền Obsidian Squircle & Viền Phản Quang */}
          <rect width="64" height="64" rx="16" fill="url(#cdata-bg-grad)" />
          <rect
            x="0.75"
            y="0.75"
            width="62.5"
            height="62.5"
            rx="15.25"
            stroke="url(#cdata-border-grad)"
            strokeWidth="1.5"
          />

          {/* Đường cong Chữ C Khí Động Học (Sóng Vịnh Hạ Long & Cyber Wave) */}
          <path
            d="M43 20 A 17 17 0 1 0 43 44"
            stroke="url(#cdata-arc-grad)"
            strokeWidth="7.2"
            strokeLinecap="round"
          />

          {/* Ngọn Hải Đăng Di Sản / Ngôi Sao Tri Thức Dữ Liệu (Emerald Beacon Astroid) */}
          <path
            d="M39.5 24 Q39.5 32 45.7 32 Q39.5 32 39.5 40 Q39.5 32 33.3 32 Q39.5 32 39.5 24 Z"
            fill="url(#cdata-spark-grad)"
          />

          {/* Điểm Sáng Trắng Trung Tâm (Core Spark Node) */}
          <circle cx="39.5" cy="32" r="1.8" fill="#FFFFFF" />
        </svg>
      </div>

      {/* Typography thương hiệu VịnhViệc */}
      <div className="flex flex-col">
        <div className="flex items-center gap-1.5">
          <span
            className={`${textSizes[size]} font-black tracking-tight ${
              isDark ? "text-white" : "text-slate-900"
            } flex items-center leading-none`}
          >
            <span>Vịnh</span>
            <span className="bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent font-black ml-0.5">
              Việc
            </span>
          </span>

          <span
            className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-bold border ${
              isDark
                ? "bg-slate-800 text-slate-300 border-slate-700"
                : "bg-slate-100 text-slate-700 border-slate-200"
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Hạ Long
          </span>
        </div>

        {showTagline && (
          <span
            className={`text-[11px] font-medium mt-0.5 hidden sm:block tracking-normal ${
              isDark ? "text-slate-400" : "text-slate-500"
            }`}
          >
            Cơ hội vàng bên Vịnh Di sản
          </span>
        )}
      </div>
    </div>
  );
}
