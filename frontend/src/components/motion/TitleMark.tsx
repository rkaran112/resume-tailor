import { motion, useReducedMotion } from 'framer-motion'
import type { ReactNode } from 'react'

interface TitleMarkProps {
  children: ReactNode
  className?: string
  as?: 'h1' | 'h2'
}

/**
 * Section header with a self-drawing underline stroke — plays once when the
 * header scrolls into view. Short duration is deliberate: this fires on
 * every `.title-mark` usage app-wide, including on every tab remount.
 */
export function TitleMark({ children, className, as: Tag = 'h2' }: TitleMarkProps) {
  const reduceMotion = useReducedMotion()

  return (
    <Tag className={`title-mark${className ? ` ${className}` : ''}`}>
      {children}
      <svg className="title-mark-svg" viewBox="0 0 100 8" preserveAspectRatio="none" aria-hidden="true">
        <motion.path
          d="M1 6 Q20 2 45 5 T95 4"
          strokeWidth={3}
          strokeLinecap="round"
          initial={reduceMotion ? false : { pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: reduceMotion ? 0 : 0.28, ease: 'easeOut' }}
        />
      </svg>
    </Tag>
  )
}
