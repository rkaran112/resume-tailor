import { useState } from 'react'
import { API_BASE_URL, ApiError } from '../../api/client'
import {
  useCoverLetterPreview,
  useCreateCoverLetter,
  useFinalizeCoverLetter,
  useUpdateCoverLetter,
  type CoverLetter,
} from '../../api/coverLetters'
import { ProgressActivity } from '../ui/ProgressActivity'

interface CoverLetterPanelProps {
  tailoredResumeId: number
  onFinalized: (coverLetter: CoverLetter) => void
}

export function CoverLetterPanel({ tailoredResumeId, onFinalized }: CoverLetterPanelProps) {
  const create = useCreateCoverLetter()
  const update = useUpdateCoverLetter()
  const finalize = useFinalizeCoverLetter()

  const [coverLetter, setCoverLetter] = useState<CoverLetter | null>(null)
  const [draftText, setDraftText] = useState('')

  const preview = useCoverLetterPreview(coverLetter?.status === 'finalized' ? coverLetter.id : null)

  async function handleGenerate() {
    const result = await create.mutateAsync(tailoredResumeId)
    setCoverLetter(result)
    setDraftText(result.edited_text ?? result.generated_text)
  }

  async function handleSaveEdit() {
    if (!coverLetter) return
    const result = await update.mutateAsync({ id: coverLetter.id, editedText: draftText })
    setCoverLetter(result)
  }

  async function handleFinalize() {
    if (!coverLetter) return
    const result = await finalize.mutateAsync(coverLetter.id)
    setCoverLetter(result)
    onFinalized(result)
  }

  const disabledMessage =
    create.error instanceof ApiError && create.error.status === 503
      ? 'Cover letters are turned off on this server. Set ENABLE_COVER_LETTER=true and an ' +
        'ANTHROPIC_API_KEY in the backend .env file, then restart the server.'
      : null

  return (
    <div>
      {!coverLetter && (
        <>
          <p style={{ fontSize: 13.5, marginTop: 0 }}>
            Drafts a short letter from your tailored resume and the job listing. You edit it, then
            make the PDF — it never goes out without you reading it.
          </p>
          <button className="btn-primary" onClick={handleGenerate} disabled={create.isPending}>
            {create.isPending ? 'Writing draft…' : 'Draft a cover letter'}
          </button>
          {create.isPending && (
            <ProgressActivity
              messages={[
                'Reading your resume and the job…',
                'Drafting your letter…',
                'Almost there…',
              ]}
            />
          )}
        </>
      )}
      {disabledMessage && <p className="error">{disabledMessage}</p>}
      {create.isError && !disabledMessage && <p className="error">{create.error.message}</p>}

      {coverLetter && coverLetter.status === 'draft' && (
        <div>
          <textarea
            value={draftText}
            onChange={(e) => setDraftText(e.target.value)}
            rows={12}
            style={{ width: '100%' }}
          />
          <div>
            <button onClick={handleSaveEdit} disabled={update.isPending}>
              {update.isPending ? 'Saving…' : 'Save edits'}
            </button>
            <button className="btn-primary" onClick={handleFinalize} disabled={finalize.isPending}>
              {finalize.isPending ? 'Making PDF…' : 'Make the PDF'}
            </button>
          </div>
          {update.isError && <p className="error">{update.error.message}</p>}
          {finalize.isError && <p className="error">{finalize.error.message}</p>}
        </div>
      )}

      {coverLetter && coverLetter.status === 'finalized' && (
        <div>
          <p>Cover letter ready.</p>
          <a href={`${API_BASE_URL}/cover-letters/${coverLetter.id}/download`} download>
            Download {coverLetter.rendered_filename}
          </a>
          {preview.data && (
            <div className="preview-frame" style={{ maxWidth: 420 }}>
              <iframe title="Cover letter preview" srcDoc={preview.data} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
