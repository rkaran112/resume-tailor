import { skillHooks } from '../../api/bank'

export function SkillList() {
  const { data, isLoading } = skillHooks.useList()
  const del = skillHooks.useDelete()

  if (isLoading) return <p>Loading…</p>

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Category</th>
          <th>Tags</th>
          <th />
        </tr>
      </thead>
      <tbody>
        {data?.map((skill) => (
          <tr key={skill.id}>
            <td>{skill.name}</td>
            <td>{skill.category}</td>
            <td>{skill.tags.join(', ')}</td>
            <td>
              <button onClick={() => del.mutate(skill.id)}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
