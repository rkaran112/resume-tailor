import { useState, type FormEvent } from 'react'
import {
  useCreateJobDescription,
  useMatchJobDescription,
  type JobDescription,
  type MatchResult,
} from '../../api/tailoring'
import { TitleMark } from '../motion/TitleMark'

interface JDInputProps {
  onMatched: (jobDescription: JobDescription, matchResult: MatchResult) => void
}

export function JDInput({ onMatched }: JDInputProps) {
  const createJobDescription = useCreateJobDescription()
  const match = useMatchJobDescription()

  const [company, setCompany] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [rawText, setRawText] = useState('')

  const isPending = createJobDescription.isPending || match.isPending
  const error = createJobDescription.error ?? match.error

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const jobDescription = await createJobDescription.mutateAsync({
      company,
      role_title: roleTitle,
      raw_text: rawText,
    })
    const matchResult = await match.mutateAsync({
      jobDescriptionId: jobDescription.id,
      body: {},
    })
    onMatched(jobDescription, matchResult)
  }

  return (
    <div className="card" style={{ maxWidth: 640 }}>
      <div className="eyebrow" style={{ marginBottom: 8 }}>Step 1 · Paste the job</div>
      <TitleMark>Paste a job</TitleMark>
      <p style={{ fontSize: 13.5, marginTop: 4 }}>
        We compare the listing against your bank and pick the bullets that fit best.
      </p>
      <form onSubmit={handleSubmit} style={{ flexDirection: 'column', alignItems: 'stretch' }}>
        <div style={{ display: 'flex', gap: 10 }}>
          <input
            placeholder="Company"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            required
            style={{ flex: 1 }}
          />
          <input
            placeholder="Role title"
            value={roleTitle}
            onChange={(e) => setRoleTitle(e.target.value)}
            required
            style={{ flex: 1 }}
          />
        </div>
        <textarea
          placeholder="Paste the job description here"
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          rows={10}
          required
          style={{ width: '100%' }}
        />
        <button className="btn-primary" type="submit" disabled={isPending}>
          {isPending ? 'Finding matches…' : 'Find my matches'}
        </button>
        {error && <span className="error">{error.message}</span>}
      </form>
    </div>
  )
}
