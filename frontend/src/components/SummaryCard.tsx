import type { ReactNode } from 'react'
import { TooltipInfo } from './ui/Tooltip'

type Accent = 'blue' | 'green' | 'amber' | 'slate'

export function SummaryCard({
  label,
  value,
  hint,
  help,
  accent = 'slate',
}: {
  label: string
  value: ReactNode
  hint?: string
  help?: string
  accent?: Accent
}) {
  return (
    <div className={`stat stat__accent-${accent}`}>
      <div className="stat__label">
        {label}
        {help && <TooltipInfo text={help} />}
      </div>
      <div className="stat__value">{value}</div>
      {hint && <div className="stat__hint">{hint}</div>}
    </div>
  )
}
