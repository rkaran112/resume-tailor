import type { ApplicationStatusEvent } from '../../api/applications'

interface StatusTimelineProps {
  events: ApplicationStatusEvent[]
}

export function StatusTimeline({ events }: StatusTimelineProps) {
  return (
    <ul>
      {events.map((event) => (
        <li key={event.id}>
          <strong>{event.status}</strong> — {new Date(event.changed_at).toLocaleString()}
          {event.note && <div>{event.note}</div>}
        </li>
      ))}
    </ul>
  )
}
