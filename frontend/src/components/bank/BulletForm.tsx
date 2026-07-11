import { useState, type FormEvent } from 'react'
import { bulletHooks, experienceHooks, projectHooks, type BulletCreate } from '../../api/bank'

export function BulletForm() {
  const create = bulletHooks.useCreate()
  const { data: experienceEntries } = experienceHooks.useList()
  const { data: projects } = projectHooks.useList()

  const [parentType, setParentType] = useState<'experience' | 'project'>('experience')
  const [parentId, setParentId] = useState('')
  const [text, setText] = useState('')
  const [tags, setTags] = useState('')
  const [impactMetric, setImpactMetric] = useState('')

  const parentOptions = parentType === 'experience' ? experienceEntries : projects

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!parentId) return
    const body: BulletCreate = {
      experience_entry_id: parentType === 'experience' ? Number(parentId) : null,
      project_id: parentType === 'project' ? Number(parentId) : null,
      text,
      tags: tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
      impact_metric: impactMetric || null,
    }
    create.mutate(body, {
      onSuccess: () => {
        setText('')
        setTags('')
        setImpactMetric('')
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <select
        value={parentType}
        onChange={(e) => {
          setParentType(e.target.value as 'experience' | 'project')
          setParentId('')
        }}
      >
        <option value="experience">Experience</option>
        <option value="project">Project</option>
      </select>
      <select value={parentId} onChange={(e) => setParentId(e.target.value)} required>
        <option value="" disabled>
          Select {parentType}…
        </option>
        {parentOptions?.map((option) => (
          <option key={option.id} value={option.id}>
            {'company' in option ? `${option.company} — ${option.title}` : option.name}
          </option>
        ))}
      </select>
      <input
        placeholder="Bullet text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        required
      />
      <input
        placeholder="Tags (comma-separated)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />
      <input
        placeholder="Impact metric"
        value={impactMetric}
        onChange={(e) => setImpactMetric(e.target.value)}
      />
      <button type="submit" disabled={create.isPending}>
        Add bullet
      </button>
      {create.isError && <span className="error">{create.error.message}</span>}
    </form>
  )
}
