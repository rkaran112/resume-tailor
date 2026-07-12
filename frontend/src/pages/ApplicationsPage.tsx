import { useState } from 'react'
import { ApplicationTable } from '../components/applications/ApplicationTable'
import { ApplicationDetailPage } from './ApplicationDetailPage'

export function ApplicationsPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  if (selectedId !== null) {
    return <ApplicationDetailPage applicationId={selectedId} onBack={() => setSelectedId(null)} />
  }

  return (
    <div>
      <h1>Resume Tailor — Applications</h1>
      <ApplicationTable onSelect={setSelectedId} />
    </div>
  )
}
