import { useState, type FormEvent } from 'react'
import { projectHooks, type ProjectCreate } from '../../api/bank'

export function ProjectForm() {
  const create = projectHooks.useCreate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [techTags, setTechTags] = useState('')
  const [link, setLink] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const body: ProjectCreate = {
      name,
      description,
      tech_tags: techTags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
      link: link || null,
    }
    create.mutate(body, {
      onSuccess: () => {
        setName('')
        setDescription('')
        setTechTags('')
        setLink('')
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <input
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <input
        placeholder="Tech tags (comma-separated)"
        value={techTags}
        onChange={(e) => setTechTags(e.target.value)}
      />
      <input placeholder="Link" value={link} onChange={(e) => setLink(e.target.value)} />
      <button type="submit" disabled={create.isPending}>
        Add project
      </button>
      {create.isError && <span className="error">{create.error.message}</span>}
    </form>
  )
}
