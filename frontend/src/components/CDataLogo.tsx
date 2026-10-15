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
  showTagline = false,
  theme = "light",
}: CDataLogoProps) {
  const iconSizes = {
    sm: "h-8 w-8",
    md: "h-9 w-9 sm:h-10 sm:w-10",
    lg: "h-11 w-11 sm:h-12 sm:w-12",
  };

  const textSizes = {
    sm: "text-lg",
    md: "text-xl sm:text-2xl",
    lg: "text-2xl sm:text-3xl",
  };

  const isDark = theme === "dark";

  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      {/* Biểu tượng Logo Tối Giản & Nhận Diện VịnhViệc (Monogram VV + Ngọn Hải Đăng Vịnh) */}
      <div
        className={`relative flex ${iconSizes[size]} shrink-0 items-center justify-center transition-transform duration-200 group-hover:scale-105`}
      >
        <svg
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-xs"
        >
          <defs>
            <linearGradient id="vv-brand-bg" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1E40AF" />
              <stop offset="100%" stopColor="#2563EB" />
            </linearGradient>
            <linearGradient id="vv-spark-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#60A5FA" />
            </linearGradient>
          </defs>

          {/* Nền Squircle Hiện Đại */}
          <rect width="40" height="40" rx="10" fill="url(#vv-brand-bg)" />

          {/* Đường Viền Tinh Tế */}
          <rect
            x="0.5"
            y="0.5"
            width="39"
            height="39"
            rx="9.5"
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth="1"
          />

          {/* Biểu Tượng VịnhViệc (Double V: Sóng Vịnh + Cơ Hội Tuyển Dụng) */}
          <path
            d="M8.5 15 L14.5 27 L20 17 L25.5 27 L31.5 15"
            stroke="#FFFFFF"
            strokeWidth="3.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Điểm Sáng / Viên Ngọc Di Sản Vịnh Hạ Long */}
          <circle cx="20" cy="11" r="2.2" fill="url(#vv-spark-grad)" />
          <circle cx="20" cy="11" r="1" fill="#FFFFFF" />
        </svg>
      </div>

      {/* Typography Tên Web VịnhViệc Chuẩn Đẹp, Rõ Ràng & Đơn Giản */}
      <div className="flex flex-col justify-center">
        <div className="flex items-center gap-1.5 leading-none">
          <span
            className={`${textSizes[size]} font-black tracking-tight ${
              isDark ? "text-white" : "text-slate-900"
            }`}
          >
            Vịnh<span className="text-blue-600">Việc</span>
          </span>

          <span
            className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md border ${
              isDark
                ? "bg-slate-800 text-blue-400 border-slate-700"
                : "bg-blue-50 text-blue-700 border-blue-200/80"
            }`}
          >
            .vn
          </span>
        </div>

        {showTagline && (
          <span
            className={`text-[11px] font-medium mt-1 tracking-normal ${
              isDark ? "text-slate-400" : "text-slate-500"
            }`}
          >
            Việc làm thông minh Quảng Ninh
          </span>
        )}
      </div>
    </div>
  );
}
