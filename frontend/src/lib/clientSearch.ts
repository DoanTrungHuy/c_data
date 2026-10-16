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

// Bảng từ đồng nghĩa vai trò và chuyên môn
const ROLE_SYNONYMS: Record<string, string[]> = {
  it: ["it", "cntt", "cong nghe thong tin", "information technology", "phan mem", "software", "lap trinh", "he thong", "mang", "support", "ky su cntt"],
  "it support": [
    "it support",
    "helpdesk",
    "ho tro ky thuat",
    "ky thuat vien cntt",
    "it officer",
    "quan tri he thong",
    "quan tri mang",
    "desktop support",
    "system admin",
  ],
  "it officer": ["it officer", "chuyen vien it", "nhan vien it", "it support", "quan tri he thong"],
  developer: ["developer", "lap trinh vien", "software engineer", "frontend", "backend", "fullstack", "react", "python", "node"],
  "ky su": ["ky su", "engineer", "ky su cntt", "ky su phan mem", "ky su mang", "ky su tu dong hoa", "ky su van hanh", "ky su he thong", "ky thuat vien"],
  "mang": ["mang", "network", "quan tri mang", "ha tang mang", "cisco", "ccna", "lan", "wan", "firewall", "router"],
  "phan mem": ["phan mem", "software", "lap trinh", "developer", "cntt", "react", "python", "backend", "frontend"],
  "khach san": ["khach san", "hotel", "resort", "wyndham", "flc", "novotel", "muong thanh", "sun world", "du thuyen", "yoko onsen"],
  "y te": ["y te", "benh vien", "vinmec", "bai chay", "his", "pacs", "duoc si", "dieu duong"],
  "cong nghiep": ["cong nghiep", "cang", "cict", "cai lan", "kcn", "calofic", "than", "tkv", "vinacomin", "nhiet dien"],
  "ke toan": ["ke toan", "accountant", "kiem toan", "thu quy", "ke toan tong hop", "ke toan kho", "ke toan thanh toan"],
  marketing: ["marketing", "truyen thong", "digital marketing", "seo", "ads", "content"],
  sales: ["sales", "kinh doanh", "ban hang", "tu van", "phat trien thi truong"],
};

// Từ đồng nghĩa địa danh
const LOCATION_SYNONYMS: Record<string, string[]> = {
  "ha long": ["ha long", "bai chay", "hong gai", "hong ha", "hong hai", "cai lan", "tuan chau", "quang ninh"],
  "quang ninh": ["quang ninh", "ha long", "cam pha", "uong bi", "dong trieu", "mong cai", "van don", "quang yen"],
  "ha noi": ["ha noi", "cau giay", "thanh xuan", "dong da", "ba dinh", "hai ba trung", "nam tu liem", "bac tu liem"],
  "ho chi minh": ["ho chi minh", "hcm", "sai gon", "quan 1", "quan 7", "tan binh", "thu duc", "binh thanh"],
  "da nang": ["da nang", "hai chau", "thanh khe", "son tra", "ngu hanh son"],
};

// Phân khu trọng điểm tại TP. Hạ Long & Quảng Ninh
const HALONG_LOCAL_ZONES: Record<string, string[]> = {
  "bai chay": ["bai chay", "wyndham", "sun world", "flc", "novotel", "khach san", "resort"],
  "cai lan": ["cai lan", "cict", "cang", "kcn", "calofic", "dong tau", "container"],
  "hon gai": ["hon gai", "hong gai", "cot 5", "benh vien", "vinmec", "le thanh tong", "bach dang"],
  "tuan chau": ["tuan chau", "du thuyen", "dao tuan chau", "cang tuan chau"],
  "cam pha": ["cam pha", "deo nai", "coc sau", "mong duong", "nhiet dien", "mo than"],
  "uong bi": ["uong bi", "yen tu", "dong mai"],
  "van don": ["van don", "san bay", "cai rong"],
};

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
      // Nếu đang trong môi trường Node.js (build time SSG)
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
        // Trong trình duyệt (Client-side)
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

// Danh sách các từ dừng phổ biến trong câu tìm kiếm việc làm tiếng Việt
const QUERY_STOP_WORDS = new Set([
  "tuyen", "tuyendung", "can", "cantuyen", "tim", "timviec",
  "viec", "vieclam", "job", "jobs", "tai", "o", "cho", "va", "nhung",
  "cac", "mot", "nhom", "doi", "cap", "khu", "vuc", "chuyen", "nhan"
]);

// Danh sách các địa danh / khu vực trọng điểm
const KNOWN_LOCATIONS = [
  "quang ninh", "ha long", "bai chay", "cai lan", "hon gai", "hong gai", "tuan chau",
  "cam pha", "uong bi", "dong trieu", "mong cai", "van don", "quang yen",
  "ha noi", "ho chi minh", "hcm", "sai gon", "da nang", "hai phong", "binh duong"
];

// Các âm tiết tiếng Việt đơn lẻ hay bị va chạm nhầm vào giữa các từ ghép (như 'toàn' trong 'an toàn', 'toàn thời gian')
const VIETNAMESE_SYLLABLE_COLLISIONS = new Set([
  "toan", "thiet", "hoan", "thanh", "dong", "nghiep", "phan", "mem", "vien", "nhan", "chuyen",
  "quan", "tri", "he", "thong", "bang", "bai", "cai", "hon", "gai", "ninh", "long", "kinh", "doanh"
]);

/**
 * Tìm kiếm Real-time (Client-side Search Engine)
 * Chạy ngay lập tức trong 2ms trên từng phím gõ của người dùng
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

  // Tách địa danh trong chuỗi tìm kiếm nếu có (ví dụ "IT Bãi Cháy" -> có "bai chay")
  let cleanQWithoutLoc = normQ;
  const matchedLocsInQ: string[] = [];
  for (const loc of KNOWN_LOCATIONS) {
    if (cleanQWithoutLoc.includes(loc)) {
      matchedLocsInQ.push(loc);
      cleanQWithoutLoc = cleanQWithoutLoc.replace(loc, " ");
    }
  }

  const allTokens = normQ.split(/\s+/).filter(Boolean);
  const cleanQTrimmed = cleanQWithoutLoc.trim();

  // Tập hợp các cụm từ / từ khóa nghiệp vụ mục tiêu
  const searchPhrases = new Set<string>();
  if (cleanQTrimmed) {
    searchPhrases.add(cleanQTrimmed);
  }

  for (const tok of cleanQTrimmed.split(/\s+/)) {
    if (tok && tok.length >= 3 && !VIETNAMESE_SYLLABLE_COLLISIONS.has(tok) && !QUERY_STOP_WORDS.has(tok)) {
      searchPhrases.add(tok);
    }
  }

  // Mở rộng từ đồng nghĩa vai trò/chuyên ngành
  for (const [key, synonyms] of Object.entries(ROLE_SYNONYMS)) {
    if (normQ === key || normQ.includes(key) || synonyms.some((s) => normQ === s || normQ.includes(s))) {
      synonyms.forEach((s) => searchPhrases.add(s));
    }
  }

  // Mở rộng vị trí địa lý
  const locationTokens = new Set<string>();
  if (normProvince) {
    locationTokens.add(normProvince);
    for (const [locKey, locSynonyms] of Object.entries(LOCATION_SYNONYMS)) {
      if (normProvince.includes(locKey) || locSynonyms.some((s) => normProvince.includes(s))) {
        locSynonyms.forEach((s) => locationTokens.add(s));
      }
    }
  }

  // Lọc danh sách nếu người dùng đang xem việc làm đã lưu
  let pool = allJobs;
  if (params.saved) {
    const savedIds = getSavedJobIds();
    pool = allJobs.filter((j) => savedIds.includes(String(j.id)));
  }

  // Chấm điểm và lọc ứng viên
  const scoredJobs = pool.map((job) => {
    let score = 0;
    const reasons: string[] = [];

    const normTitle = removeVietnameseTones(job.title || "");
    const normCompany = removeVietnameseTones(job.company_name || "");
    const normDesc = removeVietnameseTones(job.description || "");
    const normReq = removeVietnameseTones(job.requirements || "");
    const normCategory = removeVietnameseTones(job.category || "");
    const normLoc = removeVietnameseTones(
      `${job.location_province || ""} ${job.location_district || ""} ${job.location_full || ""}`
    );

    // 1. Kiểm tra vị trí địa lý (Hard filter nếu có chỉ định tỉnh thành)
    const locArray = Array.from(locationTokens);
    if (locArray.length > 0) {
      let locMatched = false;
      for (let i = 0; i < locArray.length; i++) {
        const loc = locArray[i];
        if (normLoc.includes(loc)) {
          locMatched = true;
          score += 25;
          reasons.push(`Thuộc khu vực phù hợp (${job.location_province || rawProvince}) (+25)`);
          break;
        }
      }
      if (!locMatched) {
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

    // 1.1 Khớp địa bàn trọng điểm nếu người dùng gõ trong ô tìm kiếm (ví dụ "IT Bãi Cháy", "Cảng Cái Lân")
    for (const [zoneKey, zoneKeywords] of Object.entries(HALONG_LOCAL_ZONES)) {
      if (normQ.includes(zoneKey) || zoneKeywords.some((z) => normQ.includes(z))) {
        const zoneMatched =
          normLoc.includes(zoneKey) ||
          normCompany.includes(zoneKey) ||
          zoneKeywords.some((z) => normLoc.includes(z) || normCompany.includes(z));
        if (zoneMatched) {
          score += 20;
          reasons.push(`Khớp chính xác khu vực trọng điểm (${zoneKey.toUpperCase()}) (+20)`);
        }
      }
    }

    // 2. Kiểm tra từ khóa chức danh & nhiệm vụ thực tế
    let queryMatched = false;
    let queryScore = 0;

    if (allTokens.length > 0) {
      if (searchPhrases.size > 0) {
        const phraseList = Array.from(searchPhrases);
        for (const phrase of phraseList) {
          if (normTitle.includes(phrase)) {
            queryMatched = true;
            queryScore += 45;
            reasons.push(`Chức danh khớp "${phrase}" (+45)`);
            break;
          } else if (normCompany.includes(phrase)) {
            queryMatched = true;
            queryScore += 35;
            reasons.push(`Khớp tên doanh nghiệp/đơn vị "${phrase}" (+35)`);
            break;
          } else if (normCategory.includes(phrase)) {
            queryMatched = true;
            queryScore += 25;
            reasons.push(`Khớp danh mục ngành nghề (+25)`);
            break;
          } else if (job.tech_stack && job.tech_stack.some((t) => removeVietnameseTones(t).includes(phrase))) {
            queryMatched = true;
            queryScore += 35;
            reasons.push(`Khớp công nghệ/kỹ năng "${phrase}" (+35)`);
            break;
          } else if (normDesc.includes(phrase) || normReq.includes(phrase)) {
            queryMatched = true;
            queryScore += 20;
            reasons.push(`Nội dung mô tả công việc có liên quan (+20)`);
            break;
          }
        }

        // BẮT BUỘC: Nếu người dùng đã gõ từ khóa mà không khớp bất kỳ cụm từ nghiệp vụ nào -> LOẠI BỎ NGAY LẬP TỨC!
        if (!queryMatched) {
          return {
            job: {
              ...job,
              match_score: 0,
              match_reasons: [],
            },
            score: -9999,
          };
        }
      } else if (matchedLocsInQ.length > 0) {
        // Người dùng chỉ gõ địa danh trong ô tìm kiếm (ví dụ "Bãi Cháy" hoặc "Cái Lân")
        const locInJob = matchedLocsInQ.some((l) => normLoc.includes(l) || normCompany.includes(l));
        if (!locInJob) {
          return {
            job: {
              ...job,
              match_score: 0,
              match_reasons: [],
            },
            score: -9999,
          };
        }
        queryMatched = true;
        queryScore += 30;
      }

      // Ràng buộc khắt khe (Strict mode)
      if (params.strict_mode && cleanQTrimmed) {
        const fullJobHaystack = `${normTitle} ${normCompany} ${normDesc} ${normReq} ${normLoc} ${normCategory}`;
        const hasAll = cleanQTrimmed.split(/\s+/).every((t) => fullJobHaystack.includes(t));
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
      // Khi không có từ khóa tìm kiếm (chế độ duyệt danh sách)
      score += 40;
    }

    // 3. Khớp ngành nghề lọc
    if (params.category) {
      const normCatParam = removeVietnameseTones(params.category);
      if (normCategory.includes(normCatParam)) {
        score += 20;
      } else {
        score -= 30;
      }
    }

    // 4. Khớp mức lương
    if (params.salary_min && (job.salary_max || job.salary_min || 0) < params.salary_min) {
      score -= 20;
    }
    if (params.salary_max && (job.salary_min || 0) > params.salary_max) {
      score -= 20;
    }

    // 5. Khớp nền tảng / hình thức làm việc
    if (params.job_type) {
      const normType = removeVietnameseTones(params.job_type);
      const normJobType = removeVietnameseTones(job.job_type || "");
      if (normJobType.includes(normType)) {
        score += 10;
      } else {
        score -= 20;
      }
    }

    // 6. Lọc theo Phân cấp chất lượng kiểm định (Diamond / Gold)
    if (params.quality_tier) {
      const qScore = job.quality_score || 0;
      if (params.quality_tier === "diamond" && qScore < 85) {
        return { job, score: -9999 };
      }
      if (params.quality_tier === "gold" && qScore < 70) {
        return { job, score: -9999 };
      }
    }

    // 7. Lọc theo Tech Stack / Kỹ năng công nghệ
    if (params.tech_stack) {
      const targetTech = removeVietnameseTones(params.tech_stack);
      const jobTechs = (job.tech_stack || []).map((t) => removeVietnameseTones(t));
      const hasTech = jobTechs.some((t) => t.includes(targetTech) || targetTech.includes(t));
      if (hasTech) {
        score += 35;
        reasons.push(`Khớp công nghệ yêu cầu: ${params.tech_stack} (+35)`);
      } else {
        score -= 25;
      }
    }

    // 8. Điểm cộng chất lượng: Ưu tiên các tin có độ uy tín & thông tin đầy đủ
    if (job.quality_score && job.quality_score >= 85) {
      score += 15;
      reasons.push(`Tin tuyển dụng thẩm định kim cương (${job.quality_score}/100đ) (+15)`);
    } else if (job.quality_score && job.quality_score >= 70) {
      score += 8;
    }

    // 9. Điểm cộng Dẫn chứng tuyển dụng xác thực (Verified Evidence Proof Bonus)
    if (job.evidence_proof && job.evidence_proof.verified) {
      score += 15;
      reasons.push("Dẫn chứng tuyển dụng đã qua kiểm định pháp nhân (+15)");
    }

    // 10. Lọc khắt khe nếu người dùng bật chế độ chỉ xem tin có dẫn chứng (Verified Only)
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
  let eligible = scoredJobs
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

  const keywords = total > 0 ? [
    "IT Support Hạ Long",
    "IT Officer Khách Sạn",
    "Kỹ sư CNTT Cái Lân",
    "Lập trình viên React",
    "Nhân viên IT Bãi Cháy",
    "Quản trị mạng hệ thống",
  ] : [];

  return {
    items: pagedItems,
    total,
    page,
    page_size: pageSize,
    total_pages: totalPages,
    related_keywords: keywords,
    matched_industries: [],
  };
}
