import { educationHooks } from '../../api/bank'

export function EducationList() {
  const { data, isLoading } = educationHooks.useList()
  const del = educationHooks.useDelete()

  if (isLoading) return <p>Loading…</p>

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
        {data?.map((entry) => (
          <tr key={entry.id}>
            <td>{entry.institution}</td>
            <td>{entry.degree}</td>
            <td>{entry.field}</td>
            <td>{entry.start_date}</td>
            <td>{entry.end_date ?? ''}</td>
            <td>{entry.gpa ?? ''}</td>
            <td>
              <button onClick={() => del.mutate(entry.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
