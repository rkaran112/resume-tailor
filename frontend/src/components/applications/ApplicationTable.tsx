import { useApplications } from '../../api/applications'
import { rowRiseStyle } from '../../lib/rowStagger'
import { EmptyState } from '../ui/EmptyState'
import { TableSkeleton } from '../ui/Skeleton'
import { StatusPill } from './StatusPill'

interface ApplicationTableProps {
  onSelect: (id: number) => void
}

export function ApplicationTable({ onSelect }: ApplicationTableProps) {
  const { data, isLoading } = useApplications()

  if (isLoading) return <TableSkeleton columns={5} />
  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="Nothing tracked yet"
        hint="Finish a resume on the Tailor tab and save it here to start tracking applications."
      />
    )
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Role</th>
          <th>Applied</th>
          <th>Status</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {data.map((application, i) => (
          <tr key={application.id} className="row-rise" style={rowRiseStyle(i)}>
            <td>{application.company}</td>
            <td>{application.role_title}</td>
            <td className="mono-num">{application.date_applied}</td>
            <td>
              <StatusPill status={application.status} />
            </td>
            <td>
              <button className="btn-ghost" onClick={() => onSelect(application.id)}>
                View
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
