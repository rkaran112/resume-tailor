import { useState } from 'react'
import { projectHooks, type Project } from '../../api/bank'
import { rowRiseStyle } from '../../lib/rowStagger'
import { EmptyState } from '../ui/EmptyState'
import { TableSkeleton } from '../ui/Skeleton'

export function ProjectList() {
  const { data, isLoading } = projectHooks.useList()
  const del = projectHooks.useDelete()
  const update = projectHooks.useUpdate()

  const [editingId, setEditingId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [techTags, setTechTags] = useState('')
  const [link, setLink] = useState('')

  function startEdit(project: Project) {
    setEditingId(project.id)
    setName(project.name)
    setDescription(project.description)
    setTechTags(project.tech_tags.join(', '))
    setLink(project.link ?? '')
  }

  function saveEdit(id: number) {
    update.mutate(
      {
        id,
        body: {
          name,
          description,
          tech_tags: techTags
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean),
          link: link || null,
        },
      },
      { onSuccess: () => setEditingId(null) },
    )
  }

  if (isLoading) return <TableSkeleton columns={5} />
  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="No projects yet"
        hint="Add a project above — side projects and open source count too."
      />
    )
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Tech tags</th>
          <th>Link</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {data.map((project, i) =>
          editingId === project.id ? (
            <tr key={project.id} className="editing row-rise" style={rowRiseStyle(i)}>
              <td>
                <input className="cell-edit" value={name} onChange={(e) => setName(e.target.value)} />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Description"
                />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={techTags}
                  onChange={(e) => setTechTags(e.target.value)}
                  placeholder="Tags, comma-separated"
                />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={link}
                  onChange={(e) => setLink(e.target.value)}
                  placeholder="Link"
                />
              </td>
              <td className="actions">
                <div className="row-actions">
                  <button
                    className="btn-primary btn-sm"
                    onClick={() => saveEdit(project.id)}
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
            <tr key={project.id} className="row-rise" style={rowRiseStyle(i)}>
              <td>{project.name}</td>
              <td>{project.description}</td>
              <td>
                {project.tech_tags.map((tag) => (
                  <span key={tag} className="tag-chip">
                    {tag}
                  </span>
                ))}
              </td>
              <td>{project.link}</td>
              <td className="actions">
                <div className="row-actions">
                  <button className="btn-ghost btn-sm" onClick={() => startEdit(project)}>
                    Edit
                  </button>
                  <button className="btn-ghost btn-sm" onClick={() => del.mutate(project.id)}>
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
