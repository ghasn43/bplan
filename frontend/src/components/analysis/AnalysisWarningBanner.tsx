import { useState } from 'react'
import type { FinancialAnalysisWarning, Severity } from '@/types/financialAnalysis'

const ICON: Record<Severity, string> = { info: 'ℹ', warning: '⚠', critical: '⛔' }
const BANNER: Record<Severity, string> = { info: 'banner--info', warning: 'banner--warning', critical: 'banner--warning' }
const ORDER: Record<Severity, number> = { critical: 0, warning: 1, info: 2 }

export function AnalysisWarningBanner({ warnings }: { warnings: FinancialAnalysisWarning[] }) {
  const [open, setOpen] = useState(true)
  if (warnings.length === 0) return null
  const sorted = [...warnings].sort((a, b) => ORDER[a.severity] - ORDER[b.severity])
  return (
    <div className="card">
      <button className="card__header" style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setOpen((o) => !o)}>
        <div className="card__header-main">
          <div className="card__icon" style={{ background: 'var(--amber-50)', color: 'var(--amber-600)' }}>⚠</div>
          <div style={{ textAlign: 'left' }}>
            <div className="card__title">Financial health notes</div>
            <div className="card__subtitle">{warnings.length} item(s)</div>
          </div>
        </div>
        <span className={`collapsible__chevron${open ? ' collapsible__chevron--open' : ''}`}>▸</span>
      </button>
      {open && (
        <div className="card__body stack--sm">
          {sorted.map((w, i) => (
            <div key={i} className={`banner ${BANNER[w.severity]}`}>
              <span className="banner__icon">{ICON[w.severity]}</span>
              <div>{w.message}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
