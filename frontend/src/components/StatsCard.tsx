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
  iconBgClass = "bg-neutral-100 text-black",
  borderAccent = "hover:border-black",
}: StatsCardProps) {
  const formattedValue =
    typeof value === "number" ? value.toLocaleString("vi-VN") : value;

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-neutral-200 bg-white p-6 shadow-xs transition-all duration-200 hover:-translate-y-1 hover:shadow-md ${borderAccent}`}
    >
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">{label}</p>
          <p className="text-3xl font-black tracking-tight text-black">
            {formattedValue}
          </p>
          {subtitle && (
            <p className="text-xs font-semibold text-neutral-600 flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-black inline-block" />
              <span>{subtitle}</span>
            </p>
          )}
        </div>
        <div
          className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-neutral-200 ${iconBgClass}`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}
