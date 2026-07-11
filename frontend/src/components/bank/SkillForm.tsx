import { useState, type FormEvent } from 'react'
import { skillHooks, type SkillCreate } from '../../api/bank'

export function SkillForm() {
  const create = skillHooks.useCreate()
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [tags, setTags] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const body: SkillCreate = {
      name,
      category,
      tags: tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean),
    }
    create.mutate(body, {
      onSuccess: () => {
        setName('')
        setCategory('')
        setTags('')
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <input
        placeholder="Category"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        required
      />
      <input
        placeholder="Tags (comma-separated)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />
      <button type="submit" disabled={create.isPending}>
        Add skill
      </button>
      {create.isError && <span className="error">{create.error.message}</span>}
    </form>
  )
}
