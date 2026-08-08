import { motion, useMotionValue, useReducedMotion, useSpring } from 'framer-motion'
import type { MouseEvent, ReactNode } from 'react'

interface MagneticButtonProps {
  children: ReactNode
  onClick?: () => void
  className?: string
}

const PULL_STRENGTH = 0.35

/**
 * Cursor-attraction hover pull, bounded by a spring so it always snaps back.
 * Scoped to hero-tier CTAs only — see DESIGN.md Decisions Log.
 */
export function MagneticButton({ children, onClick, className }: MagneticButtonProps) {
  const reduceMotion = useReducedMotion()
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 200, damping: 15, mass: 0.4 })
  const springY = useSpring(y, { stiffness: 200, damping: 15, mass: 0.4 })

  if (reduceMotion) {
    return (
      <button className={className} onClick={onClick}>
        {children}
      </button>
    )
  }

  function handleMouseMove(e: MouseEvent<HTMLButtonElement>) {
    const rect = e.currentTarget.getBoundingClientRect()
    x.set((e.clientX - (rect.left + rect.width / 2)) * PULL_STRENGTH)
    y.set((e.clientY - (rect.top + rect.height / 2)) * PULL_STRENGTH)
  }

  function handleMouseLeave() {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.button
      className={className}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ x: springX, y: springY }}
    >
      {children}
    </motion.button>
  )
}
