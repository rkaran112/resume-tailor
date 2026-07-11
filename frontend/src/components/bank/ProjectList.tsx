import { projectHooks } from '../../api/bank'

export function ProjectList() {
  const { data, isLoading } = projectHooks.useList()
  const del = projectHooks.useDelete()

  if (isLoading) return <p>Loading…</p>

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
        {data?.map((project) => (
          <tr key={project.id}>
            <td>{project.name}</td>
            <td>{project.description}</td>
            <td>{project.tech_tags.join(', ')}</td>
            <td>{project.link}</td>
            <td>
              <button onClick={() => del.mutate(project.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
