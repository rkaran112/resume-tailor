import { useState } from 'react'
import { API_BASE_URL } from '../../api/client'
import { useFinalizeTailoredResume, type TailoredResume } from '../../api/tailoring'

interface ExportControlsProps {
  tailoredResumeId: number
}

export function ExportControls({ tailoredResumeId }: ExportControlsProps) {
  const finalize = useFinalizeTailoredResume()
  const [finalized, setFinalized] = useState<TailoredResume | null>(null)

  async function handleFinalize() {
    const result = await finalize.mutateAsync(tailoredResumeId)
    setFinalized(result)
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
    </div>
  )
}
