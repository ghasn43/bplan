import { SectionCard } from '@/components/SectionCard'
import { Badge } from '@/components/ui/Badge'
import { formatStatementNumber } from '@/utils/statementFormat'
import type { BalanceCheckResult, BalanceSheetPeriod } from '@/types/balanceSheet'

export function BalanceCheckPanel({
  check,
  periods,
  currency,
}: {
  check: BalanceCheckResult
  periods: BalanceSheetPeriod[]
  currency: string
}) {
  const balanced = check.status === 'balanced'
  return (
    <SectionCard
      title="Balance check"
      subtitle="Total assets − total equity and liabilities (should be zero)."
      icon="⚖"
      actions={<Badge tone={balanced ? 'green' : 'red'} dot>{balanced ? 'Balanced' : `Out by ${formatStatementNumber(check.max_difference)}`}</Badge>}
    >
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Period</th>
              <th style={{ textAlign: 'right' }}>Difference ({currency})</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {periods.map((p, i) => (
              <tr key={p.index}>
                <td>{p.label}</td>
                <td className="table__num">{formatStatementNumber(check.values_by_period[i])}</td>
                <td>
                  <Badge tone={check.is_balanced_by_period[i] ? 'green' : 'red'}>
                    {check.is_balanced_by_period[i] ? 'Balanced' : 'Out of balance'}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  )
}
