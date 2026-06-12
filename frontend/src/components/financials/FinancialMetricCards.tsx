import type { ReactNode } from 'react'
import { TooltipInfo } from '@/components/ui/Tooltip'
import { formatStatementCurrency, formatStatementPercent } from '@/utils/statementFormat'
import type { ISMargins, ISTotals } from '@/types/incomeStatement'

type Accent = 'blue' | 'green' | 'amber' | 'slate'

function Metric({
  label,
  value,
  negative,
  sub,
  help,
  accent,
}: {
  label: string
  value: string
  negative: boolean
  sub?: ReactNode
  help?: string
  accent: Accent
}) {
  return (
    <div className={`fin-metric fin-metric--${accent}`}>
      <div className="fin-metric__label">
        {label}
        {help && <TooltipInfo text={help} />}
      </div>
      <div className={`fin-metric__value${negative ? ' fin-metric__value--neg' : ''}`}>{value}</div>
      {sub && <div className="fin-metric__sub">{sub}</div>}
    </div>
  )
}

export function FinancialMetricCards({
  totals,
  margins,
  currency,
}: {
  totals: ISTotals
  margins: ISMargins
  currency: string
}) {
  const cur = (v: number) => formatStatementCurrency(v, currency)

  return (
    <div className="fin-metric-grid">
      <Metric
        label="Total Revenue" accent="blue" negative={totals.total_revenue < 0}
        value={cur(totals.total_revenue)}
      />
      <Metric
        label="Gross Profit" accent="blue" negative={totals.gross_profit < 0}
        value={cur(totals.gross_profit)}
        sub={`Gross margin ${formatStatementPercent(margins.gross_margin_total_pct)}`}
      />
      <Metric
        label="EBITDA" accent={totals.ebitda >= 0 ? 'green' : 'amber'} negative={totals.ebitda < 0}
        value={cur(totals.ebitda)} help="Operating profit excluding depreciation and amortisation."
        sub={`EBITDA margin ${formatStatementPercent(margins.ebitda_margin_total_pct)}`}
      />
      <Metric
        label="Operating Profit" accent={totals.operating_profit >= 0 ? 'green' : 'amber'}
        negative={totals.operating_profit < 0} value={cur(totals.operating_profit)}
        sub={`Operating margin ${formatStatementPercent(margins.operating_margin_total_pct)}`}
      />
      <Metric
        label="Profit Before Tax" accent="slate" negative={totals.profit_before_tax < 0}
        value={cur(totals.profit_before_tax)}
      />
      <Metric
        label="Profit for the Period" accent={totals.profit_for_period >= 0 ? 'green' : 'amber'}
        negative={totals.profit_for_period < 0} value={cur(totals.profit_for_period)}
        sub={`Net margin ${formatStatementPercent(margins.net_margin_total_pct)}`}
      />
    </div>
  )
}
