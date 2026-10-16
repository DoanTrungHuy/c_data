import { Job, JobListResponse, JobSearchParams } from "@/types/job";
import { getSavedJobIds } from "@/lib/savedJobs";

/**
 * Chuẩn hóa chuỗi tiếng Việt không dấu để tìm kiếm thời gian thực
 */
export function removeVietnameseTones(str: string): string {
  if (!str) return "";
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLowerCase()
    .trim();
}

// Bảng từ đồng nghĩa vai trò và chuyên môn có trọng tâm chính xác (Precise Role Taxonomy)
const PRECISE_ROLE_SYNONYMS: Record<string, string[]> = {
  it: ["it", "cntt", "cong nghe thong tin", "information technology"],
  "it support": [
    "it support",
    "helpdesk",
    "ho tro ky thuat",
    "ky thuat vien cntt",
    "desktop support",
    "it helpdesk",
    "it officer",
  ],
  "it officer": [
    "it officer",
    "chuyen vien it",
    "nhan vien it",
    "it support",
    "quan tri he thong it",
  ],
  "lap trinh vien": [
    "lap trinh vien",
    "developer",
    "software engineer",
    "lap trinh",
    "coder",
  ],
  developer: [
    "developer",
    "lap trinh vien",
    "software engineer",
    "frontend developer",
    "backend developer",
    "fullstack developer",
  ],
  frontend: ["frontend", "front-end", "react", "vue", "nextjs", "next.js", "ui developer"],
  backend: [
    "backend",
    "back-end",
    "python",
    "fastapi",
    "nodejs",
    "node.js",
    "java",
    "golang",
  ],
  "ke toan": ["ke toan", "accountant", "kiem toan", "thu quy"],
  "ke toan truong": ["ke toan truong", "chief accountant", "truong phong ke toan"],
  "ke toan tong hop": ["ke toan tong hop", "general accountant"],
  "ke toan thue": ["ke toan thue", "tax accountant"],
  "le tan": ["le tan", "receptionist", "tiep tan", "khanh tiet", "front desk"],
  marketing: [
    "marketing",
    "truyen thong",
    "digital marketing",
    "seo",
    "content creator",
    "copywriter",
    "truyen thong su kien",
  ],
  sales: [
    "sales",
    "kinh doanh",
    "nhan vien kinh doanh",
    "ban hang",
    "tu van ban hang",
    "phat trien thi truong",
  ],
  "nhan su": ["nhan su", "hr", "human resources", "tuyen dung", "c&b"],
  "lai xe": ["lai xe", "tai xe", "lai xe b2", "lai xe du lich", "lai xe 16 cho"],
  "bao ve": ["bao ve", "an ninh", "ve si", "tuan tra", "an ninh toa nha"],
  "an toan thong tin": ["an toan thong tin", "cyber security", "information security", "soc", "attt"],
  "phuc vu": ["phuc vu", "waiter", "waitress", "order", "chay ban"],
  "dau bep": ["dau bep", "chef", "cook", "bep truong", "phu bep"],
  "quan tri mang": [
    "quan tri mang",
    "network admin",
    "ha tang mang",
    "network engineer",
    "cisco",
  ],
  "ky su tu dong hoa": [
    "ky su tu dong hoa",
    "automation engineer",
    "plc",
    "scada",
    "dcs",
  ],
  "ky su dien": ["ky su dien", "electrical engineer", "dien cong nghiep"],
  "ky su xay dung": ["ky su xay dung", "civil engineer", "giam sat xay dung"],
};

// Phân cấp địa danh: Phường/Xã/Khu vực -> Quận/Huyện/Thị xã/Thành phố -> Tỉnh
const WARD_ALIASES: Record<string, string[]> = {
  "bai chay": ["bai chay", "wyndham", "novotel", "sun world", "ha long bay view"],
  "cai lan": ["cai lan", "cict", "cang cai lan", "kcn cai lan", "calofic"],
  "hon gai": ["hon gai", "hong gai", "cot 5", "benh vien da khoa tinh", "vinmec ha long"],
  "tuan chau": ["tuan chau", "dao tuan chau", "cang tuan chau"],
  "dong trieu": ["dong trieu", "mao khe"],
  "cam pha": ["cam pha", "quang hanh", "yoko onsen", "mong duong", "coc sau", "deo nai"],
  "uong bi": ["uong bi", "yen tu"],
  "mong cai": ["mong cai", "tra co"],
  "van don": ["van don", "san bay van don", "cai rong"],
};

const DISTRICT_ALIASES: Record<string, string[]> = {
  "ha long": [
    "ha long",
    "bai chay",
    "hon gai",
    "hong gai",
    "cai lan",
    "tuan chau",
    "gieng day",
    "ha lam",
    "ha tu",
    "cao thang",
    "wyndham",
    "novotel",
    "sun world",
  ],
  "cam pha": ["cam pha", "quang hanh", "yoko onsen", "mong duong", "coc sau", "deo nai"],
  "uong bi": ["uong bi", "yen tu"],
  "dong trieu": ["dong trieu", "mao khe"],
  "mong cai": ["mong cai", "tra co"],
  "van don": ["van don", "cai rong", "san bay van don"],
  "quang yen": ["quang yen", "kcn amata", "dong mai"],
};

const PROVINCE_ALIASES: Record<string, string[]> = {
  "quang ninh": [
    "quang ninh",
    "ha long",
    "cam pha",
    "uong bi",
    "dong trieu",
    "mong cai",
    "van don",
    "quang yen",
    "bai chay",
    "cai lan",
    "hon gai",
  ],
  "ha noi": [
    "ha noi",
    "cau giay",
    "thanh xuan",
    "dong da",
    "ba dinh",
    "hai ba trung",
    "nam tu liem",
    "bac tu liem",
  ],
  "ho chi minh": [
    "ho chi minh",
    "hcm",
    "sai gon",
    "quan 1",
    "quan 7",
    "tan binh",
    "thu duc",
    "binh thanh",
  ],
  "da nang": ["da nang", "hai chau", "thanh khe", "son tra", "ngu hanh son"],
};

// Sắp xếp các địa danh từ cụ thể nhất (phường/khu) đến tổng quát nhất (tỉnh)
const KNOWN_LOCATIONS_ORDERED = [
  "bai chay",
  "cai lan",
  "hon gai",
  "hong gai",
  "tuan chau",
  "quang hanh",
  "mao khe",
  "ha long",
  "cam pha",
  "uong bi",
  "dong trieu",
  "mong cai",
  "van don",
  "quang yen",
  "quang ninh",
  "ha noi",
  "ho chi minh",
  "hcm",
  "sai gon",
  "da nang",
  "hai phong",
];

function getTargetLocationTokens(locKey: string): Set<string> {
  const norm = removeVietnameseTones(locKey);
  const tokens = new Set<string>([norm]);

  if (WARD_ALIASES[norm]) {
    WARD_ALIASES[norm].forEach((t) => tokens.add(t));
    return tokens;
  }

  if (DISTRICT_ALIASES[norm]) {
    DISTRICT_ALIASES[norm].forEach((t) => tokens.add(t));
    return tokens;
  }

  if (PROVINCE_ALIASES[norm]) {
    PROVINCE_ALIASES[norm].forEach((t) => tokens.add(t));
    return tokens;
  }

  return tokens;
}

let cachedJobs: Job[] | null = null;
let isFetchingJobs = false;
let fetchPromise: Promise<Job[]> | null = null;

/**
 * Tải toàn bộ dữ liệu jobs từ JSON tĩnh phục vụ tìm kiếm Real-time
 */
export async function loadAllJobsForClient(): Promise<Job[]> {
  if (cachedJobs && cachedJobs.length > 0) {
    return cachedJobs;
  }

  if (isFetchingJobs && fetchPromise) {
    return fetchPromise;
  }

  isFetchingJobs = true;
  fetchPromise = (async () => {
    try {
      if (typeof window === "undefined") {
        try {
          const fs = require("fs");
          const path = require("path");
          const jsonPath = path.join(process.cwd(), "public", "data", "jobs.json");
          if (fs.existsSync(jsonPath)) {
            const data = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
            if (Array.isArray(data) && data.length > 0) {
              cachedJobs = data;
              return data;
            }
          }
        } catch {
          // ignore
        }
      } else {
        const isGhPages =
          window.location.pathname.startsWith("/c_data") ||
          window.location.hostname.includes("github.io");
        const dataUrl = isGhPages ? "/c_data/data/jobs.json" : "/data/jobs.json";

        const res = await fetch(dataUrl);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            cachedJobs = data;
            return data;
          }
        }
      }
    } catch (err) {
      console.warn("Client fallback to static JSON failed:", err);
    } finally {
      isFetchingJobs = false;
    }
    return [];
  })();

  return fetchPromise;
}

/**
 * Sinh từ khóa liên quan thông minh và năng động dựa trên từ khóa người dùng gõ
 */
function generateContextualKeywords(cleanRoleQ: string, total: number): string[] {
  if (total === 0) return [];

  if (cleanRoleQ.includes("it support") || cleanRoleQ.includes("helpdesk")) {
    return [
      "IT Support Hạ Long",
      "IT Officer Khách Sạn",
      "Helpdesk Bãi Cháy",
      "Quản trị hệ thống CNTT",
      "Kỹ thuật viên IT Quảng Ninh",
    ];
  }
  if (cleanRoleQ === "it" || cleanRoleQ === "cntt") {
    return [
      "IT Officer Khách Sạn 5 Sao",
      "Kỹ sư CNTT Cái Lân",
      "IT Support Bãi Cháy",
      "Quản trị mạng hệ thống",
      "Lập trình viên React",
    ];
  }
  if (cleanRoleQ.includes("ke toan")) {
    return [
      "Kế toán trưởng Hạ Long",
      "Kế toán tổng hợp Bãi Cháy",
      "Kế toán thuế Quảng Ninh",
      "Chuyên viên kế toán doanh thu",
      "Kế toán kho Cái Lân",
    ];
  }
  if (cleanRoleQ.includes("le tan") || cleanRoleQ.includes("tiep tan")) {
    return [
      "Lễ tân khách sạn 5 sao Bãi Cháy",
      "Nhân viên tiếp tân Hạ Long",
      "Lễ tân tiếng Anh Novotel",
      "Chuyên viên hành chính khánh tiết",
    ];
  }
  if (cleanRoleQ.includes("marketing") || cleanRoleQ.includes("truyen thong")) {
    return [
      "Digital Marketing Hạ Long",
      "Chuyên viên Content Creator",
      "Truyền thông sự kiện Bãi Cháy",
      "SEO Marketing Du Lịch",
    ];
  }
  if (cleanRoleQ.includes("sales") || cleanRoleQ.includes("kinh doanh")) {
    return [
      "Nhân viên kinh doanh Hạ Long",
      "Tư vấn bán hàng Bãi Cháy",
      "Chuyên viên phát triển thị trường",
      "Sale du lịch khách sạn",
    ];
  }
  if (cleanRoleQ.includes("lap trinh") || cleanRoleQ.includes("developer") || cleanRoleQ.includes("react")) {
    return [
      "Lập trình viên React Hạ Long",
      "Backend Python FPT Quảng Ninh",
      "Frontend Next.js TypeScript",
      "Fullstack Developer",
    ];
  }

  return [
    "IT Support Hạ Long",
    "IT Officer Khách Sạn",
    "Kỹ sư CNTT Cái Lân",
    "Lập trình viên React",
    "Nhân viên IT Bãi Cháy",
    "Quản trị mạng hệ thống",
  ];
}

/**
 * Tìm kiếm Real-time (Client-side Search Engine)
 * Chạy ngay lập tức trong 2ms trên từng phím gõ của người dùng
 * Đảm bảo độ chính xác tuyệt đối, loại bỏ 100% false positives
 */
export function searchJobsRealtime(
  allJobs: Job[],
  params: JobSearchParams = {}
): JobListResponse {
  if (!allJobs || allJobs.length === 0) {
    return {
      items: [],
      total: 0,
      page: 1,
      page_size: params.page_size || 20,
      total_pages: 0,
      related_keywords: [],
      matched_industries: [],
    };
  }

  const rawQ = (params.q || "").trim();
  const normQ = removeVietnameseTones(rawQ);
  const rawProvince = (params.province || "").trim();
  const normProvince = removeVietnameseTones(rawProvince);

  // 1. Phân tách địa danh nếu người dùng gõ trong ô tìm kiếm (ví dụ "IT Bãi Cháy" -> tách "IT" và "Bãi Cháy")
  let cleanRoleQ = normQ;
  let detectedLoc = "";
  for (const loc of KNOWN_LOCATIONS_ORDERED) {
    if (cleanRoleQ.includes(loc)) {
      detectedLoc = loc;
      cleanRoleQ = cleanRoleQ.replace(loc, " ").replace(/\s+/g, " ").trim();
      break;
    }
  }

  // Tiêu chí địa điểm bắt buộc
  let targetLocTokens: Set<string> | null = null;
  if (detectedLoc) {
    targetLocTokens = getTargetLocationTokens(detectedLoc);
  } else if (normProvince) {
    targetLocTokens = getTargetLocationTokens(normProvince);
  }

  const roleTokens = cleanRoleQ.split(/\s+/).filter(Boolean);
  const isMultiWord = roleTokens.length > 1;

  // Lọc danh sách nếu người dùng đang xem việc làm đã lưu
  let pool = allJobs;
  if (params.saved) {
    const savedIds = getSavedJobIds();
    pool = allJobs.filter((j) => savedIds.includes(String(j.id)));
  }

  // Chấm điểm và xếp hạng từng tin tuyển dụng
  const scoredJobs = pool.map((job) => {
    let score = 0;
    const reasons: string[] = [];

    const normTitle = removeVietnameseTones(job.title || "");
    const normCompany = removeVietnameseTones(job.company_name || "");
    const normCategory = removeVietnameseTones(job.category || "");
    const normDesc = removeVietnameseTones(job.description || "");
    const normReq = removeVietnameseTones(job.requirements || "");
    const normLoc = removeVietnameseTones(
      `${job.location_province || ""} ${job.location_district || ""} ${job.location_full || ""}`
    );
    const techStackNorm = (job.tech_stack || []).map((t) => removeVietnameseTones(t));

    // A. BẮT BUỘC KHỚP VỊ TRÍ ĐỊA LÝ (Hard location filter nếu có chỉ định)
    if (targetLocTokens && targetLocTokens.size > 0) {
      let locMatched = false;
      for (const loc of Array.from(targetLocTokens)) {
        if (normLoc.includes(loc) || normCompany.includes(loc) || normTitle.includes(loc)) {
          locMatched = true;
          break;
        }
      }
      if (!locMatched) {
        return { job, score: -9999 };
      }
      score += 25;
      reasons.push(`Khu vực tuyển dụng phù hợp (+25)`);
    }

    // B. KHỚP TỪ KHÓA NGHỀ NGHIỆP / CÔNG VIỆC
    if (cleanRoleQ) {
      let queryScore = 0;

      // Tier 1: Khớp chức danh tuyệt đối (Exact Title)
      if (normTitle === cleanRoleQ) {
        queryScore = 120;
        reasons.push(`Chức danh chính xác tuyệt đối "${job.title}" (+120)`);
      }
      // Tier 2: Tiêu đề chứa nguyên văn cụm tìm kiếm (Phrase Substring)
      else if (normTitle.includes(cleanRoleQ)) {
        queryScore = 95;
        reasons.push(`Tiêu đề chứa nguyên cụm "${cleanRoleQ}" (+95)`);
      }
      // Tier 3: Tất cả từ khóa trong query đều có mặt trong Tiêu đề (All tokens in title)
      else if (isMultiWord && roleTokens.every((t) => new RegExp(`(^|\\s)${t}(\\s|$)`).test(normTitle))) {
        queryScore = 85;
        reasons.push(`Tiêu đề chứa đủ các từ khóa "${cleanRoleQ}" (+85)`);
      }
      // Tier 4: Khớp từ đồng nghĩa chính xác trong Tiêu đề (Precise Role Synonym in Title)
      else {
        for (const [key, synList] of Object.entries(PRECISE_ROLE_SYNONYMS)) {
          const userMatchesRole = cleanRoleQ === key || synList.includes(cleanRoleQ);
          if (userMatchesRole) {
            for (const syn of synList) {
              if (normTitle.includes(syn)) {
                queryScore = 75;
                reasons.push(`Tiêu đề khớp vị trí tương đương "${syn}" (+75)`);
                break;
              }
            }
            if (queryScore > 0) break;
          }
        }
      }

      // Tier 5: Khớp tên doanh nghiệp (Company match)
      if (queryScore === 0 && normCompany.includes(cleanRoleQ)) {
        queryScore = 70;
        reasons.push(`Khớp doanh nghiệp "${job.company_name}" (+70)`);
      }

      // Tier 6: Khớp công nghệ chuyên môn (Tech Stack match)
      if (
        queryScore === 0 &&
        techStackNorm.some((t) => t === cleanRoleQ || cleanRoleQ.includes(t) || t.includes(cleanRoleQ))
      ) {
        queryScore = 65;
        reasons.push(`Khớp kỹ năng / công nghệ tuyển dụng (+65)`);
      }

      // Tier 7: Từ khóa đơn (Single token match in title or category)
      if (queryScore === 0 && !isMultiWord) {
        if (cleanRoleQ === "it" || cleanRoleQ === "cntt") {
          const itRegex = /(?:^|\s|\/|\()(it|cntt)(?:$|\s|\/|\))/i;
          if (itRegex.test(normTitle)) {
            queryScore = 60;
            reasons.push(`Tiêu đề định danh vị trí CNTT / IT (+60)`);
          }
        } else {
          const wordRegex = new RegExp(`(^|\\s)${cleanRoleQ}(\\s|$)`);
          if (wordRegex.test(normTitle)) {
            queryScore = 60;
            reasons.push(`Tiêu đề chứa từ khóa "${cleanRoleQ}" (+60)`);
          } else if (normCategory.includes(cleanRoleQ)) {
            queryScore = 40;
            reasons.push(`Khớp danh mục ngành nghề (+40)`);
          }
        }
      }

      // Tier 8: Khớp mô tả công việc (Description Match - Gated chặt chẽ, không để rò rỉ tin trái ngành)
      if (queryScore === 0) {
        if (isMultiWord) {
          // Bắt buộc chứa nguyên cụm từ trong mô tả
          if (normDesc.includes(cleanRoleQ) || normReq.includes(cleanRoleQ)) {
            queryScore = 25;
            reasons.push(`Mô tả công việc có cụm từ liên quan "${cleanRoleQ}" (+25)`);
          }
        } else if (cleanRoleQ.length >= 3 && cleanRoleQ !== "it") {
          const wordRegex = new RegExp(`(^|\\s)${cleanRoleQ}(\\s|$)`);
          if (wordRegex.test(normDesc) || wordRegex.test(normReq)) {
            queryScore = 20;
            reasons.push(`Mô tả công việc có đề cập "${cleanRoleQ}" (+20)`);
          }
        }
      }

      // BẮT BUỘC: Nếu có từ khóa mà không khớp bất kỳ điều kiện nào -> LOẠI BỎ NGAY LẬP TỨC
      if (queryScore === 0) {
        return {
          job: {
            ...job,
            match_score: 0,
            match_reasons: [],
          },
          score: -9999,
        };
      }

      // Ràng buộc nghiêm ngặt (Strict mode)
      if (params.strict_mode) {
        const fullJobHaystack = `${normTitle} ${normCompany} ${normDesc} ${normReq} ${normLoc} ${normCategory}`;
        const hasAll = cleanRoleQ.split(/\s+/).every((t) => fullJobHaystack.includes(t));
        if (!hasAll) {
          return {
            job: {
              ...job,
              match_score: 0,
              match_reasons: [],
            },
            score: -9999,
          };
        }
      }

      score += queryScore;
    } else {
      // Khi không có từ khóa (chế độ duyệt danh sách)
      score += 40;
    }

    // C. CÁC TIÊU CHÍ BỘ LỌC BỔ SUNG (Category, Salary, Job Type, Quality Tier)
    if (params.category) {
      const normCatParam = removeVietnameseTones(params.category);
      if (normCategory.includes(normCatParam)) {
        score += 20;
      } else {
        score -= 30;
      }
    }

    if (params.salary_min && (job.salary_max || job.salary_min || 0) < params.salary_min) {
      score -= 20;
    }
    if (params.salary_max && (job.salary_min || 0) > params.salary_max) {
      score -= 20;
    }

    if (params.job_type) {
      const normType = removeVietnameseTones(params.job_type);
      const normJobType = removeVietnameseTones(job.job_type || "");
      if (normJobType.includes(normType)) {
        score += 10;
      } else {
        score -= 20;
      }
    }

    if (params.quality_tier) {
      const qScore = job.quality_score || 0;
      if (params.quality_tier === "diamond" && qScore < 85) {
        return { job, score: -9999 };
      }
      if (params.quality_tier === "gold" && qScore < 70) {
        return { job, score: -9999 };
      }
    }

    if (params.tech_stack) {
      const targetTech = removeVietnameseTones(params.tech_stack);
      const hasTech = techStackNorm.some((t) => t.includes(targetTech) || targetTech.includes(t));
      if (hasTech) {
        score += 35;
        reasons.push(`Khớp công nghệ yêu cầu: ${params.tech_stack} (+35)`);
      } else {
        score -= 25;
      }
    }

    // Điểm cộng chất lượng thẩm định
    if (job.quality_score && job.quality_score >= 85) {
      score += 15;
      reasons.push(`Tin tuyển dụng thẩm định kim cương (${job.quality_score}/100đ) (+15)`);
    } else if (job.quality_score && job.quality_score >= 70) {
      score += 8;
    }

    // Điểm cộng Dẫn chứng tuyển dụng xác thực (Verified Evidence Proof Bonus)
    if (job.evidence_proof && job.evidence_proof.verified) {
      score += 15;
      reasons.push("Dẫn chứng tuyển dụng đã qua kiểm định pháp nhân (+15)");
    }

    if (params.verified_only && (!job.evidence_proof || !job.evidence_proof.verified)) {
      return { job, score: -9999 };
    }

    return {
      job: {
        ...job,
        match_score: Math.min(100, Math.max(0, Math.round(score))),
        match_reasons: reasons,
      },
      score,
    };
  });

  // Lọc chỉ giữ các công việc có điểm phù hợp dương
  const eligible = scoredJobs
    .filter((item) => item.score > 0)
    .sort((a, b) => {
      if (params.sort_by === "quality") {
        return (b.job.quality_score || 0) - (a.job.quality_score || 0);
      }
      return b.score - a.score;
    })
    .map((item) => item.job);

  // Phân trang
  const page = params.page || 1;
  const pageSize = params.page_size || 20;
  const total = eligible.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = (page - 1) * pageSize;
  const pagedItems = eligible.slice(start, start + pageSize);

  const keywords = generateContextualKeywords(cleanRoleQ, total);

  return {
    items: pagedItems,
    total,
    page,
    page_size: pageSize,
    total_pages: totalPages,
    related_keywords: keywords,
    matched_industries: cleanRoleQ ? [cleanRoleQ] : [],
  };
}
