import React from "react";

interface CDataLogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
}

export default function CDataLogo({
  className = "",
  size = "md",
  showTagline = true,
}: CDataLogoProps) {
  const iconSizes = {
    sm: "h-8 w-8",
    md: "h-10 w-10 md:h-11 md:w-11",
    lg: "h-14 w-14",
  };

  const textSizes = {
    sm: "text-lg",
    md: "text-xl md:text-2xl",
    lg: "text-3xl",
  };

  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      {/* Dynamic Animated Logo Badge */}
      <div
        className={`relative flex ${iconSizes[size]} shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-slate-950 via-slate-900 to-indigo-950 p-1.5 shadow-lg shadow-indigo-900/20 ring-1 ring-white/10 group-hover:scale-105 group-hover:ring-primary-400/40 transition-all duration-300`}
      >
        <svg
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full"
        >
          <defs>
            <linearGradient id="header-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="50%" stopColor="#6366F1" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
            <linearGradient id="star-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FDE047" />
              <stop offset="100%" stopColor="#F59E0B" />
            </linearGradient>
          </defs>

          {/* Radar Ring "C" */}
          <path
            d="M48 20 C43 13 35 11 28 13 C19 16 13 24 13 32 C13 40 19 48 28 51 C36 53 43 50 48 44"
            stroke="url(#header-grad)"
            strokeWidth="7"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Radar Wave */}
          <path
            d="M44 26 C41 22 36 21 32 22 C26 24 22 29 22 34 C22 38 25 42 30 43 C33 44 37 43 40 40"
            stroke="#38BDF8"
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.75"
          />

          {/* Central Beacon Compass Star */}
          <g transform="translate(32, 32)">
            <circle r="4" fill="none" stroke="#F59E0B" strokeWidth="1.2" opacity="0.8" />
            <path
              d="M0 -8.5 Q0 0 8.5 0 Q0 0 0 8.5 Q0 0 -8.5 0 Q0 0 0 -8.5 Z"
              fill="url(#star-grad)"
            />
            <circle r="1.8" fill="#FFFFFF" />
          </g>

          {/* Scanning Node */}
          <circle cx="48" cy="20" r="3" fill="#38BDF8" />
          <circle cx="48" cy="20" r="1.5" fill="#FFFFFF" />
        </svg>

        {/* Live Pulse Glow */}
        <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
        </span>
      </div>

      {/* Typography */}
      <div className="flex flex-col">
        <span
          className={`${textSizes[size]} font-black tracking-tight text-slate-900 flex items-center gap-1.5`}
        >
          <span>C</span>
          <span className="text-primary-600">_</span>
          <span className="bg-gradient-to-r from-slate-900 via-primary-950 to-indigo-900 bg-clip-text text-transparent">
            Data
          </span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-gradient-to-r from-amber-50 to-orange-50 text-amber-800 border border-amber-200/80 shadow-2xs">
            Hạ Long • VN
          </span>
        </span>

        {showTagline && (
          <span className="text-[11px] font-semibold text-slate-500 -mt-0.5 hidden sm:block tracking-wide">
            Radar việc làm thông minh &amp; Đang tuyển dụng
          </span>
        )}
      </div>
    </div>
  );
}
