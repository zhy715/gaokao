// --- Major Category ---
export interface MajorCategory {
  id: number;
  name: string;
  code: string;
}

// --- University ---
export interface UniversityInfo {
  id: number;
  name: string;
  city: string;
  province: string;
  tier: string;
  type: string;
  is_double_first_class: boolean;
  avg_employment_rate: number;
  description: string;
}

export interface UniversityDetail extends UniversityInfo {
  website: string;
  majors: MajorInUni[];
  admission_trends: AdmissionTrend[];
}

export interface MajorInUni {
  id: number;
  name: string;
  code: string;
  category: string;
  prospect_score: number;
  avg_salary: number;
  is_key_major: boolean;
}

export interface AdmissionTrend {
  year: number;
  min_score: number;
  max_score: number;
  avg_score: number;
}

// --- Major ---
export interface MajorInfo {
  id: number;
  name: string;
  code: string;
  category: string;
  avg_salary: number;
  employment_rate: number;
  prospect_score: number;
  description: string;
  keywords: string;
}

// --- Assessment ---
export interface AssessmentQuestion {
  id: number;
  question: string;
  options: string[];
}

export interface AssessmentResult {
  scores: Record<string, number>;
  top_categories: { code: string; name: string; score: number }[];
  primary_category: { code: string; name: string; score: number } | null;
}

// --- Recommendation ---
export interface RecommendationItem {
  id: number;
  university: UniversityInfo;
  major: {
    id: number;
    name: string;
    category: string;
    code: string;
    prospect_score: number;
    avg_salary: number;
    employment_rate: number;
  };
  admission: {
    year: number;
    min_score: number;
    avg_score: number;
    min_rank: number;
    enrollment_quota: number;
  };
  analysis: {
    tier: 'reach' | 'match' | 'safety';
    rank_ratio: number;
    rank_match_score: number;
    interest_score: number;
    prospect_score: number;
    composite_score: number;
  };
}

export interface RecommendationResponse {
  student: {
    province: string;
    score: number;
    category: string;
    estimated_rank: number;
    year: number;
  };
  summary: {
    total: number;
    reach_count: number;
    match_count: number;
    safety_count: number;
  };
  recommendations: {
    reach: RecommendationItem[];
    match: RecommendationItem[];
    safety: RecommendationItem[];
  };
}

// --- Score Rank ---
export interface ScoreRankResult {
  rank: number | null;
  score: number;
  province: string;
  category: string;
  year: number;
  error?: string;
}

// --- API Pagination ---
export interface Paginated<T> {
  total: number;
  page: number;
  page_size: number;
  [key: string]: T[] | number;
}
