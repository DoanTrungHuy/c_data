import axios from "axios";
import {
  Job,
  Company,
  Province,
  JobSearchParams,
  JobListResponse,
  DashboardStats,
} from "@/types/job";

// Determine base API URL:
// In browser: use relative /api/v1 (which next.config.js proxies) or NEXT_PUBLIC_API_URL
// On server: use internal Docker container URL API_URL or fallback to localhost
function getBaseUrl(): string {
  // Ưu tiên biến môi trường NEXT_PUBLIC_API_URL nếu được cấu hình (ví dụ khi deploy Vercel / Cloud)
  if (process.env.NEXT_PUBLIC_API_URL) {
    const clean = process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, "");
    return clean.endsWith("/api/v1") ? clean : `${clean}/api/v1`;
  }

  // Trong trình duyệt (client-side) không có biến môi trường thì dùng relative rewrite
  if (typeof window !== "undefined") {
    return "/api/v1";
  }

  // Trên server SSR
  if (process.env.API_URL) {
    const clean = process.env.API_URL.replace(/\/+$/, "");
    return clean.endsWith("/api/v1") ? clean : `${clean}/api/v1`;
  }
  return "http://localhost:8000/api/v1";
}

export const apiClient = axios.create({
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Interceptor to dynamically set baseURL depending on environment
apiClient.interceptors.request.use((config) => {
  if (!config.baseURL) {
    config.baseURL = getBaseUrl();
  }
  return config;
});

// Mock/fallback sample jobs for graceful degradation if backend is warming up or empty
const SAMPLE_FALLBACK_JOBS: Job[] = [
  {
    id: 1,
    title: "Senior Frontend Engineer (React/Next.js/TypeScript)",
    company_name: "Tập Đoàn Công Nghệ VNG",
    description: `<h3>Mô tả công việc</h3>
<p>Chúng tôi đang tìm kiếm Senior Frontend Engineer tài năng đồng hành cùng các sản phẩm triệu người dùng tại Việt Nam.</p>
<ul>
  <li>Phát triển các tính năng mới cho nền tảng web bằng Next.js, React, TypeScript.</li>
  <li>Tối ưu hóa hiệu năng website, Core Web Vitals và SEO.</li>
  <li>Phối hợp cùng Product Manager và Designer xây dựng trải nghiệm người dùng mượt mà.</li>
  <li>Review code và hướng dẫn các kỹ sư junior trong nhóm.</li>
</ul>`,
    requirements: `<h3>Yêu cầu ứng viên</h3>
<ul>
  <li>Tối thiểu 3+ năm kinh nghiệm làm việc với React.js, Next.js, TypeScript.</li>
  <li>Thành thạo Tailwind CSS, HTML5, CSS3, Responsive design.</li>
  <li>Hiểu sâu về SSR, SSG, ISR và caching trong Next.js.</li>
  <li>Kinh nghiệm với RESTful API, GraphQL và State Management.</li>
</ul>`,
    salary_min: 30000000,
    salary_max: 55000000,
    salary_text: "30 - 55 triệu VNĐ",
    location_province: "Hồ Chí Minh",
    location_district: "Quận 7",
    location_full: "Tòa nhà VNG Campus, Tân Thuận Đông, Quận 7, TP. HCM",
    job_type: "Toàn thời gian",
    category: "Công nghệ thông tin / Phần mềm",
    experience_level: "Senior (3 - 5 năm)",
    source_platform: "TopCV",
    source_url: "https://topcv.vn",
    posted_at: new Date(Date.now() - 3600000 * 4).toISOString(),
    expires_at: new Date(Date.now() + 86400000 * 30).toISOString(),
    is_active: true,
  },
  {
    id: 2,
    title: "Chuyên Viên Digital Marketing & Growth Hacking",
    company_name: "Sun Group - Vùng Đông Bắc",
    description: `<h3>Mô tả công việc</h3>
<p>Triển khai các chiến dịch tiếp thị số cho các quần thể du lịch nghỉ dưỡng hàng đầu tại Quảng Ninh và miền Bắc.</p>
<ul>
  <li>Lên kế hoạch và thực thi chiến dịch quảng cáo đa kênh: Meta Ads, Google Ads, TikTok Ads.</li>
  <li>Theo dõi, đo lường và tối ưu chi phí chuyển đổi (CPA, ROAS).</li>
  <li>Xây dựng nội dung viral và chiến lược SEO trên website.</li>
</ul>`,
    requirements: `<h3>Yêu cầu ứng viên</h3>
<ul>
  <li>2+ năm kinh nghiệm trong lĩnh vực Digital Marketing, ưu tiên ngành Du lịch / Dịch vụ.</li>
  <li>Có tư duy dữ liệu tốt, thành thạo Google Analytics 4, Meta Business Suite.</li>
  <li>Sáng tạo, chủ động và có tinh thần trách nhiệm cao.</li>
</ul>`,
    salary_min: 15000000,
    salary_max: 25000000,
    salary_text: "15 - 25 triệu VNĐ",
    location_province: "Quảng Ninh",
    location_district: "Thành phố Hạ Long",
    location_full: "Bãi Cháy, TP. Hạ Long, Quảng Ninh",
    job_type: "Toàn thời gian",
    category: "Marketing / Truyền thông / PR",
    experience_level: "Middle (1 - 3 năm)",
    source_platform: "VietnamWorks",
    source_url: "https://vietnamworks.com",
    posted_at: new Date(Date.now() - 3600000 * 12).toISOString(),
    expires_at: new Date(Date.now() + 86400000 * 25).toISOString(),
    is_active: true,
  },
  {
    id: 3,
    title: "Kỹ Sư Backend Python (FastAPI / PostgreSQL)",
    company_name: "FPT Software",
    description: `<h3>Mô tả công việc</h3>
<p>Tham gia phát triển hệ thống lõi xử lý dữ liệu lớn và các microservices cho khách hàng quốc tế.</p>
<ul>
  <li>Xây dựng API hiệu năng cao với Python (FastAPI / Django).</li>
  <li>Thiết kế cơ sở dữ liệu PostgreSQL, tối ưu truy vấn SQL và indexing.</li>
  <li>Tích hợp message broker Redis, Celery và RabbitMQ.</li>
</ul>`,
    requirements: `<h3>Yêu cầu ứng viên</h3>
<ul>
  <li>Thành thạo Python và các framework web như FastAPI, Django.</li>
  <li>Nắm vững nguyên lý hướng đối tượng, Clean Architecture, RESTful API.</li>
  <li>Có kinh nghiệm với Docker, Git, CI/CD là lợi thế.</li>
</ul>`,
    salary_min: 22000000,
    salary_max: 40000000,
    salary_text: "22 - 40 triệu VNĐ",
    location_province: "Hà Nội",
    location_district: "Cầu Giấy",
    location_full: "Tòa nhà FPT Cầu Giấy, Duy Tân, Hà Nội",
    job_type: "Toàn thời gian",
    category: "Công nghệ thông tin / Phần mềm",
    experience_level: "Middle / Senior",
    source_platform: "ITviec",
    source_url: "https://itviec.com",
    posted_at: new Date(Date.now() - 3600000 * 24).toISOString(),
    expires_at: new Date(Date.now() + 86400000 * 20).toISOString(),
    is_active: true,
  },
  {
    id: 4,
    title: "Trưởng Nhóm Kinh Doanh Bất Động Sản Nghỉ Dưỡng",
    company_name: "BIM Group",
    description: `<h3>Mô tả công việc</h3>
<p>Quản lý đội ngũ tư vấn và bán các dự án bất động sản cao cấp ven vịnh Hạ Long.</p>
<ul>
  <li>Xây dựng và phát triển đội ngũ kinh doanh 8 - 12 nhân viên.</li>
  <li>Mở rộng mạng lưới khách hàng VIP và đối tác đầu tư.</li>
  <li>Đảm bảo chỉ tiêu doanh số hàng tháng và quý của nhóm.</li>
</ul>`,
    requirements: `<h3>Yêu cầu ứng viên</h3>
<ul>
  <li>Kinh nghiệm tối thiểu 3 năm trong lĩnh vực BĐS, ít nhất 1 năm vị trí Team Leader.</li>
  <li>Kỹ năng đàm phán, thuyết trình và chốt deal xuất sắc.</li>
  <li>Tác phong chuyên nghiệp, hiểu biết thị trường BĐS Quảng Ninh và phía Bắc.</li>
</ul>`,
    salary_min: 25000000,
    salary_max: 60000000,
    salary_text: "25 - 60 triệu + Hoa hồng cao",
    location_province: "Quảng Ninh",
    location_district: "Thành phố Hạ Long",
    location_full: "Bán đảo 2, Khu đô thị Halong Marina, Hùng Thắng, Hạ Long",
    job_type: "Toàn thời gian",
    category: "Kinh doanh / Bán hàng",
    experience_level: "Quản lý / Trưởng nhóm",
    source_platform: "CareerViet",
    source_url: "https://careerviet.vn",
    posted_at: new Date(Date.now() - 3600000 * 36).toISOString(),
    expires_at: new Date(Date.now() + 86400000 * 15).toISOString(),
    is_active: true,
  },
  {
    id: 5,
    title: "Kế Toán Tổng Hợp & Thuế Doanh Nghiệp",
    company_name: "Công ty Cổ phần May Sông Hồng",
    description: `<h3>Mô tả công việc</h3>
<p>Kiểm tra, rà soát chứng từ, lập báo cáo thuế và báo cáo tài chính định kỳ theo chuẩn mực kế toán Việt Nam.</p>`,
    requirements: `<h3>Yêu cầu ứng viên</h3>
<ul>
  <li>Tốt nghiệp Đại học chuyên ngành Kế toán - Kiểm toán - Tài chính.</li>
  <li>Sử dụng thành thạo phần mềm kế toán MISA, Bravo và Excel nâng cao.</li>
  <li>Chăm chỉ, cẩn thận, trung thực và chịu được áp lực mùa quyết toán.</li>
</ul>`,
    salary_min: 12000000,
    salary_max: 18000000,
    salary_text: "12 - 18 triệu VNĐ",
    location_province: "Hà Nội",
    location_district: "Thanh Xuân",
    location_full: "Nguyễn Trãi, Thanh Xuân, Hà Nội",
    job_type: "Toàn thời gian",
    category: "Kế toán / Kiểm toán / Thuế",
    experience_level: "1 - 3 năm",
    source_platform: "TopCV",
    source_url: "https://topcv.vn",
    posted_at: new Date(Date.now() - 3600000 * 48).toISOString(),
    expires_at: new Date(Date.now() + 86400000 * 28).toISOString(),
    is_active: true,
  },
  {
    id: 6,
    title: "Fullstack Developer (Node.js + React) - Remote",
    company_name: "Techcombank Digital Lab",
    description: `<h3>Mô tả công việc</h3>
<p>Phát triển các module ngân hàng số thế hệ mới, hỗ trợ làm việc từ xa 100%.</p>`,
    requirements: `<h3>Yêu cầu ứng viên</h3>
<ul>
  <li>Kinh nghiệm vững chắc với Node.js, Express/NestJS và React.</li>
  <li>Kinh nghiệm làm việc từ xa độc lập, giao tiếp tốt.</li>
</ul>`,
    salary_min: 28000000,
    salary_max: 45000000,
    salary_text: "28 - 45 triệu VNĐ",
    location_province: "Đà Nẵng",
    location_district: "Hải Châu",
    location_full: "Làm việc từ xa (Toàn quốc) / Văn phòng đại diện Đà Nẵng",
    job_type: "Làm việc từ xa",
    category: "Công nghệ thông tin / Phần mềm",
    experience_level: "Senior",
    source_platform: "VietnamWorks",
    source_url: "https://vietnamworks.com",
    posted_at: new Date(Date.now() - 3600000 * 8).toISOString(),
    expires_at: new Date(Date.now() + 86400000 * 30).toISOString(),
    is_active: true,
  },
];

const DEFAULT_STATS: DashboardStats = {
  total_jobs: 106,
  total_companies: 68,
  total_provinces_with_jobs: 8,
  new_jobs_today: 14,
  jobs_by_province: [
    { province: "Quảng Ninh", count: 90 },
    { province: "Hà Nội", count: 6 },
    { province: "Bình Dương", count: 3 },
    { province: "Hồ Chí Minh", count: 2 },
    { province: "Đà Nẵng", count: 2 },
    { province: "Hải Phòng", count: 2 },
  ],
  jobs_by_category: [
    { category: "Công nghệ thông tin / Phần mềm / IT", count: 53 },
    { category: "Du lịch / Khách sạn / Nghỉ dưỡng", count: 12 },
    { category: "Ngân hàng / Tài chính / Giao dịch", count: 8 },
    { category: "Kế toán / Kiểm toán / Thuế", count: 7 },
    { category: "Công nghiệp / Than - Khoáng sản / Cơ điện", count: 6 },
    { category: "Kinh doanh / Bán hàng / Marketing", count: 6 },
    { category: "Nhà hàng / Dịch vụ ăn uống / F&B", count: 5 },
    { category: "Chăm sóc khách hàng / Tư vấn", count: 4 },
  ],
  jobs_by_platform: [
    { platform: "CareerViet", count: 42 },
    { platform: "Sun Group Career", count: 18 },
    { platform: "Vinpearl Resort", count: 12 },
    { platform: "TKV Than Quảng Ninh", count: 10 },
    { platform: "Wyndham Legend", count: 8 },
    { platform: "FPT Telecom", count: 6 },
  ],
};

import { loadAllJobsForClient, searchJobsRealtime } from "./clientSearch";

/**
 * Fetch jobs list with pagination & filters - hỗ trợ cả Backend API và Client-side Realtime Engine
 */
export async function getJobs(params: JobSearchParams = {}): Promise<JobListResponse> {
  // Nếu là tìm việc đã lưu (lưu trong client LocalStorage), dùng ngay Client-side Engine
  if (params.saved) {
    try {
      const allJobs = await loadAllJobsForClient();
      if (allJobs && allJobs.length > 0) {
        return searchJobsRealtime(allJobs, params);
      }
    } catch (err) {
      console.warn("Client-side saved search failed:", err);
    }
  }

  try {
    const response = await apiClient.get<JobListResponse>("/jobs", { params });
    if (response.data && Array.isArray(response.data.items)) {
      return response.data;
    }
  } catch {
    // Backend API offline / GitHub Pages static mode -> chuyển ngay sang Real-time Client Engine
  }

  try {
    const allJobs = await loadAllJobsForClient();
    if (allJobs && allJobs.length > 0) {
      return searchJobsRealtime(allJobs, params);
    }
  } catch (err) {
    console.warn("Client-side search failed:", err);
  }

  return filterSampleJobs(params);
}

/**
 * Filter fallback jobs for mock/fallback mode
 */
function filterSampleJobs(params: JobSearchParams): JobListResponse {
  let filtered = [...SAMPLE_FALLBACK_JOBS];

  if (params.q) {
    const q = params.q.toLowerCase();
    filtered = filtered.filter(
      (j) =>
        j.title.toLowerCase().includes(q) ||
        j.company_name.toLowerCase().includes(q) ||
        (j.category && j.category.toLowerCase().includes(q))
    );
  }

  if (params.province) {
    filtered = filtered.filter(
      (j) =>
        j.location_province?.toLowerCase().includes(params.province!.toLowerCase()) ||
        j.location_full?.toLowerCase().includes(params.province!.toLowerCase())
    );
  }

  if (params.category) {
    filtered = filtered.filter((j) =>
      j.category?.toLowerCase().includes(params.category!.toLowerCase())
    );
  }

  if (params.job_type) {
    filtered = filtered.filter((j) =>
      j.job_type?.toLowerCase().includes(params.job_type!.toLowerCase())
    );
  }

  if (params.source_platform) {
    filtered = filtered.filter((j) =>
      j.source_platform?.toLowerCase().includes(params.source_platform!.toLowerCase())
    );
  }

  if (params.salary_min) {
    filtered = filtered.filter(
      (j) => (j.salary_max || j.salary_min || 0) >= params.salary_min!
    );
  }

  if (params.salary_max) {
    filtered = filtered.filter(
      (j) => (j.salary_min || 0) <= params.salary_max!
    );
  }

  const page = params.page || 1;
  const pageSize = params.page_size || 20;
  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);

  return {
    items,
    total,
    page,
    page_size: pageSize,
    total_pages: totalPages,
  };
}

/**
 * Fetch a single job by its ID
 */
export async function getJob(id: string | number): Promise<Job | null> {
  try {
    const response = await apiClient.get<Job>(`/jobs/${id}`);
    if (response.data && response.data.id) {
      return response.data;
    }
  } catch {
    // API failed, tìm trong cơ sở dữ liệu client
  }

  try {
    const allJobs = await loadAllJobsForClient();
    const found = allJobs.find(
      (j) => String(j.id) === String(id)
    );
    if (found) return found;
  } catch {
    // fallback
  }

  return (
    SAMPLE_FALLBACK_JOBS.find((j) => String(j.id) === String(id)) || null
  );
}

/**
 * ⚡ Kích hoạt cào trực tiếp thời gian thực từ sàn tuyển dụng, mạng xã hội và website doanh nghiệp
 */
export async function crawlLiveJobs(
  q?: string,
  province?: string
): Promise<{
  success: boolean;
  total_crawled: number;
  message: string;
  by_source?: { portals: number; social_media: number; corporate: number };
  jobs: any[];
}> {
  try {
    const response = await apiClient.post("/jobs/crawl-live", null, {
      params: { q, province, max_items: 10 },
    });
    return response.data;
  } catch (err) {
    console.warn("Crawl live failed:", (err as Error).message);
    return {
      success: false,
      total_crawled: 0,
      message: "Không thể kết nối đến nguồn dữ liệu trực tiếp vào lúc này.",
      jobs: [],
    };
  }
}

export interface SocialHarvestResponse {
  success: boolean;
  scanned_at?: string;
  total_harvested: number;
  by_platform: {
    facebook: number;
    threads: number;
    tiktok: number;
  };
  saved_count: number;
  scanned_sources_count?: number;
  scanned_sources?: Array<{ type: string; name: string; members: string }>;
  queried_sources?: Array<{
    source_id: string;
    name: string;
    status: string;
    access_method: string;
    items_count: number;
    latency_ms: number;
  }>;
  failed_or_blocked_sources?: Array<{
    source_id: string;
    name: string;
    status: string;
    error_code: string;
    reason: string;
    fallback_applied: boolean;
  }>;
  post_types_summary?: {
    original_hiring: number;
    shared_posts: number;
    discussions_filtered: number;
    spam_rejected: number;
    expired_closed: number;
  };
  anti_scam_rejected?: number;
  verified_rate?: string;
  radar_logs?: Array<{
    phase: number;
    title: string;
    message: string;
    timestamp: string;
    status: string;
  }>;
  conclusions?: any;
  jobs: any[];
}

/**
 * 🛰️ Radar Mò Quét Dữ Liệu Chuyên Sâu Đa Mạng Xã Hội (Facebook, Threads, TikTok)
 */
export async function harvestSocialDeep(
  keyword?: string
): Promise<SocialHarvestResponse> {
  try {
    const response = await apiClient.post<SocialHarvestResponse>(
      "/jobs/social-deep-harvest",
      null,
      {
        params: { q: keyword },
      }
    );
    return response.data;
  } catch (err) {
    console.warn("harvestSocialDeep failed:", (err as Error).message);
    return {
      success: false,
      total_harvested: 0,
      by_platform: { facebook: 0, threads: 0, tiktok: 0 },
      saved_count: 0,
      jobs: [],
    };
  }
}

/**
 * Search jobs with keyword and optional filters
 */
export async function searchJobs(
  query: string,
  filters: Partial<JobSearchParams> = {}
): Promise<JobListResponse> {
  return getJobs({
    q: query,
    ...filters,
  });
}

/**
 * Get companies list
 */
export async function getCompanies(): Promise<Company[]> {
  try {
    const response = await apiClient.get<Company[]>("/companies");
    if (Array.isArray(response.data) && response.data.length > 0) {
      return response.data;
    }
  } catch (err) {
    console.warn("API /companies failed:", (err as Error).message);
  }

  return [
    {
      id: 1,
      name: "Tập Đoàn Công Nghệ VNG",
      logo_url: null,
      province: "Hồ Chí Minh",
      description: "Kỳ lân công nghệ đầu tiên tại Việt Nam, tiên phong trong game và thanh toán số.",
      jobs_count: 42,
    },
    {
      id: 2,
      name: "Sun Group - Vùng Đông Bắc",
      logo_url: null,
      province: "Quảng Ninh",
      description: "Tập đoàn đầu tư phát triển du lịch, nghỉ dưỡng và hạ tầng hàng đầu Việt Nam.",
      jobs_count: 28,
    },
    {
      id: 3,
      name: "FPT Software",
      logo_url: null,
      province: "Hà Nội",
      description: "Công ty xuất khẩu phần mềm và dịch vụ CNTT lớn nhất Đông Nam Á.",
      jobs_count: 65,
    },
    {
      id: 4,
      name: "BIM Group",
      logo_url: null,
      province: "Quảng Ninh",
      description: "Tập đoàn kinh tế đa ngành với các dự án đô thị và năng lượng tái tạo quy mô lớn.",
      jobs_count: 19,
    },
  ];
}

/**
 * Get single company with jobs
 */
export async function getCompany(id: string | number): Promise<Company | null> {
  try {
    const response = await apiClient.get<Company>(`/companies/${id}`);
    if (response.data && response.data.id) {
      return response.data;
    }
  } catch (err) {
    console.warn(`API /companies/${id} failed:`, (err as Error).message);
  }

  const companies = await getCompanies();
  const found = companies.find((c) => String(c.id) === String(id)) || companies[0];
  if (found) {
    return {
      ...found,
      jobs: SAMPLE_FALLBACK_JOBS.slice(0, 3),
    };
  }
  return null;
}

/**
 * Get list of provinces from backend or fallback
 */
export async function getProvinces(): Promise<string[]> {
  try {
    const response = await apiClient.get<string[] | Province[]>("/provinces");
    if (Array.isArray(response.data) && response.data.length > 0) {
      return response.data.map((item) => (typeof item === "string" ? item : item.name));
    }
  } catch (err) {
    console.warn("API /provinces failed:", (err as Error).message);
  }

  return [
    "Hà Nội",
    "Hồ Chí Minh",
    "Đà Nẵng",
    "Quảng Ninh",
    "Hải Phòng",
    "Bình Dương",
    "Đồng Nai",
    "Cần Thơ",
    "Bắc Ninh",
  ];
}

/**
 * Get dashboard statistics
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get<DashboardStats>("/stats/dashboard");
    if (response.data && typeof response.data.total_jobs === "number") {
      return response.data;
    }
  } catch (err) {
    console.warn("API /stats/dashboard failed or offline, using fallback:", (err as Error).message);
  }

  return DEFAULT_STATS;
}
