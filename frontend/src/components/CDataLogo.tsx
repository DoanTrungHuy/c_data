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
      {/* Biểu tượng Logo Đơn Giản & Tinh Tế (Minimalist C_Data Icon) */}
      <div
        className={`relative flex ${iconSizes[size]} shrink-0 items-center justify-center bg-slate-950 border border-slate-800 shadow-md transition-transform duration-200 group-hover:scale-105 p-1.5`}
      >
        <svg
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full"
        >
          <defs>
            <linearGradient id="cdata-arc-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="50%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#6366F1" />
            </linearGradient>
            <linearGradient id="cdata-dot-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
          </defs>

          {/* Đường cong chữ C tối giản, sắc nét, hiện đại */}
          <path
            d="M44 19 A 17.5 17.5 0 1 0 44 45"
            stroke="url(#cdata-arc-grad)"
            strokeWidth="7"
            strokeLinecap="round"
          />

          {/* Điểm hội tụ dữ liệu công nghệ (Data Core Spark) */}
          <circle cx="37" cy="32" r="4.2" fill="url(#cdata-dot-grad)" />
          <circle cx="37" cy="32" r="1.5" fill="#FFFFFF" />
        </svg>
      </div>

      {/* Typography thương hiệu C_Data */}
      <div className="flex flex-col">
        <div className="flex items-center gap-1.5">
          <span
            className={`${textSizes[size]} font-black tracking-tight ${
              isDark ? "text-white" : "text-slate-900"
            } flex items-center leading-none`}
          >
            <span>C</span>
            <span className="text-sky-500 font-extrabold mx-0.5">_</span>
            <span>Data</span>
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
            Việc làm IT &amp; Công nghệ thông tin
          </span>
        )}
      </div>
    </div>
  );
}
