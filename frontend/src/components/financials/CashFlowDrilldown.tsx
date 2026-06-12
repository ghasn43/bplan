import { Modal } from '@/components/ui/Modal'
import type { CashFlowLineItem, CashFlowPeriod } from '@/types/cashFlow'
import { formatStatementNumber, isNegative } from '@/utils/statementFormat'

export function CashFlowDrilldown({
  item,
  periods,
  currency,
  onClose,
}: {
  item: CashFlowLineItem | null
  periods: CashFlowPeriod[]
  currency: string
  onClose: () => void
}) {
  if (!item) return null
  return (
    <Modal open title={`Drill-down — ${item.label}`} onClose={onClose} wide>
      <p className="muted" style={{ fontSize: 13, marginBottom: 12 }}>
        Movement by period ({currency}). Detailed source breakdowns are available in the income statement,
        asset register, projection grids and financing assumptions.
      </p>
      <div className="stmt-wrap">
        <table className="stmt">
          <thead>
            <tr>
              <th className="stmt__label-head">Period</th>
              {periods.map((p) => <th key={p.index} className="stmt__num">{p.label}</th>)}
            </tr>
          </thead>
          <tbody>
            <tr className="stmt__row stmt__row--subtotal">
              <td className="stmt__label">{item.label}</td>
              {item.values_by_period.map((v, i) => (
                <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
              ))}
            </tr>
            {item.children.map((c) => (
              <tr className="stmt__row" key={c.key}>
                <td className="stmt__label" style={{ paddingLeft: 26 }}>{c.label}</td>
                {c.values_by_period.map((v, i) => (
                  <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Modal>
  )
}
