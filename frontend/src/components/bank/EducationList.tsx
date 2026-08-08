import { useState } from 'react'
import { educationHooks, type EducationEntry } from '../../api/bank'
import { rowRiseStyle } from '../../lib/rowStagger'
import { EmptyState } from '../ui/EmptyState'
import { TableSkeleton } from '../ui/Skeleton'

export function EducationList() {
  const { data, isLoading } = educationHooks.useList()
  const del = educationHooks.useDelete()
  const update = educationHooks.useUpdate()

  const [editingId, setEditingId] = useState<number | null>(null)
  const [institution, setInstitution] = useState('')
  const [degree, setDegree] = useState('')
  const [field, setField] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [gpa, setGpa] = useState('')

  function startEdit(entry: EducationEntry) {
    setEditingId(entry.id)
    setInstitution(entry.institution)
    setDegree(entry.degree)
    setField(entry.field)
    setStartDate(entry.start_date)
    setEndDate(entry.end_date ?? '')
    setGpa(entry.gpa ?? '')
  }

  function saveEdit(id: number) {
    update.mutate(
      {
        id,
        body: {
          institution,
          degree,
          field,
          start_date: startDate,
          end_date: endDate || null,
          gpa: gpa || null,
        },
      },
      { onSuccess: () => setEditingId(null) },
    )
  }

  if (isLoading) return <TableSkeleton columns={7} />
  if (!data || data.length === 0) {
    return (
      <EmptyState title="No education yet" hint="Add a school, degree, and dates above." />
    )
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Institution</th>
          <th>Degree</th>
          <th>Field</th>
          <th>Start</th>
          <th>End</th>
          <th>GPA</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {data.map((entry, i) =>
          editingId === entry.id ? (
            <tr key={entry.id} className="editing row-rise" style={rowRiseStyle(i)}>
              <td>
                <input
                  className="cell-edit"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                />
              </td>
              <td>
                <input className="cell-edit" value={degree} onChange={(e) => setDegree(e.target.value)} />
              </td>
              <td>
                <input
                  className="cell-edit"
                  value={field}
                  onChange={(e) => setField(e.target.value)}
                  placeholder="Field"
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
              <td>
                <input
                  className="cell-edit"
                  value={gpa}
                  onChange={(e) => setGpa(e.target.value)}
                  placeholder="GPA"
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
              <td>{entry.institution}</td>
              <td>{entry.degree}</td>
              <td>{entry.field}</td>
              <td className="mono-num">{entry.start_date}</td>
              <td className="mono-num">{entry.end_date ?? ''}</td>
              <td className="mono-num">{entry.gpa ?? ''}</td>
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
