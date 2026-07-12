import { useTailoredResumePreview } from '../../api/tailoring'

interface ResumePreviewProps {
  tailoredResumeId: number
}

export function ResumePreview({ tailoredResumeId }: ResumePreviewProps) {
  const { data: html, isLoading, error } = useTailoredResumePreview(tailoredResumeId)

  if (isLoading) return <p>Loading preview…</p>
  if (error) return <p className="error">{error.message}</p>

  return (
    <iframe
      title="Resume preview"
      srcDoc={html}
      style={{ width: '100%', height: '800px', border: '1px solid var(--border)' }}
    />
  )
}
