import type { ReactNode } from 'react'
import { Badge } from '@/components/ui/Badge'
import { formatStatementCurrency } from '@/utils/statementFormat'
import type { CashFlowSummary } from '@/types/cashFlow'

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

export function CashFlowMetricCards({ summary }: { summary: CashFlowSummary }) {
  const cur = (v: number) => formatStatementCurrency(v, summary.currency)
  const reconciled = summary.reconciliation_status === 'reconciled'
  return (
    <div className="fin-metric-grid">
      <Card label="Net Operating Cash Flow" accent={summary.net_operating_cash_flow >= 0 ? 'green' : 'amber'} value={cur(summary.net_operating_cash_flow)} />
      <Card label="Net Investing Cash Flow" accent="slate" value={cur(summary.net_investing_cash_flow)} />
      <Card label="Net Financing Cash Flow" accent="blue" value={cur(summary.net_financing_cash_flow)} />
      <Card label="Net Change in Cash" accent={summary.net_change_in_cash >= 0 ? 'green' : 'amber'} value={cur(summary.net_change_in_cash)} />
      <Card
        label="Closing Cash"
        accent={summary.closing_cash >= 0 ? 'green' : 'amber'}
        value={cur(summary.closing_cash)}
        sub={`Free cash flow ${cur(summary.free_cash_flow)}`}
      />
      <div className="fin-metric fin-metric--slate">
        <div className="fin-metric__label">Reconciliation</div>
        <div className="fin-metric__value" style={{ fontSize: '1.1rem' }}>
          <Badge tone={reconciled ? 'green' : 'red'} dot>{reconciled ? 'Reconciled' : 'Not reconciled'}</Badge>
        </div>
        <div className="fin-metric__sub">Closing cash ties to Balance Sheet</div>
      </div>
    </div>
  )
}
