import { useState, type FormEvent } from 'react'
import {
  useCreateJobDescription,
  useMatchJobDescription,
  type JobDescription,
  type MatchResult,
} from '../../api/tailoring'

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
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Company"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
        required
      />
      <input
        placeholder="Role title"
        value={roleTitle}
        onChange={(e) => setRoleTitle(e.target.value)}
        required
      />
      <textarea
        placeholder="Paste the job description here"
        value={rawText}
        onChange={(e) => setRawText(e.target.value)}
        rows={10}
        required
        style={{ width: '100%' }}
      />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Matching…' : 'Match against bank'}
      </button>
      {error && <span className="error">{error.message}</span>}
    </form>
  )
}
