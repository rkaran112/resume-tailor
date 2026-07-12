import { useApplications } from '../../api/applications'

interface ApplicationTableProps {
  onSelect: (id: number) => void
}

export function ApplicationTable({ onSelect }: ApplicationTableProps) {
  const { data, isLoading } = useApplications()

  if (isLoading) return <p>Loading…</p>
  if (!data || data.length === 0) return <p>No applications logged yet.</p>

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
        {data.map((application) => (
          <tr key={application.id}>
            <td>{application.company}</td>
            <td>{application.role_title}</td>
            <td>{application.date_applied}</td>
            <td>{application.status}</td>
            <td>
              <button onClick={() => onSelect(application.id)}>View</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
