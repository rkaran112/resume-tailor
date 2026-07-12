import { useState, type FormEvent } from 'react'
import { useCreateApplication } from '../../api/applications'
import { API_BASE_URL } from '../../api/client'
import { useFinalizeTailoredResume, type JobDescription, type TailoredResume } from '../../api/tailoring'

interface ExportControlsProps {
  tailoredResumeId: number
  jobDescription: JobDescription
  coverLetterId?: number | null
}

export function ExportControls({
  tailoredResumeId,
  jobDescription,
  coverLetterId = null,
}: ExportControlsProps) {
  const finalize = useFinalizeTailoredResume()
  const createApplication = useCreateApplication()
  const [finalized, setFinalized] = useState<TailoredResume | null>(null)
  const [dateApplied, setDateApplied] = useState(() => new Date().toISOString().slice(0, 10))
  const [loggedApplicationId, setLoggedApplicationId] = useState<number | null>(null)

  async function handleFinalize() {
    const result = await finalize.mutateAsync(tailoredResumeId)
    setFinalized(result)
  }

  async function handleLogApplication(e: FormEvent) {
    e.preventDefault()
    const application = await createApplication.mutateAsync({
      tailored_resume_id: tailoredResumeId,
      cover_letter_id: coverLetterId,
      job_description_id: jobDescription.id,
      company: jobDescription.company,
      role_title: jobDescription.role_title,
      date_applied: dateApplied,
    })
    setLoggedApplicationId(application.id)
  }

  return (
    <div>
      <button onClick={handleFinalize} disabled={finalize.isPending || finalized !== null}>
        {finalize.isPending ? 'Finalizing…' : finalized ? 'Finalized' : 'Finalize'}
      </button>
      {finalize.isError && <span className="error">{finalize.error.message}</span>}
      {finalized && (
        <a href={`${API_BASE_URL}/tailored-resumes/${tailoredResumeId}/download`} download>
          Download {finalized.rendered_filename}
        </a>
      )}

      {finalized && loggedApplicationId === null && (
        <form onSubmit={handleLogApplication}>
          <label>
            Date applied
            <input
              type="date"
              value={dateApplied}
              onChange={(e) => setDateApplied(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={createApplication.isPending}>
            Log this application
          </button>
        </form>
      )}
      {loggedApplicationId !== null && <p>Application logged — see the Applications tab.</p>}
    </div>
  )
}
