import { useState } from 'react'
import { ApiError } from '../../api/client'
import {
  useAcceptEnhancedBullets,
  useEnhanceBullets,
  type EnhancedBullet,
} from '../../api/tailoring'

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
      ? 'LLM bullet enhancement is disabled on this server.'
      : null

  return (
    <div>
      <h2>LLM Bullet Enhancement (opt-in)</h2>
      <button onClick={handleEnhance} disabled={enhance.isPending}>
        {enhance.isPending ? 'Enhancing…' : 'Suggest rewrites'}
      </button>
      {disabledMessage && <p className="error">{disabledMessage}</p>}
      {enhance.isError && !disabledMessage && (
        <p className="error">{enhance.error.message}</p>
      )}

      {suggestions && suggestions.length === 0 && <p>No bullets to enhance.</p>}

      {suggestions && suggestions.length > 0 && (
        <div>
          {suggestions.map((suggestion) => (
            <div key={suggestion.bullet_id} style={{ marginBottom: 10 }}>
              <label>
                <input
                  type="checkbox"
                  checked={acceptedIds.has(suggestion.bullet_id)}
                  onChange={() => toggle(suggestion.bullet_id)}
                />
                {suggestion.flagged && (
                  <span className="error"> large change — review carefully</span>
                )}
              </label>
              <div style={{ color: 'gray' }}>Original: {suggestion.original}</div>
              <div>Suggested: {suggestion.suggested}</div>
            </div>
          ))}
          <button onClick={handleApply} disabled={accept.isPending || acceptedIds.size === 0}>
            Apply accepted rewrites
          </button>
        </div>
      )}
    </div>
  )
}
