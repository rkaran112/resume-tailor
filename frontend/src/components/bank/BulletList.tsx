import { bulletHooks, experienceHooks, projectHooks } from '../../api/bank'

export function BulletList() {
  const { data: bullets, isLoading } = bulletHooks.useList()
  const { data: experienceEntries } = experienceHooks.useList()
  const { data: projects } = projectHooks.useList()
  const del = bulletHooks.useDelete()

  if (isLoading) return <p>Loading…</p>

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
        {bullets?.map((bullet) => (
          <tr key={bullet.id}>
            <td>{parentLabel(bullet.experience_entry_id, bullet.project_id)}</td>
            <td>{bullet.text}</td>
            <td>{bullet.tags.join(', ')}</td>
            <td>{bullet.impact_metric ?? ''}</td>
            <td>
              <button onClick={() => del.mutate(bullet.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
