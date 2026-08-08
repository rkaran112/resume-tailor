import { useTailoredResumePreview } from '../../api/tailoring'
import { PagePreviewSkeleton } from '../ui/Skeleton'

interface ResumePreviewProps {
  tailoredResumeId: number
}

export function ResumePreview({ tailoredResumeId }: ResumePreviewProps) {
  const { data: html, isLoading, error } = useTailoredResumePreview(tailoredResumeId)

  if (isLoading) return <PagePreviewSkeleton />
  if (error) return <p className="error">{error.message}</p>

  return (
    <div className="preview-frame">
      <iframe title="Resume preview" srcDoc={html} />
    </div>
  )
}
