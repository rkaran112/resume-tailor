import { experienceHooks } from '../../api/bank'

export function ExperienceList() {
  const { data, isLoading } = experienceHooks.useList()
  const del = experienceHooks.useDelete()

  if (isLoading) return <p>Loading…</p>

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
        {data?.map((entry) => (
          <tr key={entry.id}>
            <td>{entry.company}</td>
            <td>{entry.title}</td>
            <td>{entry.location}</td>
            <td>{entry.start_date}</td>
            <td>{entry.end_date ?? 'Present'}</td>
            <td>
              <button onClick={() => del.mutate(entry.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
