import type { ReactNode } from 'react'
import { Badge } from '@/components/ui/Badge'
import { formatStatementCurrency } from '@/utils/statementFormat'
import type { BalanceSheetSummary } from '@/types/balanceSheet'

type Accent = 'blue' | 'green' | 'amber' | 'slate'

function Card({ label, value, accent, sub }: { label: string; value: ReactNode; accent: Accent; sub?: ReactNode }) {
  return (
    <div className={`fin-metric fin-metric--${accent}`}>
      <div className="fin-metric__label">{label}</div>
      <div className="fin-metric__value">{value}</div>
      {sub && <div className="fin-metric__sub">{sub}</div>}
    </div>
  )
}

export function BalanceSheetMetricCards({ summary }: { summary: BalanceSheetSummary }) {
  const cur = (v: number) => formatStatementCurrency(v, summary.currency)
  const balanced = summary.balance_status === 'balanced'
  return (
    <div className="fin-metric-grid">
      <Card label="Total Assets" accent="blue" value={cur(summary.total_assets)} />
      <Card
        label="Cash & Equivalents"
        accent={summary.cash >= 0 ? 'green' : 'amber'}
        value={cur(summary.cash)}
        sub={summary.cash < 0 ? 'Funding gap — negative cash' : undefined}
      />
      <Card
        label="Net Working Capital"
        accent="slate"
        value={cur(summary.net_working_capital)}
        sub={summary.current_ratio != null ? `Current ratio ${summary.current_ratio.toFixed(2)}` : undefined}
      />
      <Card
        label="Total Borrowings"
        accent="amber"
        value={cur(summary.total_borrowings)}
        sub={summary.debt_to_equity != null ? `D/E ${summary.debt_to_equity.toFixed(2)}` : undefined}
      />
      <Card label="Total Equity" accent={summary.total_equity >= 0 ? 'green' : 'amber'} value={cur(summary.total_equity)} />
      <div className="fin-metric fin-metric--slate">
        <div className="fin-metric__label">Balance Status</div>
        <div className="fin-metric__value" style={{ fontSize: '1.1rem' }}>
          <Badge tone={balanced ? 'green' : 'red'} dot>{balanced ? 'Balanced' : 'Out of balance'}</Badge>
        </div>
        <div className="fin-metric__sub">Assets = Equity + Liabilities</div>
      </div>
    </div>
  )
}
