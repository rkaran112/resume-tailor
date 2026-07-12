import { useState } from 'react'
import { useCreateTailoredResume } from '../api/tailoring'
import type { JobDescription, MatchResult, Selection } from '../api/tailoring'
import { ExportControls } from '../components/tailor/ExportControls'
import { JDInput } from '../components/tailor/JDInput'
import { LLMEnhancePanel } from '../components/tailor/LLMEnhancePanel'
import { ResumePreview } from '../components/tailor/ResumePreview'
import { SelectionReview } from '../components/tailor/SelectionReview'

export function TailorPage() {
  const [jobDescription, setJobDescription] = useState<JobDescription | null>(null)
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [tailoredResumeId, setTailoredResumeId] = useState<number | null>(null)

  const createTailoredResume = useCreateTailoredResume()

  function handleMatched(jd: JobDescription, match: MatchResult) {
    setJobDescription(jd)
    setMatchResult(match)
    setTailoredResumeId(null)
  }

  async function handleConfirmSelection(selection: Selection) {
    if (!jobDescription || !matchResult) return
    const tailoredResume = await createTailoredResume.mutateAsync({
      job_description_id: jobDescription.id,
      scoring_metadata: matchResult.scoring_metadata,
      ...selection,
    })
    setTailoredResumeId(tailoredResume.id)
  }

  return (
    <div>
      <h1>Resume Tailor — Tailor</h1>

      <JDInput onMatched={handleMatched} />

      {jobDescription && matchResult && (
        <SelectionReview
          key={jobDescription.id}
          jobDescription={jobDescription}
          matchResult={matchResult}
          onConfirm={handleConfirmSelection}
          isSubmitting={createTailoredResume.isPending}
        />
      )}

      {tailoredResumeId !== null && (
        <>
          <LLMEnhancePanel tailoredResumeId={tailoredResumeId} />

          <h2>Preview</h2>
          <ResumePreview tailoredResumeId={tailoredResumeId} />
          {jobDescription && (
            <ExportControls tailoredResumeId={tailoredResumeId} jobDescription={jobDescription} />
          )}
        </>
      )}
    </div>
  )
}
