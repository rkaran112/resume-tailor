import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'

export interface ImportedContactLink {
  label: string
  url: string
}

export interface ImportedContact {
  name: string
  email: string
  phone: string
  location: string
  links: ImportedContactLink[]
  include: boolean
}

export interface ImportedBullet {
  text: string
  tags: string[]
  include: boolean
  already_exists: boolean
}

export interface ImportedExperienceEntry {
  company: string
  title: string
  location: string
  start_date: string
  end_date: string | null
  bullets: ImportedBullet[]
  include: boolean
  already_exists: boolean
}

export interface ImportedSkill {
  name: string
  category: string
  tags: string[]
  include: boolean
  already_exists: boolean
}

export interface ImportedProject {
  name: string
  description: string
  tech_tags: string[]
  bullets: ImportedBullet[]
  include: boolean
  already_exists: boolean
}

export interface ImportedEducationEntry {
  institution: string
  degree: string
  field: string
  start_date: string
  end_date: string | null
  gpa: string
  include: boolean
  already_exists: boolean
}

export interface ResumeImportPreview {
  contact: ImportedContact
  experience: ImportedExperienceEntry[]
  skills: ImportedSkill[]
  projects: ImportedProject[]
  education: ImportedEducationEntry[]
}

export interface ResumeImportCommitResult {
  contact_updated: boolean
  experience_entries_created: number
  bullets_created: number
  skills_created: number
  projects_created: number
  education_entries_created: number
}

const BANK_QUERY_KEYS = [
  ['skills'],
  ['experience-entries'],
  ['projects'],
  ['education-entries'],
  ['bullets'],
  ['contact-info'],
]

export function useImportResume() {
  return useMutation({
    mutationFn: (file: File) => apiClient.postFile<ResumeImportPreview>('/bank/import', file),
  })
}

export function useCommitResumeImport() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (preview: ResumeImportPreview) =>
      apiClient.post<ResumeImportCommitResult>('/bank/import/commit', preview),
    onSuccess: () => {
      for (const queryKey of BANK_QUERY_KEYS) {
        qc.invalidateQueries({ queryKey })
      }
    },
  })
}
