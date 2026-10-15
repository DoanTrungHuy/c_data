import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, isValid, parseISO } from "date-fns";
import { vi } from "date-fns/locale";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format salary in Vietnamese currency
 * Example: 8 - 12 triệu, Từ 15 triệu, Lên tới 30 triệu, Thỏa thuận
 */
export function formatSalary(
  min?: number | null,
  max?: number | null,
  text?: string | null
): string {
  if (text && text.trim() !== "" && text.toLowerCase() !== "null") {
    // If the text looks like an informative salary string, return it cleaned
    const cleanText = text.trim();
    if (
      cleanText.toLowerCase() === "thỏa thuận" ||
      cleanText.toLowerCase() === "thoa thuan" ||
      cleanText.toLowerCase() === "negotiable"
    ) {
      return "Thỏa thuận";
    }
    return cleanText;
  }

  const formatNumberToMillion = (val: number): string => {
    if (val >= 1_000_000) {
      const millions = val / 1_000_000;
      return millions % 1 === 0 ? `${millions}` : `${millions.toFixed(1)}`;
    }
    if (val >= 1_000) {
      return `${(val / 1_000).toLocaleString("vi-VN")}k`;
    }
    return `${val.toLocaleString("vi-VN")}đ`;
  };

  if (min && max) {
    if (min === max) {
      return `${formatNumberToMillion(min)} triệu`;
    }
    const minStr = formatNumberToMillion(min);
    const maxStr = formatNumberToMillion(max);
    return `${minStr} - ${maxStr} triệu`;
  }

  if (min && !max) {
    return `Từ ${formatNumberToMillion(min)} triệu`;
  }

  if (!min && max) {
    return `Tới ${formatNumberToMillion(max)} triệu`;
  }

  return "Thỏa thuận";
}

/**
 * Format date to Vietnamese relative or human-readable format
 * Example: "2 giờ trước", "Hôm qua", "3 ngày trước"
 */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "Gần đây";

  try {
    const parsed = typeof dateStr === "string" ? parseISO(dateStr) : new Date(dateStr);
    if (!isValid(parsed)) {
      return "Gần đây";
    }

    const now = new Date();
    const diffHours = (now.getTime() - parsed.getTime()) / (1000 * 60 * 60);

    if (diffHours < 1 && diffHours >= 0) {
      return "Vừa xong";
    }

    if (diffHours < 24 && parsed.getDate() === now.getDate()) {
      return `Hôm nay lúc ${parsed.toLocaleTimeString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
      })}`;
    }

    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (
      parsed.getDate() === yesterday.getDate() &&
      parsed.getMonth() === yesterday.getMonth() &&
      parsed.getFullYear() === yesterday.getFullYear()
    ) {
      return "Hôm qua";
    }

    // Relative distance for <= 30 days
    if (diffHours < 24 * 30 && diffHours >= 0) {
      return formatDistanceToNow(parsed, {
        addSuffix: true,
        locale: vi,
      });
    }

    return parsed.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return "Gần đây";
  }
}

/**
 * Format job type to Vietnamese
 */
export function formatJobType(type?: string | null): string {
  if (!type) return "Toàn thời gian";

  const lower = type.toLowerCase().trim();
  if (lower.includes("toàn") || lower.includes("full")) {
    return "Toàn thời gian";
  }
  if (lower.includes("bán") || lower.includes("part")) {
    return "Bán thời gian";
  }
  if (lower.includes("remote") || lower.includes("từ xa")) {
    return "Từ xa (Remote)";
  }
  if (lower.includes("thực tập") || lower.includes("intern")) {
    return "Thực tập sinh";
  }
  if (lower.includes("hợp đồng") || lower.includes("contract") || lower.includes("freelance")) {
    return "Hợp đồng / Dự án";
  }

  return type;
}

export interface PlatformInfo {
  id: string;
  name: string;
  badgeClass: string;
  dotClass: string;
  iconBg: string;
}

/**
 * Get display info and color badges for source platforms
 */
export function getSourcePlatformInfo(platform?: string | null): PlatformInfo {
  const defaultInfo: PlatformInfo = {
    id: "c_data",
    name: "C_Data",
    badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
    dotClass: "bg-black",
    iconBg: "bg-neutral-900",
  };

  if (!platform) {
    return defaultInfo;
  }

  const p = platform.toLowerCase();

  if (p.includes("topcv")) {
    return {
      id: "topcv",
      name: "TopCV",
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("vietnamworks")) {
    return {
      id: "vietnamworks",
      name: "VietnamWorks",
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("career") || p.includes("careerviet")) {
    return {
      id: "careerviet",
      name: "CareerViet",
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("itviec")) {
    return {
      id: "itviec",
      name: "ITviec",
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("vieclam24h") || p.includes("24h")) {
    return {
      id: "vieclam24h",
      name: "Việc Làm 24h",
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("facebook") || p.includes("fb")) {
    return {
      id: "facebook",
      name: platform,
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("threads")) {
    return {
      id: "threads",
      name: platform,
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("tiktok")) {
    return {
      id: "tiktok",
      name: platform,
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("doanh nghiệp") || p.includes("công ty") || p.includes("sungroup") || p.includes("vinpearl")) {
    const cleanName = platform && platform.length > 20 ? truncateText(platform, 18) : platform;
    return {
      id: "company",
      name: cleanName,
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  if (p.includes("linkedin")) {
    return {
      id: "linkedin",
      name: "LinkedIn",
      badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
      dotClass: "bg-black",
      iconBg: "bg-neutral-900",
    };
  }

  const cleanOtherName = platform && platform.length > 20 ? truncateText(platform, 18) : platform;
  return {
    id: "other",
    name: cleanOtherName,
    badgeClass: "bg-neutral-100 text-neutral-800 border-neutral-300",
    dotClass: "bg-black",
    iconBg: "bg-neutral-900",
  };
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text?: string | null, maxLength = 120): string {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + "...";
}
