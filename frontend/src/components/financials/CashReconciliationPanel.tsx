import { SectionCard } from '@/components/SectionCard'
import { Badge } from '@/components/ui/Badge'
import { formatStatementNumber } from '@/utils/statementFormat'
import type { CashFlowPeriod, CashFlowTotals, CashReconciliationResult } from '@/types/cashFlow'

/** Opening + operating + investing + financing = closing, then ties to the Balance Sheet. */
export function CashReconciliationPanel({
  recon,
  totals,
  periods,
  currency,
}: {
  recon: CashReconciliationResult
  totals: CashFlowTotals
  periods: CashFlowPeriod[]
  currency: string
}) {
  const reconciled = recon.status === 'reconciled'
  const rows: { label: string; values: number[]; strong?: boolean }[] = [
    { label: 'Opening cash', values: totals.opening_cash },
    { label: 'Net operating cash flow', values: totals.net_cash_from_operating_activities },
    { label: 'Net investing cash flow', values: totals.net_cash_used_in_investing_activities },
    { label: 'Net financing cash flow', values: totals.net_cash_from_financing_activities },
    { label: 'Closing cash (Cash Flow)', values: recon.closing_cash_cash_flow, strong: true },
    { label: 'Cash per Balance Sheet', values: recon.cash_balance_sheet, strong: true },
    { label: 'Difference', values: recon.difference },
  ]
  return (
    <SectionCard
      title="Cash reconciliation"
      subtitle="Closing cash rolls forward and ties to the Statement of Financial Position."
      icon="⚖"
      actions={<Badge tone={reconciled ? 'green' : 'red'} dot>{reconciled ? 'Reconciled' : `Out by ${formatStatementNumber(recon.max_difference)}`}</Badge>}
    >
      <div className="stmt-wrap">
        <table className="stmt">
          <thead>
            <tr>
              <th className="stmt__label-head">Reconciliation ({currency})</th>
              {periods.map((p) => <th key={p.index} className="stmt__num">{p.label}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr className={`stmt__row${r.strong ? ' stmt__row--subtotal' : ''}${r.label === 'Difference' ? ' stmt__row--balancecheck' : ''}`} key={r.label}>
                <td className="stmt__label">{r.label}</td>
                {r.values.map((v, i) => (
                  <td key={i} className={`stmt__num${v < 0 ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  )
}
