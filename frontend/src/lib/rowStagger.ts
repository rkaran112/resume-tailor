import type { CSSProperties } from 'react'

const STEP_SECONDS = 0.04
const MAX_DELAY_SECONDS = 0.4

/** Staggered mount delay for list/table rows — same idiom as HomePage's step-card stagger. */
export function rowRiseStyle(index: number): CSSProperties {
  return { animationDelay: `${Math.min(index * STEP_SECONDS, MAX_DELAY_SECONDS)}s` }
}
