import type { ApplicationStatusEvent } from '../../api/applications'
import { StatusPill } from './StatusPill'

interface StatusTimelineProps {
  events: ApplicationStatusEvent[]
}

export function StatusTimeline({ events }: StatusTimelineProps) {
  if (events.length === 0) {
    return <p className="timeline-note">No status changes yet.</p>
  }

  // Newest first reads as a running history.
  const ordered = [...events].sort(
    (a, b) => new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime(),
  )

  return (
    <ul className="timeline">
      {ordered.map((event) => (
        <li key={event.id} className="timeline-item">
          <span className="timeline-dot" />
          <div className="timeline-row">
            <StatusPill status={event.status} />
            <span className="timeline-when">{new Date(event.changed_at).toLocaleString()}</span>
          </div>
          {event.note && <div className="timeline-note">{event.note}</div>}
        </li>
      ))}
    </ul>
  )
}
