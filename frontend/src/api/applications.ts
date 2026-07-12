import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'

export type ApplicationStatus = 'applied' | 'interview' | 'offer' | 'rejected' | 'withdrawn'

export interface ApplicationStatusEvent {
  id: number
  status: ApplicationStatus
  changed_at: string
  note: string | null
}

export interface Application {
  id: number
  tailored_resume_id: number | null
  job_description_id: number
  company: string
  role_title: string
  date_applied: string
  status: ApplicationStatus
  notes: string | null
  created_at: string
  updated_at: string
  status_events: ApplicationStatusEvent[]
}

export interface ApplicationCreate {
  tailored_resume_id?: number | null
  job_description_id: number
  company: string
  role_title: string
  date_applied: string
  status?: ApplicationStatus
  notes?: string | null
}

const applicationsKey = ['applications']

export function useApplications() {
  return useQuery({
    queryKey: applicationsKey,
    queryFn: () => apiClient.get<Application[]>('/applications'),
  })
}

export function useApplication(id: number) {
  return useQuery({
    queryKey: [...applicationsKey, id],
    queryFn: () => apiClient.get<Application>(`/applications/${id}`),
  })
}

export function useCreateApplication() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: ApplicationCreate) => apiClient.post<Application>('/applications', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: applicationsKey }),
  })
}

export function useChangeApplicationStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      status,
      note,
    }: {
      id: number
      status: ApplicationStatus
      note?: string
    }) => apiClient.post<Application>(`/applications/${id}/status`, { status, note }),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: applicationsKey })
      qc.invalidateQueries({ queryKey: [...applicationsKey, variables.id] })
    },
  })
}
