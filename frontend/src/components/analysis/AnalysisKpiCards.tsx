import { TooltipInfo } from '@/components/ui/Tooltip'
import { formatByKind } from '@/utils/statementFormat'
import type { FinancialAnalysisKPI } from '@/types/financialAnalysis'

const GROUPS: { key: string; label: string }[] = [
  { key: 'profitability', label: 'Profitability' },
  { key: 'liquidity', label: 'Liquidity' },
  { key: 'leverage', label: 'Leverage' },
  { key: 'efficiency', label: 'Efficiency' },
  { key: 'cash', label: 'Cash' },
]

export function AnalysisKpiCards({ kpis, currency }: { kpis: FinancialAnalysisKPI[]; currency: string }) {
  return (
    <div className="stack--sm">
      {GROUPS.map((g) => {
        const items = kpis.filter((k) => k.group === g.key)
        if (items.length === 0) return null
        return (
          <div key={g.key}>
            <div className="kpi-group-label">{g.label}</div>
            <div className="kpi-grid">
              {items.map((k) => {
                const tone = k.good === true ? 'good' : k.good === false ? 'bad' : 'neutral'
                return (
                  <div className={`kpi-tile kpi-tile--${tone}`} key={k.key}>
                    <div className="kpi-tile__label">
                      {k.label}
                      {k.hint && <TooltipInfo text={k.hint} />}
                    </div>
                    <div className="kpi-tile__value">{formatByKind(k.value, k.format, currency, true)}</div>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
