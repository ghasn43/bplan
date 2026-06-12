import { useState } from 'react'
import { SectionCard } from '@/components/SectionCard'
import { LoadingScreen } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useDepreciationSchedule } from '@/api/fixedAssetsApi'
import { formatStatementNumber } from '@/utils/statementFormat'

export function DepreciationScheduleTable({ projectId }: { projectId: string }) {
  const [view, setView] = useState<'monthly' | 'annual'>('annual')
  const { data, isLoading } = useDepreciationSchedule(projectId, view)

  if (isLoading || !data) return <LoadingScreen label="Building the depreciation schedule…" />

  const { periods, assets, rollforward, totals_by_period, grand_total_depreciation } = data

  const rollRows: { label: string; values: number[] }[] = [
    { label: 'Opening cost', values: rollforward.opening_cost },
    { label: 'Additions', values: rollforward.additions },
    { label: 'Depreciation charge', values: rollforward.depreciation_charge },
    { label: 'Accumulated depreciation', values: rollforward.accumulated_depreciation },
    { label: 'Closing net book value', values: rollforward.closing_net_book_value },
  ]

  return (
    <div className="stack">
      <SectionCard>
        <div className="row row--between row--wrap">
          <div className="field" style={{ minWidth: 0 }}>
            <span className="field__label">View</span>
            <div className="segmented">
              <button className={`segmented__btn${view === 'annual' ? ' segmented__btn--active' : ''}`} onClick={() => setView('annual')}>Annual</button>
              <button className={`segmented__btn${view === 'monthly' ? ' segmented__btn--active' : ''}`} onClick={() => setView('monthly')}>Monthly</button>
            </div>
          </div>
          <div className="muted" style={{ fontSize: 13 }}>
            Total depreciation over the plan: <strong>{formatStatementNumber(grand_total_depreciation)} {data.currency}</strong>
          </div>
        </div>
      </SectionCard>

      {data.warnings.length > 0 && (
        <SectionCard title="Notes" icon="ⓘ">
          <div className="stack--sm">
            {data.warnings.map((w, i) => (
              <div className="banner banner--info" key={i}><span className="banner__icon">ℹ</span><div>{w}</div></div>
            ))}
          </div>
        </SectionCard>
      )}

      <div className="card">
        <div className="card__body">
          {assets.length === 0 ? (
            <EmptyState icon="◱" title="No depreciable assets" description="Add assets in the Asset Register tab to see the depreciation schedule." />
          ) : (
            <div className="pgrid-wrap">
              <table className="pgrid">
                <thead>
                  <tr>
                    <th className="pgrid__label-head">Asset</th>
                    {periods.map((p) => <th key={p.index} className="pgrid__num">{p.label}</th>)}
                    <th className="pgrid__num pgrid__total">Total</th>
                    <th className="pgrid__num pgrid__total">Closing NBV</th>
                  </tr>
                </thead>
                <tbody>
                  {assets.map((a) => (
                    <tr key={a.asset_id}>
                      <td className="pgrid__label">
                        <strong>{a.label}</strong>
                        <span className="pgrid__group">{a.category_label}</span>
                      </td>
                      {a.depreciation_by_period.map((v, i) => (
                        <td key={i} className="pgrid__num">{formatStatementNumber(v)}</td>
                      ))}
                      <td className="pgrid__num pgrid__total">{formatStatementNumber(a.total_depreciation)}</td>
                      <td className="pgrid__num pgrid__total">{formatStatementNumber(a.closing_net_book_value)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="pgrid__totals">
                    <td className="pgrid__label">Total depreciation charge</td>
                    {totals_by_period.map((v, i) => <td key={i} className="pgrid__num">{formatStatementNumber(v)}</td>)}
                    <td className="pgrid__num pgrid__total">{formatStatementNumber(grand_total_depreciation)}</td>
                    <td className="pgrid__num pgrid__total">–</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Asset roll-forward */}
      {assets.length > 0 && (
        <SectionCard title="Fixed-asset roll-forward" subtitle="Opening cost, additions, depreciation, and closing net book value." icon="◳">
          <div className="pgrid-wrap">
            <table className="pgrid">
              <thead>
                <tr>
                  <th className="pgrid__label-head">Line</th>
                  {periods.map((p) => <th key={p.index} className="pgrid__num">{p.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {rollRows.map((r) => (
                  <tr key={r.label} className={r.label.startsWith('Closing') ? 'pgrid__totals' : undefined}>
                    <td className="pgrid__label">{r.label}</td>
                    {r.values.map((v, i) => <td key={i} className="pgrid__num">{formatStatementNumber(v)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SectionCard>
      )}
    </div>
  )
}
