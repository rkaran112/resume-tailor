import { useState } from 'react'
import { bulletHooks, experienceHooks, projectHooks, type Bullet } from '../../api/bank'
import { rowRiseStyle } from '../../lib/rowStagger'
import { EmptyState } from '../ui/EmptyState'
import { TableSkeleton } from '../ui/Skeleton'

export function BulletList() {
  const { data: bullets, isLoading } = bulletHooks.useList()
  const { data: experienceEntries } = experienceHooks.useList()
  const { data: projects } = projectHooks.useList()
  const del = bulletHooks.useDelete()
  const update = bulletHooks.useUpdate()

  const [editingId, setEditingId] = useState<number | null>(null)
  const [text, setText] = useState('')
  const [tags, setTags] = useState('')
  const [impact, setImpact] = useState('')

  function startEdit(bullet: Bullet) {
    setEditingId(bullet.id)
    setText(bullet.text)
    setTags(bullet.tags.join(', '))
    setImpact(bullet.impact_metric ?? '')
  }

  function saveEdit(id: number) {
    update.mutate(
      {
        id,
        body: {
          text,
          tags: tags
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean),
          impact_metric: impact || null,
        },
      },
      { onSuccess: () => setEditingId(null) },
    )
  }

  if (isLoading) return <TableSkeleton columns={5} />
  if (!bullets || bullets.length === 0) {
    return (
      <EmptyState
        title="No bullets yet"
        hint="Add a bullet above and attach it to a role or project. Bullets are what Tailor picks from."
      />
    )
  }

  function parentLabel(experienceEntryId: number | null, projectId: number | null): string {
    if (experienceEntryId != null) {
      const entry = experienceEntries?.find((e) => e.id === experienceEntryId)
      return entry ? `${entry.company} — ${entry.title}` : `Experience #${experienceEntryId}`
    }
    if (projectId != null) {
      const project = projects?.find((p) => p.id === projectId)
      return project ? project.name : `Project #${projectId}`
    }
    return ''
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Parent</th>
          <th>Text</th>
          <th>Tags</th>
          <th>Impact</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {bullets.map((bullet, i) =>
          editingId === bullet.id ? (
            <tr key={bullet.id} className="editing row-rise" style={rowRiseStyle(i)}>
              <td>{parentLabel(bullet.experience_entry_id, bullet.project_id)}</td>
              <td>
                <input className="cell-edit" value={text} onChange={(e) => setText(e.target.value)} />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="Tags, comma-separated"
                />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={impact}
                  onChange={(e) => setImpact(e.target.value)}
                  placeholder="Impact"
                />
              </td>
              <td className="actions">
                <div className="row-actions">
                  <button
                    className="btn-primary btn-sm"
                    onClick={() => saveEdit(bullet.id)}
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
            <tr key={bullet.id} className="row-rise" style={rowRiseStyle(i)}>
              <td>{parentLabel(bullet.experience_entry_id, bullet.project_id)}</td>
              <td>{bullet.text}</td>
              <td>
                {bullet.tags.map((tag) => (
                  <span key={tag} className="tag-chip">
                    {tag}
                  </span>
                ))}
              </td>
              <td className="mono-num">{bullet.impact_metric ?? ''}</td>
              <td className="actions">
                <div className="row-actions">
                  <button className="btn-ghost btn-sm" onClick={() => startEdit(bullet)}>
                    Edit
                  </button>
                  <button className="btn-ghost btn-sm" onClick={() => del.mutate(bullet.id)}>
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
