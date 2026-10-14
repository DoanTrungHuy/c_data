import React from "react";

interface StatsCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  iconBgClass?: string;
  borderAccent?: string;
}

export default function StatsCard({
  label,
  value,
  subtitle,
  icon,
  iconBgClass = "bg-primary-50 text-primary-600",
  borderAccent = "hover:border-primary-300",
}: StatsCardProps) {
  const formattedValue =
    typeof value === "number" ? value.toLocaleString("vi-VN") : value;

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-slate-200/90 bg-white p-6 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-md ${borderAccent}`}
    >
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="text-3xl font-black tracking-tight text-slate-900">
            {formattedValue}
          </p>
          {subtitle && (
            <p className="text-xs font-semibold text-emerald-600 flex items-center gap-1 mt-1">
              <span>●</span>
              <span>{subtitle}</span>
            </p>
          )}
        </div>
        <div
          className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl ${iconBgClass}`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}
