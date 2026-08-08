import { useState } from 'react'
import { skillHooks, type Skill } from '../../api/bank'
import { rowRiseStyle } from '../../lib/rowStagger'
import { EmptyState } from '../ui/EmptyState'
import { TableSkeleton } from '../ui/Skeleton'

export function SkillList() {
  const { data, isLoading } = skillHooks.useList()
  const del = skillHooks.useDelete()
  const update = skillHooks.useUpdate()

  const [editingId, setEditingId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [tags, setTags] = useState('')

  function startEdit(skill: Skill) {
    setEditingId(skill.id)
    setName(skill.name)
    setCategory(skill.category)
    setTags(skill.tags.join(', '))
  }

  function saveEdit(id: number) {
    update.mutate(
      {
        id,
        body: {
          name,
          category,
          tags: tags
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean),
        },
      },
      { onSuccess: () => setEditingId(null) },
    )
  }

  if (isLoading) return <TableSkeleton columns={4} />
  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="No skills yet"
        hint="Add your first skill above — languages, tools, anything you'd list on a resume."
      />
    )
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Category</th>
          <th>Tags</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {data.map((skill, i) =>
          editingId === skill.id ? (
            <tr key={skill.id} className="editing row-rise" style={rowRiseStyle(i)}>
              <td>
                <input className="cell-edit" value={name} onChange={(e) => setName(e.target.value)} />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="Category"
                />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="Tags, comma-separated"
                />
              </td>
              <td className="actions">
                <div className="row-actions">
                  <button
                    className="btn-primary btn-sm"
                    onClick={() => saveEdit(skill.id)}
                    disabled={update.isPending}
                  >
                    Save
                  </button>
                  <button className="btn-ghost btn-sm" onClick={() => setEditingId(null)}>
                    Cancel
                  </button>
                </div>
              </td>
            </tr>
          ) : (
            <tr key={skill.id} className="row-rise" style={rowRiseStyle(i)}>
              <td>{skill.name}</td>
              <td>{skill.category}</td>
              <td>
                {skill.tags.map((tag) => (
                  <span key={tag} className="tag-chip">
                    {tag}
                  </span>
                ))}
              </td>
              <td className="actions">
                <div className="row-actions">
                  <button className="btn-ghost btn-sm" onClick={() => startEdit(skill)}>
                    Edit
                  </button>
                  <button className="btn-ghost btn-sm" onClick={() => del.mutate(skill.id)}>
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ),
        )}
      </tbody>
    </table>
  )
}
