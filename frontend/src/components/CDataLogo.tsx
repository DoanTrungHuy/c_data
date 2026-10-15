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
      {/* Biểu tượng Logo Tối Giản VịnhViệc (Monogram VV đen-trắng dứt khoát) */}
      <div
        className={`relative flex ${iconSizes[size]} shrink-0 items-center justify-center transition-transform duration-200 group-hover:scale-105`}
      >
        <svg
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-xs"
        >
          {/* Nền Squircle Đen/Trắng Dứt Khoát */}
          <rect
            width="40"
            height="40"
            rx="10"
            fill={isDark ? "#FFFFFF" : "#09090B"}
          />

          {/* Viền sắc nét */}
          <rect
            x="0.5"
            y="0.5"
            width="39"
            height="39"
            rx="9.5"
            stroke={isDark ? "rgba(0, 0, 0, 0.1)" : "rgba(255, 255, 255, 0.2)"}
            strokeWidth="1"
          />

          {/* Biểu Tượng VịnhViệc (Double V Tối Giản) */}
          <path
            d="M8.5 15 L14.5 27 L20 17 L25.5 27 L31.5 15"
            stroke={isDark ? "#09090B" : "#FFFFFF"}
            strokeWidth="3.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Điểm nhấn tối giản */}
          <circle
            cx="20"
            cy="11"
            r="1.8"
            fill={isDark ? "#09090B" : "#FFFFFF"}
          />
        </svg>
      </div>

      {/* Typography Tên Web VịnhViệc Đen-Trắng Rõ Ràng & Đơn Giản */}
      <div className="flex flex-col justify-center">
        <div className="flex items-center gap-1.5 leading-none">
          <span
            className={`${textSizes[size]} font-black tracking-tight ${
              isDark ? "text-white" : "text-black"
            }`}
          >
            VịnhViệc
          </span>

          <span
            className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md border tracking-tight ${
              isDark
                ? "bg-neutral-800 text-neutral-200 border-neutral-700"
                : "bg-neutral-100 text-neutral-900 border-neutral-300"
            }`}
          >
            .vn
          </span>
        </div>

        {showTagline && (
          <span
            className={`text-[11px] font-medium mt-1 tracking-normal ${
              isDark ? "text-neutral-400" : "text-neutral-500"
            }`}
          >
            Việc làm thông minh Quảng Ninh
          </span>
        )}
      </div>
    </div>
  );
}
