import axios from 'axios';
import type {
  AssessmentQuestion,
  AssessmentResult,
  RecommendationResponse,
  ScoreRankResult,
  UniversityDetail,
  MajorInfo,
  MajorCategory,
  UniversityInfo,
  Paginated,
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/',
  timeout: 15000,
});

// --- Assessment ---
export async function getQuestions(): Promise<AssessmentQuestion[]> {
  const res = await api.get<{ questions: AssessmentQuestion[] }>('/api/assessment/questions');
  return res.data.questions;
}

export async function submitAssessment(answers: number[]): Promise<AssessmentResult> {
  const res = await api.post<AssessmentResult>('/api/assessment', { answers });
  return res.data;
}

// --- Universities ---
export async function getUniversities(params: {
  search?: string;
  tier?: string;
  province?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<Paginated<UniversityInfo>> {
  const res = await api.get('/api/universities', { params });
  return res.data as Paginated<UniversityInfo>;
}

export async function getUniversityDetail(id: number): Promise<UniversityDetail> {
  const res = await api.get<UniversityDetail>(`/api/universities/${id}`);
  return res.data;
}

// --- Majors ---
export async function getMajors(params: {
  category?: string;
  search?: string;
} = {}): Promise<{ total: number; majors: MajorInfo[] }> {
  const res = await api.get('/api/majors', { params });
  return res.data;
}

export async function getMajorDetail(id: number): Promise<MajorInfo> {
  const res = await api.get<MajorInfo>(`/api/majors/${id}`);
  return res.data;
}

export async function getMajorCategories(): Promise<MajorCategory[]> {
  const res = await api.get<{ categories: MajorCategory[] }>('/api/major-categories');
  return res.data.categories;
}

// --- Recommendation ---
export async function getRecommendations(data: {
  province: string;
  score: number;
  category: string;
  assessment_scores?: Record<string, number> | null;
  filters?: Record<string, string> | null;
  year?: number;
}): Promise<RecommendationResponse> {
  const res = await api.post<RecommendationResponse>('/api/recommend', data);
  return res.data;
}

// --- Score Rank ---
export async function getScoreRank(params: {
  province: string;
  score: number;
  category: string;
  year?: number;
}): Promise<ScoreRankResult> {
  const res = await api.get<ScoreRankResult>('/api/score-rank', { params });
  return res.data;
}

export async function getScoreDistribution(params: {
  province: string;
  category: string;
  year?: number;
}): Promise<{ province: string; category: string; year: number; distribution: { score: number; cumulative_count: number }[] }> {
  const res = await api.get('/api/score-distribution', { params });
  return res.data;
}
