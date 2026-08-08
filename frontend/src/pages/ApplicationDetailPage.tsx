import { useState } from 'react'
import {
  useApplication,
  useChangeApplicationStatus,
  type ApplicationStatus,
} from '../api/applications'
import { API_BASE_URL } from '../api/client'
import { StatusPill } from '../components/applications/StatusPill'
import { StatusTimeline } from '../components/applications/StatusTimeline'
import { TitleMark } from '../components/motion/TitleMark'

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

  function handleChangeStatus() {
    changeStatus.mutate(
      { id: applicationId, status: nextStatus, note: note || undefined },
      { onSuccess: () => setNote('') },
    )
  }

  return (
    <div>
      <button className="btn-ghost detail-back" onClick={onBack}>
        &larr; Back to applications
      </button>

      {isLoading || !application ? (
        <p className="page-intro">Loading…</p>
      ) : (
        <>
          <div className="detail-head">
            <TitleMark as="h1">
              {application.company} — {application.role_title}
            </TitleMark>
            <div className="detail-meta">
              <StatusPill status={application.status} />
              <span className="applied">Applied {application.date_applied}</span>
            </div>
            {application.notes && <p style={{ marginTop: -8 }}>{application.notes}</p>}
          </div>

          {(application.tailored_resume_id !== null || application.cover_letter_id !== null) && (
            <div className="detail-docs">
              {application.tailored_resume_id !== null && (
                <a
                  className="doc-link"
                  href={`${API_BASE_URL}/tailored-resumes/${application.tailored_resume_id}/download`}
                >
                  Resume PDF
                </a>
              )}
              {application.cover_letter_id !== null && (
                <a
                  className="doc-link"
                  href={`${API_BASE_URL}/cover-letters/${application.cover_letter_id}/download`}
                >
                  Cover letter PDF
                </a>
              )}
            </div>
          )}

          <div className="panel">
            <TitleMark>Update status</TitleMark>
            <div className="status-form">
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
              <input
                placeholder="Add a note (optional)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
              <button
                className="btn-primary"
                onClick={handleChangeStatus}
                disabled={changeStatus.isPending}
              >
                {changeStatus.isPending ? 'Saving…' : 'Save update'}
              </button>
            </div>
            {changeStatus.isError && <span className="error">{changeStatus.error.message}</span>}
          </div>

          <div className="panel">
            <TitleMark>Timeline</TitleMark>
            <StatusTimeline events={application.status_events} />
          </div>
        </>
      )}
    </div>
  )
}
