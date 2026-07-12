import { useState } from 'react'
import {
  useApplication,
  useChangeApplicationStatus,
  type ApplicationStatus,
} from '../api/applications'
import { API_BASE_URL } from '../api/client'
import { StatusTimeline } from '../components/applications/StatusTimeline'

const STATUSES: ApplicationStatus[] = ['applied', 'interview', 'offer', 'rejected', 'withdrawn']

interface ApplicationDetailPageProps {
  applicationId: number
  onBack: () => void
}

export function ApplicationDetailPage({ applicationId, onBack }: ApplicationDetailPageProps) {
  const { data: application, isLoading } = useApplication(applicationId)
  const changeStatus = useChangeApplicationStatus()
  const [nextStatus, setNextStatus] = useState<ApplicationStatus>('applied')
  const [note, setNote] = useState('')

  if (isLoading || !application) return <p>Loading…</p>

  function handleChangeStatus() {
    changeStatus.mutate(
      { id: applicationId, status: nextStatus, note: note || undefined },
      { onSuccess: () => setNote('') }
    )
  }

  return (
    <div>
      <button onClick={onBack}>&larr; Back to applications</button>
      <h1>
        {application.company} — {application.role_title}
      </h1>
      <p>Applied {application.date_applied}</p>
      <p>
        Status: <strong>{application.status}</strong>
      </p>
      {application.notes && <p>Notes: {application.notes}</p>}
      {application.tailored_resume_id !== null && (
        <p>
          <a
            href={`${API_BASE_URL}/tailored-resumes/${application.tailored_resume_id}/download`}
          >
            Download resume
          </a>
        </p>
      )}
      {application.cover_letter_id !== null && (
        <p>
          <a href={`${API_BASE_URL}/cover-letters/${application.cover_letter_id}/download`}>
            Download cover letter
          </a>
        </p>
      )}

      <h2>Change status</h2>
      <select
        value={nextStatus}
        onChange={(e) => setNextStatus(e.target.value as ApplicationStatus)}
      >
        {STATUSES.map((status) => (
          <option key={status} value={status}>
            {status}
          </option>
        ))}
      </select>
      <input placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)} />
      <button onClick={handleChangeStatus} disabled={changeStatus.isPending}>
        Update status
      </button>

      <h2>Timeline</h2>
      <StatusTimeline events={application.status_events} />
    </div>
  )
}
