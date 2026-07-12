import { useState } from 'react'
import { API_BASE_URL, ApiError } from '../../api/client'
import {
  useCoverLetterPreview,
  useCreateCoverLetter,
  useFinalizeCoverLetter,
  useUpdateCoverLetter,
  type CoverLetter,
} from '../../api/coverLetters'

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
      ? 'Cover letter generation is disabled on this server.'
      : null

  return (
    <div>
      <h2>Cover Letter (opt-in)</h2>

      {!coverLetter && (
        <button onClick={handleGenerate} disabled={create.isPending}>
          {create.isPending ? 'Generating…' : 'Generate cover letter draft'}
        </button>
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
            <button onClick={handleFinalize} disabled={finalize.isPending}>
              {finalize.isPending ? 'Finalizing…' : 'Finalize cover letter'}
            </button>
          </div>
          {update.isError && <p className="error">{update.error.message}</p>}
          {finalize.isError && <p className="error">{finalize.error.message}</p>}
        </div>
      )}

      {coverLetter && coverLetter.status === 'finalized' && (
        <div>
          <p>Cover letter finalized.</p>
          <a href={`${API_BASE_URL}/cover-letters/${coverLetter.id}/download`} download>
            Download {coverLetter.rendered_filename}
          </a>
          {preview.data && (
            <iframe
              title="Cover letter preview"
              srcDoc={preview.data}
              style={{ width: '100%', height: '800px', border: '1px solid var(--border)' }}
            />
          )}
        </div>
      )}
    </div>
  )
}
