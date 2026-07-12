import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'

export interface JobDescription {
  id: number
  company: string
  role_title: string
  raw_text: string
  extracted_keywords: string[]
  created_at: string
  updated_at: string
}

export interface JobDescriptionCreate {
  company: string
  role_title: string
  raw_text: string
}

export interface MatchRequest {
  bullets_per_experience_entry?: number
  max_skills?: number
  max_projects?: number
}

export type ScoringMetadata = Record<string, Record<string, string[]>>

export interface MatchResult {
  selected_experience_bullet_ids: number[]
  selected_project_ids: number[]
  selected_skill_ids: number[]
  selected_education_ids: number[]
  scoring_metadata: ScoringMetadata
}

export interface Selection {
  selected_experience_bullet_ids: number[]
  selected_project_ids: number[]
  selected_skill_ids: number[]
  selected_education_ids: number[]
}

export interface TailoredResume extends Selection {
  id: number
  job_description_id: number
  scoring_metadata: ScoringMetadata
  llm_enhanced: boolean
  resolved_content: unknown | null
  rendered_pdf_path: string | null
  rendered_filename: string | null
  status: 'draft' | 'finalized'
  created_at: string
  finalized_at: string | null
}

export function useCreateJobDescription() {
  return useMutation({
    mutationFn: (body: JobDescriptionCreate) =>
      apiClient.post<JobDescription>('/job-descriptions', body),
  })
}

export function useMatchJobDescription() {
  return useMutation({
    mutationFn: ({ jobDescriptionId, body }: { jobDescriptionId: number; body: MatchRequest }) =>
      apiClient.post<MatchResult>(`/job-descriptions/${jobDescriptionId}/match`, body),
  })
}

export function useCreateTailoredResume() {
  return useMutation({
    mutationFn: (
      body: Selection & { job_description_id: number; scoring_metadata: ScoringMetadata }
    ) => apiClient.post<TailoredResume>('/tailored-resumes', body),
  })
}

export function useUpdateTailoredResumeSelection() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Partial<Selection> }) =>
      apiClient.patch<TailoredResume>(`/tailored-resumes/${id}`, body),
    onSuccess: (_data, variables) =>
      qc.invalidateQueries({ queryKey: ['tailored-resume-preview', variables.id] }),
  })
}

export function useTailoredResumePreview(tailoredResumeId: number | null) {
  return useQuery({
    queryKey: ['tailored-resume-preview', tailoredResumeId],
    queryFn: () => apiClient.getText(`/tailored-resumes/${tailoredResumeId}/preview`),
    enabled: tailoredResumeId !== null,
  })
}

export function useFinalizeTailoredResume() {
  return useMutation({
    mutationFn: (tailoredResumeId: number) =>
      apiClient.post<TailoredResume>(`/tailored-resumes/${tailoredResumeId}/finalize`, {}),
  })
}
