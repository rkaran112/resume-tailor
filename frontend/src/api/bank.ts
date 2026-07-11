import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'

function createCrudHooks<TRead, TCreate, TUpdate>(resource: string) {
  const key = [resource]

  function useList() {
    return useQuery({ queryKey: key, queryFn: () => apiClient.get<TRead[]>(`/${resource}`) })
  }

  function useCreate() {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: (body: TCreate) => apiClient.post<TRead>(`/${resource}`, body),
      onSuccess: () => qc.invalidateQueries({ queryKey: key }),
    })
  }

  function useUpdate() {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: ({ id, body }: { id: number; body: TUpdate }) =>
        apiClient.patch<TRead>(`/${resource}/${id}`, body),
      onSuccess: () => qc.invalidateQueries({ queryKey: key }),
    })
  }

  function useDelete() {
    const qc = useQueryClient()
    return useMutation({
      mutationFn: (id: number) => apiClient.delete(`/${resource}/${id}`),
      onSuccess: () => qc.invalidateQueries({ queryKey: key }),
    })
  }

  return { useList, useCreate, useUpdate, useDelete }
}

interface Timestamped {
  id: number
  created_at: string
  updated_at: string
}

// ---- Skills ----

export interface Skill extends Timestamped {
  name: string
  category: string
  tags: string[]
}
export interface SkillCreate {
  name: string
  category: string
  tags: string[]
}
export type SkillUpdate = Partial<SkillCreate>

export const skillHooks = createCrudHooks<Skill, SkillCreate, SkillUpdate>('skills')

// ---- Experience entries ----

export interface ExperienceEntry extends Timestamped {
  company: string
  title: string
  location: string
  start_date: string
  end_date: string | null
  display_order: number
}
export interface ExperienceEntryCreate {
  company: string
  title: string
  location: string
  start_date: string
  end_date?: string | null
  display_order?: number
}
export type ExperienceEntryUpdate = Partial<ExperienceEntryCreate>

export const experienceHooks = createCrudHooks<
  ExperienceEntry,
  ExperienceEntryCreate,
  ExperienceEntryUpdate
>('experience-entries')

// ---- Projects ----

export interface Project extends Timestamped {
  name: string
  description: string
  tech_tags: string[]
  link: string | null
  display_order: number
}
export interface ProjectCreate {
  name: string
  description: string
  tech_tags: string[]
  link?: string | null
  display_order?: number
}
export type ProjectUpdate = Partial<ProjectCreate>

export const projectHooks = createCrudHooks<Project, ProjectCreate, ProjectUpdate>('projects')

// ---- Education entries ----

export interface EducationEntry extends Timestamped {
  institution: string
  degree: string
  field: string
  start_date: string
  end_date: string | null
  gpa: string | null
}
export interface EducationEntryCreate {
  institution: string
  degree: string
  field: string
  start_date: string
  end_date?: string | null
  gpa?: string | null
}
export type EducationEntryUpdate = Partial<EducationEntryCreate>

export const educationHooks = createCrudHooks<
  EducationEntry,
  EducationEntryCreate,
  EducationEntryUpdate
>('education-entries')

// ---- Bullets ----

export interface Bullet extends Timestamped {
  experience_entry_id: number | null
  project_id: number | null
  text: string
  tags: string[]
  impact_metric: string | null
  is_active: boolean
}
export interface BulletCreate {
  experience_entry_id?: number | null
  project_id?: number | null
  text: string
  tags: string[]
  impact_metric?: string | null
  is_active?: boolean
}
export type BulletUpdate = Partial<BulletCreate>

export const bulletHooks = createCrudHooks<Bullet, BulletCreate, BulletUpdate>('bullets')

// ---- Contact info (singleton) ----

export interface ContactLink {
  label: string
  url: string
}
export interface ContactInfo extends Timestamped {
  name: string
  email: string
  phone: string
  location: string
  links: ContactLink[]
}
export type ContactInfoUpsert = Omit<ContactInfo, 'id' | 'created_at' | 'updated_at'>

export function useContactInfo() {
  return useQuery({
    queryKey: ['contact-info'],
    queryFn: () => apiClient.get<ContactInfo>('/contact-info'),
  })
}

export function useUpsertContactInfo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: ContactInfoUpsert) => apiClient.put<ContactInfo>('/contact-info', body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['contact-info'] }),
  })
}
