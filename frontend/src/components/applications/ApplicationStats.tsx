import { useApplications, type ApplicationStatus } from '../../api/applications'

export function ApplicationStats() {
  const { data } = useApplications()
  if (!data || data.length === 0) return null

  const count = (statuses: ApplicationStatus[]) =>
    data.filter((a) => statuses.includes(a.status)).length

  const stats: Array<{ num: number; label: string; accent?: boolean }> = [
    { num: data.length, label: 'Total sent' },
    { num: count(['applied', 'interview']), label: 'In progress' },
    { num: count(['interview']), label: 'Interviews' },
    { num: count(['offer']), label: 'Offers', accent: true },
  ]

  return (
    <div className="stat-row">
      {stats.map((s) => (
        <div className="stat" key={s.label}>
          <div className={`stat-num${s.accent ? ' accent' : ''}`}>{s.num}</div>
          <div className="stat-label">{s.label}</div>
        </div>
      ))}
    </div>
  )
}
