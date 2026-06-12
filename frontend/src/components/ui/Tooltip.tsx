import type { ReactNode } from 'react'

/** Inline "?" info bubble used next to financial-term labels. */
export function TooltipInfo({ text }: { text: string }) {
  return (
    <span className="tooltip" aria-label={text}>
      <span className="tooltip__icon">?</span>
      <span className="tooltip__bubble" role="tooltip">
        {text}
      </span>
    </span>
  )
}

/** Generic hover tooltip wrapper for arbitrary trigger content. */
export function Tooltip({ text, children }: { text: string; children: ReactNode }) {
  return (
    <span className="tooltip">
      {children}
      <span className="tooltip__bubble" role="tooltip">
        {text}
      </span>
    </span>
  )
}
