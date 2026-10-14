"use client";

import { useEffect, useState } from "react";
import { Job } from "@/types/job";
import { removeVietnameseTones } from "@/lib/clientSearch";

export interface SkillCategory {
  category: string;
  skills: { id: string; name: string; keywords: string[] }[];
}

export const POPULAR_IT_SKILLS: SkillCategory[] = [
  {
    category: "Hạ tầng & IT Support",
    skills: [
      { id: "it_support", name: "IT Support / Helpdesk", keywords: ["it support", "helpdesk", "ho tro ky thuat", "ky thuat vien cntt", "desktop support"] },
      { id: "lan_wan", name: "Mạng LAN / WAN / Cáp quang", keywords: ["lan", "wan", "mang", "cap quang", "bam day mang", "switch", "router", "wifi"] },
      { id: "cctv", name: "Camera giám sát CCTV", keywords: ["camera", "cctv", "dau ghi", "hikvision", "dahua"] },
      { id: "hardware", name: "Phần cứng máy tính & Máy in", keywords: ["phan cung", "may in", "nap muc", "do muc", "sua may tinh", "pc"] },
      { id: "voip", name: "Tổng đài nội bộ VoIP / IP Phone", keywords: ["tong dai", "voip", "ip phone", "grandstream", "asterisk"] },
    ],
  },
  {
    category: "Quản trị hệ thống & Bảo mật",
    skills: [
      { id: "windows_server", name: "Windows Server & Active Directory", keywords: ["windows server", "active directory", "ad", "domain", "group policy"] },
      { id: "linux", name: "Hệ điều hành Linux / CentOS / Ubuntu", keywords: ["linux", "ubuntu", "centos", "redhat", "debian"] },
      { id: "cisco", name: "Cisco CCNA / Định tuyến & Tường lửa", keywords: ["cisco", "ccna", "fortinet", "sophos", "firewall", "tuong lua", "mikrotik"] },
      { id: "virtualization", name: "Ảo hóa VMware / Hyper-V", keywords: ["vmware", "hyper-v", "ao hoa", "esxi", "proxmox"] },
      { id: "security", name: "An toàn thông tin / An ninh mạng", keywords: ["an toan thong tin", "bao mat", "security", "an ninh mang"] },
    ],
  },
  {
    category: "Phần mềm chuyên ngành Hạ Long & Doanh nghiệp",
    skills: [
      { id: "hospitality_pms", name: "Phần mềm Khách sạn Opera / Smile", keywords: ["opera", "smile", "pms", "khach san", "resort", "hotel"] },
      { id: "hospital_his", name: "Phần mềm Y tế HIS / LIS / PACS", keywords: ["his", "lis", "pacs", "benh vien", "y te", "ho so benh an"] },
      { id: "erp_misa", name: "Phần mềm Kế toán MISA / ERP / Fast", keywords: ["misa", "erp", "fast", "phan mem ke toan", "sap"] },
      { id: "scada_plc", name: "Tự động hóa & SCADA / PLC Cảng & Than", keywords: ["scada", "plc", "tu dong hoa", "cang bien", "tos", "nhiet dien", "mo than"] },
    ],
  },
  {
    category: "Lập trình & Dữ liệu",
    skills: [
      { id: "frontend_dev", name: "Frontend (React / Next.js / Vue / HTML)", keywords: ["react", "next.js", "frontend", "html", "css", "javascript", "typescript"] },
      { id: "backend_dev", name: "Backend (Node.js / Python / Java / PHP)", keywords: ["backend", "node", "python", "java", "php", "c#", ".net"] },
      { id: "database_sql", name: "Cơ sở dữ liệu (SQL Server / MySQL)", keywords: ["sql", "mysql", "sql server", "database", "co so du lieu", "oracle"] },
      { id: "devops_docker", name: "DevOps & Docker / Cloud", keywords: ["docker", "devops", "cloud", "aws", "azure", "git"] },
    ],
  },
  {
    category: "Kinh nghiệm & Kỹ năng làm việc",
    skills: [
      { id: "english_comm", name: "Tiếng Anh giao tiếp", keywords: ["tieng anh", "english", "giao tiep", "toeic"] },
      { id: "shift_work", name: "Sẵn sàng trực ca kíp / On-call", keywords: ["truc ca", "ca kip", "24/7", "truc dem", "ngoai gio"] },
      { id: "driver_license", name: "Bằng lái xe & Linh hoạt di chuyển", keywords: ["lai xe", "xe may", "di chuyen", "o to"] },
    ],
  },
];

const SKILLS_STORAGE_KEY = "cdata_user_selected_skills";

export function getStoredSkills(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(SKILLS_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveStoredSkills(skills: string[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(SKILLS_STORAGE_KEY, JSON.stringify(skills));
    window.dispatchEvent(new CustomEvent("cdata-skills-updated", { detail: skills }));
  } catch {
    // ignore
  }
}

export interface MatchEvaluation {
  score: number; // 0 - 100
  matchedSkills: string[];
  missingSkills: string[];
}

/**
 * Chấm điểm độ phù hợp giữa kỹ năng của người dùng với một tin tuyển dụng
 */
export function evaluateJobMatch(job: Job, userSkillIds: string[]): MatchEvaluation {
  if (!userSkillIds || userSkillIds.length === 0) {
    return { score: 0, matchedSkills: [], missingSkills: [] };
  }

  const jobText = removeVietnameseTones(
    `${job.title || ""} ${job.description || ""} ${job.requirements || ""} ${job.category || ""}`
  );

  const allSkillsFlat = POPULAR_IT_SKILLS.flatMap((cat) => cat.skills);
  const userSkillsMap = new Map(allSkillsFlat.map((s) => [s.id, s]));

  const matched: string[] = [];
  const notMatched: string[] = [];

  for (const skillId of userSkillIds) {
    const skill = userSkillsMap.get(skillId);
    if (!skill) continue;

    const isPresent = skill.keywords.some((kw) => {
      const normKw = removeVietnameseTones(kw);
      return jobText.includes(normKw);
    });

    if (isPresent) {
      matched.push(skill.name);
    } else {
      notMatched.push(skill.name);
    }
  }

  // Base score calculation
  const totalSelected = userSkillIds.length;
  if (totalSelected === 0) {
    return { score: 0, matchedSkills: [], missingSkills: [] };
  }

  const matchRatio = matched.length / totalSelected;
  let finalScore = Math.round(matchRatio * 85);

  // Bonus points if title directly matches
  const normTitle = removeVietnameseTones(job.title || "");
  const hasTitleBonus = userSkillIds.some((id) => {
    const skill = userSkillsMap.get(id);
    return skill?.keywords.some((kw) => normTitle.includes(removeVietnameseTones(kw)));
  });

  if (hasTitleBonus) {
    finalScore = Math.min(98, finalScore + 15);
  } else if (matched.length > 0) {
    finalScore = Math.min(92, finalScore + 10);
  }

  return {
    score: Math.max(15, Math.min(98, finalScore)),
    matchedSkills: matched,
    missingSkills: notMatched.slice(0, 3),
  };
}

/**
 * Hook theo dõi danh sách kỹ năng người dùng theo thời gian thực
 */
export function useUserSkills() {
  const [skills, setSkills] = useState<string[]>([]);

  useEffect(() => {
    setSkills(getStoredSkills());

    const handleUpdate = (e: any) => {
      if (e.detail && Array.isArray(e.detail)) {
        setSkills(e.detail);
      } else {
        setSkills(getStoredSkills());
      }
    };

    window.addEventListener("cdata-skills-updated", handleUpdate);
    window.addEventListener("storage", handleUpdate);
    return () => {
      window.removeEventListener("cdata-skills-updated", handleUpdate);
      window.removeEventListener("storage", handleUpdate);
    };
  }, []);

  const updateSkills = (newSkills: string[]) => {
    setSkills(newSkills);
    saveStoredSkills(newSkills);
  };

  return {
    skills,
    updateSkills,
    hasSkills: skills.length > 0,
  };
}
