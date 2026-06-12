import type { BalanceSheet, BalanceSheetLineItem } from '@/types/balanceSheet'
import { formatStatementNumber, isNegative } from '@/utils/statementFormat'

export function BalanceSheetTable({
  statement,
  onDrilldown,
}: {
  statement: BalanceSheet
  onDrilldown: (item: BalanceSheetLineItem) => void
}) {
  const periods = statement.periods

  const rowClass = (r: BalanceSheetLineItem): string => {
    if (r.is_balance_check) return 'stmt__row stmt__row--balancecheck'
    if (r.is_grand_total) return 'stmt__row stmt__row--grandtotal'
    if (r.is_subtotal) return 'stmt__row stmt__row--subtotal'
    if (r.is_header) return 'stmt__row stmt__row--section'
    if (r.level === 0) return 'stmt__row stmt__row--group'
    return 'stmt__row'
  }

  return (
    <div className="stmt-wrap">
      <table className="stmt">
        <thead>
          <tr>
            <th className="stmt__label-head">Line item</th>
            {periods.map((p) => (
              <th key={p.index} className="stmt__num">{p.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {statement.rows.map((r) => {
            const hasValues = r.values_by_period.length > 0
            const indent = 14 + (r.is_header || r.level === 0 ? 0 : (r.level - 1) * 16)
            return (
              <tr className={rowClass(r)} key={r.key}>
                <td className="stmt__label" style={{ paddingLeft: indent }}>
                  {r.drilldown_available ? (
                    <button className="stmt__drill" onClick={() => onDrilldown(r)} title="Drill down">
                      {r.label}
                    </button>
                  ) : (
                    <span>{r.label}</span>
                  )}
                  {r.note && <span className="stmt__note">{r.note}</span>}
                </td>
                {hasValues
                  ? r.values_by_period.map((v, i) => (
                      <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>
                        {formatStatementNumber(v)}
                      </td>
                    ))
                  : periods.map((p) => <td key={p.index} className="stmt__num" />)}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
