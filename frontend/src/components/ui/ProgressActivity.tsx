import { useEffect, useState } from 'react'

interface ProgressActivityProps {
  // Rotating status lines shown one at a time so a long wait feels like
  // progress rather than a hang. Falls back to a single label if one is given.
  messages: string[]
  intervalMs?: number
}

export function ProgressActivity({ messages, intervalMs = 2600 }: ProgressActivityProps) {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    if (messages.length <= 1) return
    const timer = setInterval(() => {
      // Stop advancing at the last message; we don't know when work finishes,
      // and cycling back to "starting" would read as a stall.
      setIndex((i) => (i < messages.length - 1 ? i + 1 : i))
    }, intervalMs)
    return () => clearInterval(timer)
  }, [messages.length, intervalMs])

  return (
    <div className="activity" role="status" aria-live="polite">
      <span className="activity-label">{messages[index] ?? 'Working…'}</span>
      <div className="progress-track" />
    </div>
  )
}
