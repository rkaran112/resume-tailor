import { useState } from 'react'
import { experienceHooks, type ExperienceEntry } from '../../api/bank'
import { rowRiseStyle } from '../../lib/rowStagger'
import { EmptyState } from '../ui/EmptyState'
import { TableSkeleton } from '../ui/Skeleton'

export function ExperienceList() {
  const { data, isLoading } = experienceHooks.useList()
  const del = experienceHooks.useDelete()
  const update = experienceHooks.useUpdate()

  const [editingId, setEditingId] = useState<number | null>(null)
  const [company, setCompany] = useState('')
  const [title, setTitle] = useState('')
  const [location, setLocation] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  function startEdit(entry: ExperienceEntry) {
    setEditingId(entry.id)
    setCompany(entry.company)
    setTitle(entry.title)
    setLocation(entry.location)
    setStartDate(entry.start_date)
    setEndDate(entry.end_date ?? '')
  }

  function saveEdit(id: number) {
    update.mutate(
      { id, body: { company, title, location, start_date: startDate, end_date: endDate || null } },
      { onSuccess: () => setEditingId(null) },
    )
  }

  if (isLoading) return <TableSkeleton columns={6} />
  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="No experience yet"
        hint="Add a role above, then attach bullets to it under the Bullets tab."
      />
    )
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Title</th>
          <th>Location</th>
          <th>Start</th>
          <th>End</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {data.map((entry, i) =>
          editingId === entry.id ? (
            <tr key={entry.id} className="editing row-rise" style={rowRiseStyle(i)}>
              <td>
                <input className="cell-edit" value={company} onChange={(e) => setCompany(e.target.value)} />
              </td>
              <td>
                <input className="cell-edit" value={title} onChange={(e) => setTitle(e.target.value)} />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Location"
                />
              </td>
              <td>
                <input
                  className="cell-edit"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </td>
              <td>
                <input
                  className="cell-edit"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </td>
              <td className="actions">
                <div className="row-actions">
                  <button
                    className="btn-primary btn-sm"
                    onClick={() => saveEdit(entry.id)}
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
            <tr key={entry.id} className="row-rise" style={rowRiseStyle(i)}>
              <td>{entry.company}</td>
              <td>{entry.title}</td>
              <td>{entry.location}</td>
              <td className="mono-num">{entry.start_date}</td>
              <td className="mono-num">{entry.end_date ?? 'Present'}</td>
              <td className="actions">
                <div className="row-actions">
                  <button className="btn-ghost btn-sm" onClick={() => startEdit(entry)}>
                    Edit
                  </button>
                  <button className="btn-ghost btn-sm" onClick={() => del.mutate(entry.id)}>
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
