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
  it: ["it", "cntt", "cong nghe thong tin", "information technology", "phan mem", "software", "lap trinh", "he thong"],
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
  "ke toan": ["ke toan", "accountant", "kiem toan", "thu quy", "ke toan tong hop", "ke toan kho", "ke toan thanh toan"],
  marketing: ["marketing", "truyen thong", "digital marketing", "seo", "ads", "content"],
  "sales": ["sales", "kinh doanh", "ban hang", "tu van", "phat trien thi truong"],
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

  // Tạo tập từ khóa mở rộng thông minh
  const searchTokens = normQ.split(/\s+/).filter(Boolean);
  const expandedTokens = new Set<string>(searchTokens);

  for (const [key, synonyms] of Object.entries(ROLE_SYNONYMS)) {
    if (normQ.includes(key) || synonyms.some((s) => normQ.includes(s))) {
      synonyms.forEach((s) => expandedTokens.add(s));
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
          score += 35;
          reasons.push(`Thuộc khu vực phù hợp (${job.location_province || rawProvince}) (+35)`);
          break;
        }
      }
      if (!locMatched) {
        // Tỉnh thành yêu cầu hoàn toàn không khớp -> LOẠI BỎ NGAY LẬP TỨC (Hard Exclusion)
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
          score += 45;
          reasons.push(`Khớp chính xác khu vực trọng điểm (${zoneKey.toUpperCase()}) (+45)`);
        }
      }
    }

    // 1.2 Nếu từ khóa q chứa tên tỉnh thành (ví dụ người dùng gõ "Hà Nội" trong ô tìm kiếm)
    for (const [locKey, locSynonyms] of Object.entries(LOCATION_SYNONYMS)) {
      if (normQ.includes(locKey) || locSynonyms.some((s) => normQ.includes(s))) {
        const locInJob = normLoc.includes(locKey) || locSynonyms.some((s) => normLoc.includes(s));
        if (locInJob) {
          score += 30;
          reasons.push(`Khớp địa bàn trong từ khóa (${locKey.toUpperCase()}) (+30)`);
        } else {
          score -= 50; // Trừ điểm nặng nếu người dùng gõ đích danh địa bàn mà việc làm ở nơi khác
        }
      }
    }

    // 2. Kiểm tra từ khóa chức danh & nhiệm vụ thực tế
    if (searchTokens.length > 0) {
      let titleHits = 0;
      let descHits = 0;

      // Khớp chính xác cả cụm
      if (normTitle.includes(normQ)) {
        score += 40;
        reasons.push(`Chức danh khớp trực tiếp "${rawQ}" (+40)`);
      } else {
        // Khớp từng từ hoặc từ đồng nghĩa
        const expArray = Array.from(expandedTokens);
        for (let i = 0; i < expArray.length; i++) {
          const token = expArray[i];
          if (normTitle.includes(token)) {
            titleHits++;
          }
          if (normDesc.includes(token) || normReq.includes(token)) {
            descHits++;
          }
        }

        if (titleHits > 0) {
          score += Math.min(30, titleHits * 12);
          reasons.push(`Chức danh có từ khóa chuyên môn phù hợp (+${Math.min(30, titleHits * 12)})`);
        }
        if (descHits > 0) {
          score += Math.min(20, descHits * 5);
          reasons.push(`Mô tả công việc có các trách nhiệm kỹ thuật phù hợp (+${Math.min(20, descHits * 5)})`);
        }
      }

      if (normCompany.includes(normQ)) {
        score += 20;
        reasons.push(`Khớp tên doanh nghiệp/khách sạn (+20)`);
      }

      if (normCategory.includes(normQ)) {
        score += 15;
      }

      // Ràng buộc khắt khe (Strict mode)
      if (params.strict_mode) {
        const fullJobHaystack = `${normTitle} ${normCompany} ${normDesc} ${normReq} ${normLoc} ${normCategory}`;
        const hasAll = searchTokens.every((t) => fullJobHaystack.includes(t));
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
    } else {
      // Khi không có từ khóa tìm kiếm thì điểm cơ sở
      score += 10;
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

    return {
      job: {
        ...job,
        match_score: Math.max(0, score),
        match_reasons: reasons,
      },
      score,
    };
  });

  // Lọc chỉ giữ các công việc có điểm phù hợp dương (hoặc hiển thị tất cả nếu không có query)
  let eligible = scoredJobs
    .filter((item) => (normQ || normProvince ? item.score > 0 : true))
    .sort((a, b) => b.score - a.score)
    .map((item) => item.job);

  // Phân trang
  const page = params.page || 1;
  const pageSize = params.page_size || 20;
  const total = eligible.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = (page - 1) * pageSize;
  const pagedItems = eligible.slice(start, start + pageSize);

  const keywords = [
    "IT Support Hạ Long",
    "IT Officer Khách Sạn",
    "Kỹ sư CNTT Cái Lân",
    "Lập trình viên React",
    "Nhân viên IT Bãi Cháy",
    "Quản trị mạng hệ thống",
  ];

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
