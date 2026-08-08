const STATUS_PILL_CLASS: Record<string, string> = {
  applied: 'pill-info',
  interview: 'pill-warning',
  offer: 'pill-success',
  rejected: 'pill-error',
  withdrawn: 'pill-neutral',
}

interface StatusPillProps {
  status: string
}

export function StatusPill({ status }: StatusPillProps) {
  const cls = STATUS_PILL_CLASS[status] ?? 'pill-neutral'
  return <span className={`pill ${cls}`}>{status}</span>
}
