import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { useCashBridge } from '@/api/balanceSheetApi'
import { formatStatementNumber, isNegative } from '@/utils/statementFormat'
import type { ScenarioKey } from '@/types/balanceSheet'

/** Cash drill-down = the internal cash bridge (precursor to the Cash Flow Statement). */
export function BalanceSheetDrilldown({
  projectId,
  scenario,
  lineKey,
  lineLabel,
  onClose,
}: {
  projectId: string
  scenario: ScenarioKey
  lineKey: string | null
  lineLabel: string
  onClose: () => void
}) {
  const isCash = lineKey === 'cash'
  const { data, isLoading } = useCashBridge(projectId, scenario, isCash && !!lineKey)

  if (!lineKey) return null

  return (
    <Modal open title={`Drill-down — ${lineLabel}`} onClose={onClose} wide>
      {!isCash ? (
        <p className="muted">
          Detailed drill-down for this line is available in its source schedule (asset register, projection grids,
          working capital, or financing). The cash line provides a full cash bridge here.
        </p>
      ) : isLoading || !data ? (
        <div className="row" style={{ gap: 10 }}><Spinner /> Building cash bridge…</div>
      ) : (
        <div className="stmt-wrap">
          <table className="stmt">
            <thead>
              <tr>
                <th className="stmt__label-head">Cash movement ({data.currency})</th>
                {data.periods.map((p, i) => <th key={i} className="stmt__num">{p}</th>)}
              </tr>
            </thead>
            <tbody>
              <tr className="stmt__row stmt__row--subtotal">
                <td className="stmt__label">Opening cash</td>
                {data.opening_cash.map((v, i) => (
                  <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
                ))}
              </tr>
              {data.lines.map((l) => (
                <tr className="stmt__row" key={l.key}>
                  <td className="stmt__label" style={{ paddingLeft: 26 }}>{l.label}</td>
                  {l.values.map((v, i) => (
                    <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
                  ))}
                </tr>
              ))}
              <tr className="stmt__row stmt__row--grandtotal">
                <td className="stmt__label">Closing cash</td>
                {data.closing_cash.map((v, i) => (
                  <td key={i} className={`stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`}>{formatStatementNumber(v)}</td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </Modal>
  )
}
