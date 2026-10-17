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

/**
 * Thuật toán Damerau-Levenshtein Edit Distance (Hỗ trợ chuyển đổi vị trí 2 ký tự kế tiếp - Transposition)
 * Dùng cho tính năng Typo Tolerance tương tự Meilisearch / Elasticsearch
 */
export function damerauLevenshtein(a: string, b: string): number {
  if (a === b) return 0;
  const lenA = a.length;
  const lenB = b.length;
  if (Math.abs(lenA - lenB) > 2) return Math.abs(lenA - lenB);
  if (lenA === 0) return lenB;
  if (lenB === 0) return lenA;

  const d: number[][] = [];
  for (let i = 0; i <= lenA; i++) {
    d[i] = [i];
  }
  for (let j = 0; j <= lenB; j++) {
    d[0][j] = j;
  }

  for (let i = 1; i <= lenA; i++) {
    for (let j = 1; j <= lenB; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(
        d[i - 1][j] + 1, // deletion
        d[i][j - 1] + 1, // insertion
        d[i - 1][j - 1] + cost // substitution
      );
      // Transposition
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + cost);
      }
    }
  }
  return d[lenA][lenB];
}

// Bảng từ đồng nghĩa vai trò và chuyên môn có trọng tâm chính xác (Precise Role Taxonomy)
const PRECISE_ROLE_SYNONYMS: Record<string, string[]> = {
  it: ["it", "cntt", "cong nghe thong tin", "information technology"],
  cntt: ["cntt", "it", "cong nghe thong tin", "information technology"],
  "it support": [
    "it support",
    "helpdesk",
    "ho tro ky thuat",
    "ky thuat vien cntt",
    "desktop support",
    "it helpdesk",
    "it officer",
  ],
  helpdesk: [
    "helpdesk",
    "it helpdesk",
    "it support",
    "ho tro ky thuat",
    "desktop support",
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
    "coder",
  ],
  coder: ["coder", "developer", "lap trinh vien", "software engineer"],
  frontend: [
    "frontend",
    "front-end",
    "react",
    "vue",
    "nextjs",
    "next.js",
    "ui developer",
  ],
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
  react: ["react", "reactjs", "react.js", "frontend", "nextjs", "next.js"],
  python: ["python", "fastapi", "django", "backend"],
  ke_toan: ["ke toan", "accountant", "kiem toan", "thu quy"],
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
  hr: ["hr", "nhan su", "human resources", "tuyen dung", "c&b"],
  "lai xe": ["lai xe", "tai xe", "lai xe b2", "lai xe du lich", "lai xe 16 cho"],
  "bao ve": ["bao ve", "an ninh", "ve si", "tuan tra", "an ninh toa nha"],
  "an toan thong tin": [
    "an toan thong tin",
    "cyber security",
    "information security",
    "soc",
    "attt",
  ],
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

// Từ dừng tìm kiếm việc làm tiếng Việt (Search Intent Stopwords - Algolia Query Rules)
const SEARCH_INTENT_STOPWORDS = new Set([
  "tuyen",
  "dung",
  "tuyen dung",
  "can",
  "can tuyen",
  "tim",
  "tim viec",
  "tim viec lam",
  "viec",
  "viec lam",
  "chuc danh",
  "vi tri",
  "chuyen vien",
  "tai",
  "o",
  "trong",
  "va",
  "cho",
  "cua",
  "cac",
  "nhung",
  "cap do",
]);

// Phân cấp địa danh: Phường/Xã/Khu vực -> Quận/Huyện/Thị xã/Thành phố -> Tỉnh
const WARD_ALIASES: Record<string, string[]> = {
  "bai chay": ["bai chay", "wyndham", "novotel", "sun world", "ha long bay view", "ha long", "quang ninh"],
  "cai lan": ["cai lan", "cict", "cang cai lan", "kcn cai lan", "calofic", "ha long", "quang ninh"],
  "hon gai": ["hon gai", "hong gai", "cot 5", "benh vien da khoa tinh", "vinmec ha long", "ha long", "quang ninh"],
  "hong gai": ["hon gai", "hong gai", "cot 5", "benh vien da khoa tinh", "vinmec ha long", "ha long", "quang ninh"],
  "tuan chau": ["tuan chau", "dao tuan chau", "cang tuan chau", "ha long", "quang ninh"],
  "dong trieu": ["dong trieu", "mao khe", "quang ninh"],
  "cam pha": ["cam pha", "quang hanh", "yoko onsen", "mong duong", "coc sau", "deo nai", "quang ninh"],
  "uong bi": ["uong bi", "yen tu", "quang ninh"],
  "mong cai": ["mong cai", "tra co", "quang ninh"],
  "van don": ["van don", "san bay van don", "cai rong", "quang ninh"],
  "quang yen": ["quang yen", "kcn amata", "dong mai", "song khoai", "quang ninh"],
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
    "quang ninh", // Hạ Long thuộc tỉnh Quảng Ninh
  ],
  "cam pha": ["cam pha", "quang hanh", "yoko onsen", "mong duong", "coc sau", "deo nai", "quang ninh"],
  "uong bi": ["uong bi", "yen tu", "quang ninh"],
  "dong trieu": ["dong trieu", "mao khe", "quang ninh"],
  "mong cai": ["mong cai", "tra co", "quang ninh"],
  "van don": ["van don", "cai rong", "san bay van don", "quang ninh"],
  "quang yen": ["quang yen", "kcn amata", "dong mai", "song khoai", "quang ninh"],
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
    "hong gai",
    "tuan chau",
    "song khoai",
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
    "hoan kiem",
    "ha dong",
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
    "quan 3",
  ],
  "da nang": ["da nang", "hai chau", "thanh khe", "son tra", "ngu hanh son"],
  "hai phong": ["hai phong", "ngo quyen", "le chan", "hong bang", "dinh vu"],
  "binh duong": ["binh duong", "thu dau mot", "di an", "thuan an", "vsip"],
  "bac ninh": ["bac ninh", "tu son", "yen phong", "que vo"],
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
  "cau giay",
  "thanh xuan",
  "nam tu liem",
  "ha noi",
  "ho chi minh",
  "hcm",
  "sai gon",
  "da nang",
  "hai phong",
  "binh duong",
  "bac ninh",
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
 * Phân tích câu truy vấn (Search Query Intent Parser)
 * Bóc tách: địa danh, từ khóa vai trò, loại bỏ stopwords ý định tìm việc
 */
export function parseSearchQuery(rawQuery: string): {
  cleanRoleQuery: string;
  roleTokens: string[];
  detectedLocation: string;
  isMultiWord: boolean;
} {
  let norm = removeVietnameseTones(rawQuery);

  // 1. Nhận diện và tách địa danh nếu có trong câu truy vấn
  let detectedLoc = "";
  for (const loc of KNOWN_LOCATIONS_ORDERED) {
    // Ranh giới từ hoặc cụm từ
    const locPattern = new RegExp(`(^|\\s)${loc}(\\s|$)`, "i");
    if (locPattern.test(norm)) {
      detectedLoc = loc;
      norm = norm.replace(locPattern, " ").replace(/\s+/g, " ").trim();
      break;
    }
  }

  // 2. Tách từ và loại bỏ các stopwords ý định tìm kiếm
  const rawTokens = norm.split(/[\s,./\-_+()]+/).filter(Boolean);
  const filteredTokens: string[] = [];

  for (let i = 0; i < rawTokens.length; i++) {
    const t = rawTokens[i];
    // Giữ lại các từ viết tắt chuyên ngành quan trọng dù ngắn
    if (["it", "ai", "qa", "qc", "ui", "ux", "hr"].includes(t)) {
      filteredTokens.push(t);
      continue;
    }
    // Ghép 2 từ kiểm tra stopwords (ví dụ "tuyen dung", "viec lam", "tim viec")
    if (i < rawTokens.length - 1) {
      const pair = `${t} ${rawTokens[i + 1]}`;
      if (SEARCH_INTENT_STOPWORDS.has(pair)) {
        i++; // bỏ cả cặp
        continue;
      }
    }
    if (!SEARCH_INTENT_STOPWORDS.has(t)) {
      filteredTokens.push(t);
    }
  }

  const cleanRoleQuery = filteredTokens.join(" ").trim();
  return {
    cleanRoleQuery,
    roleTokens: filteredTokens,
    detectedLocation: detectedLoc,
    isMultiWord: filteredTokens.length > 1,
  };
}

/**
 * Kiểm tra đối sánh vị trí địa lý nghiêm ngặt (Strict Location Guardrails)
 * Không bao giờ cho phép rò rỉ việc làm Hà Nội sang Quảng Ninh hoặc ngược lại
 */
export function isLocationMatching(
  normLocText: string,
  targetLocTokens: Set<string> | null,
  detectedLoc: string
): boolean {
  if (!targetLocTokens || targetLocTokens.size === 0) {
    return true; // Không có yêu cầu địa điểm
  }

  // 1. Kiểm tra loại trừ xung đột tỉnh thành
  const isTargetQuangNinh =
    detectedLoc === "quang ninh" ||
    detectedLoc === "ha long" ||
    detectedLoc === "bai chay" ||
    detectedLoc === "cai lan" ||
    detectedLoc === "hon gai";

  const isTargetHaNoi = detectedLoc === "ha noi" || detectedLoc === "cau giay";

  if (isTargetQuangNinh) {
    // Nếu target là Quảng Ninh/Hạ Long, loại ngay nếu job ở Hà Nội hoặc HCM mà không có Quảng Ninh/Hạ Long
    const hasHaNoiOnly =
      normLocText.includes("ha noi") &&
      !normLocText.includes("quang ninh") &&
      !normLocText.includes("ha long") &&
      !normLocText.includes("bai chay");
    if (hasHaNoiOnly) return false;

    const hasHcmOnly =
      (normLocText.includes("ho chi minh") || normLocText.includes("sai gon")) &&
      !normLocText.includes("quang ninh") &&
      !normLocText.includes("ha long");
    if (hasHcmOnly) return false;
  }

  if (isTargetHaNoi) {
    const hasQnOnly =
      normLocText.includes("quang ninh") && !normLocText.includes("ha noi");
    if (hasQnOnly) return false;
  }

  // 2. Kiểm tra có chứa ít nhất một alias của khu vực đích
  for (const token of Array.from(targetLocTokens)) {
    if (normLocText.includes(token)) {
      return true;
    }
  }

  return false;
}

/**
 * Thuật toán tìm kiếm & xếp hạng toàn diện (Unified Open Source Search Engine)
 * Tích hợp: Okapi BM25 + Damerau-Levenshtein Typo Tolerance + N-Gram Phrase Matching + Strict Location Guardrails
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
  const rawProvince = (params.province || "").trim();

  // 1. Phân tích Intent và bóc tách Địa danh / Vai trò
  const {
    cleanRoleQuery,
    roleTokens,
    detectedLocation,
    isMultiWord,
  } = parseSearchQuery(rawQ);
  const cleanRoleQ = cleanRoleQuery;

  // 2. Xác định token vị trí địa lý bắt buộc
  let effectiveLoc = detectedLocation;
  if (!effectiveLoc && rawProvince) {
    effectiveLoc = removeVietnameseTones(rawProvince);
  }

  const targetLocTokens = effectiveLoc ? getTargetLocationTokens(effectiveLoc) : null;

  // 3. Lọc pool việc làm đã lưu nếu cần
  let pool = allJobs;
  if (params.saved) {
    const savedIds = getSavedJobIds();
    pool = allJobs.filter((j) => savedIds.includes(String(j.id)));
  }

  // 4. BM25 Precomputation: Tính Term Frequency & IDF cho corpus
  const N = pool.length || 1;
  const docTermFreqs: Array<{
    titleTokens: string[];
    techTokens: string[];
    companyTokens: string[];
    catTokens: string[];
    descTokens: string[];
    reqTokens: string[];
    allTokens: Set<string>;
  }> = [];

  const dfMap = new Map<string, number>();

  for (const job of pool) {
    const tTokens = removeVietnameseTones(job.title || "").split(/[\s,./\-_+()]+/).filter(Boolean);
    const techTokens = (job.tech_stack || []).map((t) => removeVietnameseTones(t)).filter(Boolean);
    const compTokens = removeVietnameseTones(job.company_name || "").split(/[\s,./\-_+()]+/).filter(Boolean);
    const catTokens = removeVietnameseTones(job.category || "").split(/[\s,./\-_+()]+/).filter(Boolean);
    const descTokens = removeVietnameseTones(job.description || "").split(/[\s,./\-_+()]+/).filter(Boolean);
    const reqTokens = removeVietnameseTones(job.requirements || "").split(/[\s,./\-_+()]+/).filter(Boolean);

    const docTerms = new Set<string>([
      ...tTokens,
      ...techTokens,
      ...compTokens,
      ...catTokens,
      ...descTokens.slice(0, 50),
      ...reqTokens.slice(0, 50),
    ]);

    docTerms.forEach((term) => {
      dfMap.set(term, (dfMap.get(term) || 0) + 1);
    });

    docTermFreqs.push({
      titleTokens: tTokens,
      techTokens,
      companyTokens: compTokens,
      catTokens,
      descTokens,
      reqTokens,
      allTokens: docTerms,
    });
  }

  const idf = (term: string): number => {
    const df = dfMap.get(term) || 0;
    return Math.log(1 + (N - df + 0.5) / (df + 0.5));
  };

  // 5. Chấm điểm từng tin tuyển dụng (Multi-Signal Scoring)
  const scoredJobs = pool.map((job, idx) => {
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

    // A. BẮT BUỘC KHỚP VỊ TRÍ ĐỊA LÝ (Hard Geographic Boundary)
    if (targetLocTokens) {
      const locMatch = isLocationMatching(
        `${normLoc} ${normCompany} ${normTitle}`,
        targetLocTokens,
        effectiveLoc
      );
      if (!locMatch) {
        return { job, score: -9999 };
      }
      score += 25;
      reasons.push(`Khu vực tuyển dụng phù hợp (+25)`);
    }

    // B. KHỚP TỪ KHÓA NGHỀ NGHIỆP / CÔNG VIỆC
    if (cleanRoleQ) {
      let queryScore = 0;

      // Tier 1: Khớp chức danh chính xác tuyệt đối (Exact Title Match)
      if (normTitle === cleanRoleQ) {
        queryScore = 140;
        reasons.push(`Chức danh chính xác tuyệt đối "${job.title}" (+140)`);
      }
      // Tier 2: Tiêu đề chứa nguyên văn cụm tìm kiếm (Phrase Substring in Title)
      else if (normTitle.includes(cleanRoleQ)) {
        queryScore = 110;
        reasons.push(`Tiêu đề chứa nguyên cụm "${cleanRoleQ}" (+110)`);
      }
      // Tier 3: Tất cả các từ trong query đều có mặt trong tiêu đề (All Query Tokens in Title)
      else if (
        isMultiWord &&
        roleTokens.every((t) => {
          if (["it", "ai", "qa", "qc"].includes(t)) {
            return new RegExp(`(^|\\s|\\/|\\()${t}($|\\s|\\/|\\))`).test(normTitle);
          }
          return normTitle.includes(t);
        })
      ) {
        queryScore = 95;
        reasons.push(`Tiêu đề chứa đủ các từ khóa "${cleanRoleQ}" (+95)`);
      }
      // Tier 4: Khớp từ đồng nghĩa chuyên môn (Semantic Role Synonyms)
      else {
        for (const [key, synList] of Object.entries(PRECISE_ROLE_SYNONYMS)) {
          const userMatchesRole = cleanRoleQ === key || synList.includes(cleanRoleQ);
          if (userMatchesRole) {
            for (const syn of synList) {
              if (
                normTitle.includes(syn) ||
                (isMultiWord && syn.split(/\s+/).every((st) => normTitle.includes(st)))
              ) {
                queryScore = 85;
                reasons.push(`Tiêu đề khớp vị trí tương đương "${syn}" (+85)`);
                break;
              }
            }
            if (queryScore > 0) break;
          }
        }
      }

      // Tier 5: Khớp kỹ năng công nghệ (Tech Stack Match)
      if (
        queryScore === 0 &&
        techStackNorm.some((t) => {
          if (t === cleanRoleQ || cleanRoleQ.includes(t) || t.includes(cleanRoleQ)) return true;
          // Typo tolerance trên tech stack
          if (
            cleanRoleQ.length >= 4 &&
            Math.abs(cleanRoleQ.length - t.length) <= 1 &&
            damerauLevenshtein(cleanRoleQ, t) <= 1
          ) {
            return true;
          }
          return false;
        })
      ) {
        queryScore = 75;
        reasons.push(`Khớp công nghệ tuyển dụng chuyên sâu (+75)`);
      }

      // Tier 6: Khớp tên doanh nghiệp (Company Name Match)
      if (queryScore === 0 && normCompany.includes(cleanRoleQ)) {
        queryScore = 70;
        reasons.push(`Khớp tên doanh nghiệp "${job.company_name}" (+70)`);
      }

      // Tier 7: Từ đơn đặc thù (Single Acronym or Keyword in Title / Category)
      if (queryScore === 0 && !isMultiWord) {
        if (cleanRoleQ === "it" || cleanRoleQ === "cntt") {
          const itRegex = /(?:^|\s|\/|\()(it|cntt)(?:$|\s|\/|\))/i;
          if (itRegex.test(normTitle)) {
            queryScore = 65;
            reasons.push(`Tiêu đề định danh vị trí CNTT / IT (+65)`);
          } else if (normCategory.includes("cong nghe thong tin") || normCategory.includes("it")) {
            queryScore = 45;
            reasons.push(`Khớp danh mục ngành Công nghệ thông tin (+45)`);
          }
        } else {
          // Khớp từ đơn trong tiêu đề hoặc danh mục
          if (normTitle.includes(cleanRoleQ)) {
            queryScore = 65;
            reasons.push(`Tiêu đề chứa từ khóa "${cleanRoleQ}" (+65)`);
          } else if (normCategory.includes(cleanRoleQ)) {
            queryScore = 45;
            reasons.push(`Khớp danh mục ngành nghề (+45)`);
          }
        }
      }

      // Tier 8: Okapi BM25 Multi-Field Term Frequency Scoring
      if (queryScore === 0) {
        let bm25Total = 0;
        const dfs = docTermFreqs[idx];

        for (const token of roleTokens) {
          const termIdf = idf(token);
          if (termIdf <= 0) continue;

          let termScore = 0;
          // Title field (weight 10)
          if (dfs.titleTokens.includes(token)) termScore += 10.0 * termIdf;
          // Tech field (weight 6)
          if (dfs.techTokens.includes(token)) termScore += 6.0 * termIdf;
          // Category (weight 4)
          if (dfs.catTokens.includes(token)) termScore += 4.0 * termIdf;
          // Company (weight 3)
          if (dfs.companyTokens.includes(token)) termScore += 3.0 * termIdf;
          // Req & Desc (weight 1.5)
          if (dfs.reqTokens.includes(token) || dfs.descTokens.includes(token)) {
            termScore += 1.5 * termIdf;
          }

          // Damerau-Levenshtein Fuzzy Match if not exact
          if (termScore === 0 && token.length >= 4) {
            const hasFuzzyTitle = dfs.titleTokens.some(
              (tt) => Math.abs(token.length - tt.length) <= 1 && damerauLevenshtein(token, tt) <= 1
            );
            if (hasFuzzyTitle) {
              termScore += 7.0 * termIdf;
              reasons.push(`Khớp gần đúng (Typo Tolerance: ${token}) (+35)`);
            }
          }

          bm25Total += termScore;
        }

        if (bm25Total >= 8.0) {
          queryScore = Math.min(60, Math.round(bm25Total * 3));
          reasons.push(`BM25 đa trường: Tiêu đề + Kỹ năng (+${queryScore})`);
        }
      }

      // Tier 9: Khớp trong mô tả / yêu cầu công việc (Gated)
      if (queryScore === 0) {
        if (isMultiWord) {
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

      // NẾU CÓ TỪ KHÓA MÀ KHÔNG KHỚP BẤT KỲ TIÊU CHÍ NÀO -> LOẠI BỎ
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

      // Ràng buộc chế độ khắt khe (Strict mode)
      if (params.strict_mode) {
        const fullHaystack = `${normTitle} ${normCompany} ${normDesc} ${normReq} ${normLoc} ${normCategory}`;
        const hasAll = roleTokens.every((t) => fullHaystack.includes(t));
        if (!hasAll) {
          return { job, score: -9999 };
        }
      }

      score += queryScore;
    } else {
      // Khi không có từ khóa (duyệt danh sách theo địa điểm / bộ lọc)
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
      const hasTech = techStackNorm.some(
        (t) => t.includes(targetTech) || targetTech.includes(t)
      );
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
