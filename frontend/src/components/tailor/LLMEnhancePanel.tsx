import { useState } from 'react'
import { ApiError } from '../../api/client'
import {
  useAcceptEnhancedBullets,
  useEnhanceBullets,
  type EnhancedBullet,
} from '../../api/tailoring'
import { ProgressActivity } from '../ui/ProgressActivity'

interface LLMEnhancePanelProps {
  tailoredResumeId: number
}

export function LLMEnhancePanel({ tailoredResumeId }: LLMEnhancePanelProps) {
  const enhance = useEnhanceBullets()
  const accept = useAcceptEnhancedBullets()
  const [suggestions, setSuggestions] = useState<EnhancedBullet[] | null>(null)
  const [acceptedIds, setAcceptedIds] = useState<Set<number>>(new Set())

  async function handleEnhance() {
    const result = await enhance.mutateAsync(tailoredResumeId)
    setSuggestions(result.bullets)
    setAcceptedIds(new Set())
  }

  function toggle(bulletId: number) {
    setAcceptedIds((prev) => {
      const next = new Set(prev)
      if (next.has(bulletId)) {
        next.delete(bulletId)
      } else {
        next.add(bulletId)
      }
      return next
    })
  }

  async function handleApply() {
    if (!suggestions) return
    const accepted: Record<number, string> = {}
    for (const suggestion of suggestions) {
      if (acceptedIds.has(suggestion.bullet_id)) {
        accepted[suggestion.bullet_id] = suggestion.suggested
      }
    }
    await accept.mutateAsync({ id: tailoredResumeId, accepted })
    setSuggestions(null)
  }

  const disabledMessage =
    enhance.error instanceof ApiError && enhance.error.status === 503
      ? 'Wording polish is turned off on this server. Set ENABLE_LLM_ENHANCE=true and an ' +
        'ANTHROPIC_API_KEY in the backend .env file, then restart the server.'
      : null

  return (
    <div>
      <p style={{ fontSize: 13.5, marginTop: 0 }}>
        Ask AI to tighten your chosen bullets. Every suggestion appears next to the original, and
        nothing changes unless you check it and apply.
      </p>
      <button className="btn-primary" onClick={handleEnhance} disabled={enhance.isPending}>
        {enhance.isPending ? 'Writing suggestions…' : 'Suggest rewrites'}
      </button>
      {enhance.isPending && (
        <ProgressActivity
          messages={[
            'Reading your chosen bullets…',
            'Drafting tighter wording…',
            'Almost there…',
          ]}
        />
      )}
      {disabledMessage && <p className="error">{disabledMessage}</p>}
      {enhance.isError && !disabledMessage && (
        <p className="error">{enhance.error.message}</p>
      )}

      {suggestions && suggestions.length === 0 && <p>No bullets to polish.</p>}

      {suggestions && suggestions.length > 0 && (
        <div>
          {suggestions.map((suggestion) => (
            <div key={suggestion.bullet_id} className="card" style={{ marginBottom: 10 }}>
              <label>
                <input
                  type="checkbox"
                  checked={acceptedIds.has(suggestion.bullet_id)}
                  onChange={() => toggle(suggestion.bullet_id)}
                />
                {suggestion.flagged && (
                  <span className="pill pill-warning"> big change — read closely</span>
                )}
              </label>
              <div style={{ color: 'var(--ink-faint)', fontSize: 13 }}>
                Original: {suggestion.original}
              </div>
              <div style={{ fontSize: 13.5 }}>Suggested: {suggestion.suggested}</div>
            </div>
          ))}
          <button
            className="btn-primary"
            onClick={handleApply}
            disabled={accept.isPending || acceptedIds.size === 0}
          >
            Apply checked rewrites
          </button>
        </div>
      )}
    </div>
  )
}
