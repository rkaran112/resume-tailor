import type { CSSProperties } from 'react'

interface DrawMarkProps {
  variant: 'check' | 'strike'
  delaySeconds: number
  className?: string
}

/**
 * A literally hand-drawn mark (checkmark or strike-through), stroked in via
 * `pathLength` + `stroke-dashoffset` rather than faded/scaled. Dependency-free
 * so it can share a CSS-driven infinite loop with the hero's other marks —
 * see `.draw-mark*` / `draw-check` / `draw-strike` in index.css.
 */
export function DrawMark({ variant, delaySeconds, className }: DrawMarkProps) {
  const pathStyle: CSSProperties = { animationDelay: `${delaySeconds}s` }
  const wrapperClass = `draw-mark draw-mark-${variant}${className ? ` ${className}` : ''}`

  if (variant === 'check') {
    return (
      <svg className={wrapperClass} viewBox="0 0 16 16" aria-hidden="true">
        <path
          d="M3 8.5 L6.5 12 L13 3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          pathLength={1}
          style={pathStyle}
        />
      </svg>
    )
  }

  return (
    <svg className={wrapperClass} viewBox="0 0 100 6" preserveAspectRatio="none" aria-hidden="true">
      <path d="M1 3 Q30 1 50 3 T99 3" strokeLinecap="round" pathLength={1} style={pathStyle} />
    </svg>
  )
}
