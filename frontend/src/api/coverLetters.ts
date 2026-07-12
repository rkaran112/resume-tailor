import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'

export interface CoverLetter {
  id: number
  tailored_resume_id: number
  job_description_id: number
  generated_text: string
  edited_text: string | null
  llm_generated: boolean
  rendered_pdf_path: string | null
  rendered_filename: string | null
  status: 'draft' | 'finalized'
  created_at: string
  finalized_at: string | null
}

export function useCreateCoverLetter() {
  return useMutation({
    mutationFn: (tailoredResumeId: number) =>
      apiClient.post<CoverLetter>('/cover-letters', { tailored_resume_id: tailoredResumeId }),
  })
}

export function useUpdateCoverLetter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, editedText }: { id: number; editedText: string }) =>
      apiClient.patch<CoverLetter>(`/cover-letters/${id}`, { edited_text: editedText }),
    onSuccess: (_data, variables) =>
      qc.invalidateQueries({ queryKey: ['cover-letter-preview', variables.id] }),
  })
}

export function useCoverLetterPreview(coverLetterId: number | null) {
  return useQuery({
    queryKey: ['cover-letter-preview', coverLetterId],
    queryFn: () => apiClient.getText(`/cover-letters/${coverLetterId}/preview`),
    enabled: coverLetterId !== null,
  })
}

export function useFinalizeCoverLetter() {
  return useMutation({
    mutationFn: (coverLetterId: number) =>
      apiClient.post<CoverLetter>(`/cover-letters/${coverLetterId}/finalize`, {}),
  })
}
