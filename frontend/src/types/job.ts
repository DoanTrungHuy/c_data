export interface JobSourceLink {
  platform: string;
  url: string;
  posted_at?: string | null;
  verified?: boolean;
}

export interface StructuredLocation {
  province?: string | null;
  district?: string | null;
  address?: string | null;
  is_primary?: boolean;
  country?: string;
}

export type WorkplaceType = "onsite" | "hybrid" | "remote" | "unknown";
export type JobStatus = "active_confirmed" | "active_likely" | "expired" | "closed" | "unknown";
export type SalaryPeriod = "month" | "year" | "hour" | "day" | "project" | "unknown";

export interface Job {
  id: number | string;
  title: string;
  company_name: string;
  description?: string | null;
  requirements?: string | null;

  // Locations
  locations?: StructuredLocation[] | null;
  location_province?: string | null;
  location_district?: string | null;
  location_full?: string | null;

  // Workplace & Employment
  workplace_type?: WorkplaceType;
  employment_type?: string;
  job_type?: string | null;
  category?: string | null;
  experience_level?: string | null;
  required_skills?: string[] | null;

  // Salary
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string;
  salary_period?: SalaryPeriod;
  salary_text?: string | null;

  // Source & Origin
  source_name?: string;
  source_platform?: string | null;
  source_url?: string | null;
  apply_url?: string | null;
  source_job_id?: string | null;

  // Temporal Tracking
  posted_at?: string | null;
  updated_at?: string | null;
  deadline_at?: string | null;
  expires_at?: string | null;
  first_seen_at?: string | null;
  last_seen_at?: string | null;
  first_discovered_at?: string | null;
  last_verified_at?: string | null;
  crawled_at?: string | null;

  // Status & Verification
  status?: JobStatus;
  status_reason?: string | null;
  status_evidence?: any;
  verification_status?: "verified" | "unverified" | "unknown" | null;
  is_active?: boolean;

  // Confidence & Deduplication
  extraction_confidence?: number;
  location_confidence?: number;
  raw_data_reference?: string | null;
  content_hash?: string | null;

  // Relations & Enriched Metadata
  created_at?: string | null;
  company_id?: number | string | null;
  company?: Company | null;
  raw_data?: any;
  all_sources?: JobSourceLink[] | null;
  match_reasons?: string[] | null;
  match_score?: number | null;
  quality_score?: number | null;
  quality_tier?: "diamond" | "gold" | "standard" | null;
  tech_stack?: string[] | null;
  benefits_detail?: string[] | null;
  interview_process?: Array<{ step: number; title: string; desc: string }> | null;
  evidence_proof?: EvidenceProof | null;
  quality_audit?: {
    corporate_verified?: boolean;
    salary_transparent?: boolean;
    address_specific?: boolean;
    direct_contact?: boolean;
    jd_detailed?: boolean;
    tech_stack_clarity?: boolean;
    anti_scam_verified?: boolean;
  } | null;
}

export interface EvidenceProof {
  verified: boolean;
  source_type: "job_board" | "official_portal" | "enterprise_direct" | "social_verified";
  source_name: string;
  direct_url: string;
  url_status: number;
  recruiter_contact?: {
    hr_name?: string;
    hotline?: string;
    zalo?: string;
    email?: string;
  };
  address_confirmed?: string;
  announcement_snippet?: string;
  verified_at: string;
  proof_badge: string;
}

export interface Company {
  id: number | string;
  name: string;
  slug?: string;
  logo_url?: string | null;
  website?: string | null;
  description?: string | null;
  address?: string | null;
  province?: string | null;
  jobs_count?: number;
  jobs?: Job[];
}

export interface Province {
  id?: number | string;
  name: string;
  code?: string;
  jobs_count?: number;
}

export interface JobSearchParams {
  page?: number;
  page_size?: number;
  province?: string;
  category?: string;
  job_type?: string;
  salary_min?: number;
  salary_max?: number;
  source_platform?: string;
  q?: string;
  sort_by?: string;
  live?: boolean;
  strict_mode?: boolean;
  verified_only?: boolean;
  saved?: boolean;
  quality_tier?: string;
  tech_stack?: string;
}

export interface SearchIntentDiagnostics {
  primary_role?: string | null;
  role_family?: string[] | string | null;
  role_synonyms?: string[];
  target_province?: string | null;
  target_district?: string | null;
  province?: string | null;
  city?: string | null;
  location_aliases?: string[];
  seniority?: string | null;
  work_environment?: string | null;
  remote_preference?: string | null;
  travel_preference?: string | null;
  field_work_preference?: string | null;
  max_posting_age_days?: number | null;
  negative_constraints?: string[];
  required_skills?: string[];
}

export interface SearchDiagnostics {
  original_query: string;
  parsed_intent?: SearchIntentDiagnostics;
  intent?: SearchIntentDiagnostics;
  expanded_queries: string[];
  total_candidates_examined: number;
  removed_by_filters: {
    hard_location: number;
    hard_remote: number;
    hard_posting_age: number;
    hard_exclusion: number;
    expired: number;
  };
  duplicates_consolidated: number;
  ranking_details: Array<{
    job_id: string;
    title: string;
    company: string;
    score: number;
    criteria: Record<string, number>;
    reasons: string[];
  }>;
  multi_source_discovery?: Record<string, any>;
  final_eligible_count?: number;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  related_keywords?: string[];
  matched_industries?: string[];
  diagnostics?: SearchDiagnostics | null;
}

export interface ProvinceJobCount {
  province: string;
  count: number;
}

export interface CategoryJobCount {
  category: string;
  count: number;
}

export interface PlatformJobCount {
  platform: string;
  count: number;
}

export interface DashboardStats {
  total_jobs: number;
  total_companies: number;
  total_provinces_with_jobs: number;
  new_jobs_today: number;
  jobs_by_province: ProvinceJobCount[];
  jobs_by_category: CategoryJobCount[];
  jobs_by_platform: PlatformJobCount[];
}
