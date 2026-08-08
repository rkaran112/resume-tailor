import { useState } from 'react'
import type { CoverLetter } from '../api/coverLetters'
import { useCreateTailoredResume } from '../api/tailoring'
import type { JobDescription, MatchResult, Selection } from '../api/tailoring'
import { CoverLetterPanel } from '../components/tailor/CoverLetterPanel'
import { ExportControls } from '../components/tailor/ExportControls'
import { JDInput } from '../components/tailor/JDInput'
import { LLMEnhancePanel } from '../components/tailor/LLMEnhancePanel'
import { ResumePreview } from '../components/tailor/ResumePreview'
import { SelectionReview } from '../components/tailor/SelectionReview'
import { TitleMark } from '../components/motion/TitleMark'

export function TailorPage() {
  const [jobDescription, setJobDescription] = useState<JobDescription | null>(null)
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [tailoredResumeId, setTailoredResumeId] = useState<number | null>(null)
  const [coverLetterId, setCoverLetterId] = useState<number | null>(null)

  const createTailoredResume = useCreateTailoredResume()

  function handleMatched(jd: JobDescription, match: MatchResult) {
    setJobDescription(jd)
    setMatchResult(match)
    setTailoredResumeId(null)
    setCoverLetterId(null)
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
      <TitleMark as="h1">Tailor</TitleMark>
      <p className="page-intro">
        Paste a job → pick your bullets → download the PDF. One page, three steps.
      </p>

      {!jobDescription && <JDInput onMatched={handleMatched} />}

      {jobDescription && matchResult && (
        <div className="workbench-frame">
          <div className="workbench">
            <div className="workbench-left">
              <div className="jd-summary">
                <div className="company-role">
                  {jobDescription.company} — {jobDescription.role_title}
                </div>
                <p>{jobDescription.raw_text}</p>
                <button
                  className="btn-ghost"
                  style={{ marginTop: 8, padding: '4px 10px', fontSize: 12 }}
                  onClick={() => {
                    setJobDescription(null)
                    setMatchResult(null)
                    setTailoredResumeId(null)
                    setCoverLetterId(null)
                  }}
                >
                  ← Start over with a different job
                </button>
              </div>

              <SelectionReview
                key={jobDescription.id}
                jobDescription={jobDescription}
                matchResult={matchResult}
                onConfirm={handleConfirmSelection}
                isSubmitting={createTailoredResume.isPending}
              />

              {tailoredResumeId !== null && (
                <>
                  <details className="optional-panel">
                    <summary>Polish the wording — optional</summary>
                    <div className="optional-body">
                      <LLMEnhancePanel tailoredResumeId={tailoredResumeId} />
                    </div>
                  </details>

                  <details className="optional-panel">
                    <summary>Add a cover letter — optional</summary>
                    <div className="optional-body">
                      <CoverLetterPanel
                        tailoredResumeId={tailoredResumeId}
                        onFinalized={(coverLetter: CoverLetter) =>
                          setCoverLetterId(coverLetter.id)
                        }
                      />
                    </div>
                  </details>

                  <ExportControls
                    tailoredResumeId={tailoredResumeId}
                    jobDescription={jobDescription}
                    coverLetterId={coverLetterId}
                  />
                </>
              )}
            </div>

            <div className="workbench-right">
              <h3>Preview</h3>
              {tailoredResumeId === null ? (
                <div className="preview-placeholder">
                  Pick your bullets on the left and create a draft — your resume appears here.
                </div>
              ) : (
                <ResumePreview tailoredResumeId={tailoredResumeId} />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
