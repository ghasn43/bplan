import type { CashFlowLineItem, CashFlowStatement } from '@/types/cashFlow'
import { formatStatementNumber, isNegative } from '@/utils/statementFormat'

export function CashFlowTable({
  statement,
  onDrilldown,
}: {
  statement: CashFlowStatement
  onDrilldown: (item: CashFlowLineItem) => void
}) {
  const periods = statement.periods

  const rowClass = (r: CashFlowLineItem): string => {
    if (r.key === 'cash_recon') return 'stmt__row stmt__row--balancecheck'
    if (r.is_grand_total) return 'stmt__row stmt__row--grandtotal'
    if (r.is_subtotal) return 'stmt__row stmt__row--subtotal'
    if (r.is_section_header) return 'stmt__row stmt__row--section'
    if (r.level === 0) return 'stmt__row stmt__row--group'
    return 'stmt__row'
  }

  return (
    <div className="stmt-wrap">
      <table className="stmt">
        <thead>
          <tr>
            <th className="stmt__label-head">Line item</th>
            {periods.map((p) => <th key={p.index} className="stmt__num">{p.label}</th>)}
            {periods.length > 1 && <th className="stmt__num stmt__total">Total</th>}
          </tr>
        </thead>
        <tbody>
          {statement.rows.map((r) => {
            const hasValues = r.values_by_period.length > 0
            const indent = 14 + (r.is_section_header || r.level === 0 ? 0 : (r.level - 1) * 16)
            const showTotal = periods.length > 1 && hasValues && !r.is_section_header &&
              r.key !== 'opening_cash' && r.key !== 'closing_cash' && r.key !== 'cash_recon'
            return (
              <tr className={rowClass(r)} key={r.key}>
                <td className="stmt__label" style={{ paddingLeft: indent }}>
                  {r.drilldown_available ? (
                    <button className="stmt__drill" onClick={() => onDrilldown(r)} title="Drill down">{r.label}</button>
                  ) : (
                    <span>{r.label}</span>
                  )}
                  {r.note && <span className="stmt__note">{r.note}</span>}
                </td>
                {hasValues
                  ? r.values_by_period.map((v, i) => (
                      <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
                    ))
                  : periods.map((p) => <td key={p.index} className="stmt__num" />)}
                {periods.length > 1 && (
                  <td className={`stmt__num stmt__total${isNegative(r.total) ? ' stmt__num--neg' : ''}`}>
                    {showTotal ? formatStatementNumber(r.total) : ''}
                  </td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
