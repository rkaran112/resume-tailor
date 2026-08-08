import { useState } from 'react'
import { ApplicationStats } from '../components/applications/ApplicationStats'
import { ApplicationTable } from '../components/applications/ApplicationTable'
import { TitleMark } from '../components/motion/TitleMark'
import { ApplicationDetailPage } from './ApplicationDetailPage'

export function ApplicationsPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  if (selectedId !== null) {
    return <ApplicationDetailPage applicationId={selectedId} onBack={() => setSelectedId(null)} />
  }

  return (
    <div>
      <TitleMark as="h1">Track</TitleMark>
      <p className="page-intro">
        Every application you've sent — which resume went out, when, and where it stands now.
      </p>
      <ApplicationStats />
      <ApplicationTable onSelect={setSelectedId} />
    </div>
  )
}
