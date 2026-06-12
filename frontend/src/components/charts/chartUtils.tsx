import type { ChartSeries } from '@/types/financialAnalysis'
import { formatByKind, formatCompactCurrency, formatStatementPercent } from '@/utils/statementFormat'

export const CHART_HEIGHT = 280

export const PALETTE = ['#2563eb', '#059669', '#d97706', '#64748b', '#4f46e5', '#0d9488', '#94a3b8', '#0891b2', '#7c3aed', '#b45309']

export const AXIS = { fontSize: 11, fill: '#94a3b8' }
export const GRID_COLOR = '#eef2f7'

/** Y-axis tick formatter based on the chart unit. */
export function axisFormatter(unit: string, _currency?: string) {
  return (v: number) => {
    if (unit === 'percent') return `${Math.round(v)}%`
    if (unit === 'ratio') return `${v.toFixed(1)}x`
    if (unit === 'number') return Intl.NumberFormat('en-US', { notation: 'compact' }).format(v)
    return formatCompactCurrency(v, '').trim().replace(/[()]/g, (m) => (m === '(' ? '-' : ''))
  }
}

export function seriesColor(s: ChartSeries, i: number): string {
  return s.color || PALETTE[i % PALETTE.length]
}

/** Professional tooltip that formats each series value by its declared format. */
export function makeTooltip(series: ChartSeries[], currency: string) {
  const byKey = new Map(series.map((s) => [s.key, s]))
  return function ChartTooltip({ active, payload, label }: any) {
    if (!active || !payload || payload.length === 0) return null
    return (
      <div className="chart-tooltip">
        <div className="chart-tooltip__label">{label}</div>
        {payload.map((p: any) => {
          const s = byKey.get(p.dataKey)
          const fmt = s?.format ?? 'currency'
          return (
            <div className="chart-tooltip__row" key={p.dataKey}>
              <span className="chart-tooltip__dot" style={{ background: p.color }} />
              <span className="chart-tooltip__name">{s?.label ?? p.name}</span>
              <span className="chart-tooltip__val">{formatByKind(p.value, fmt, currency)}</span>
            </div>
          )
        })}
      </div>
    )
  }
}

export function pctTooltip(currency: string) {
  return function PieTooltip({ active, payload }: any) {
    if (!active || !payload || !payload.length) return null
    const p = payload[0]
    return (
      <div className="chart-tooltip">
        <div className="chart-tooltip__row">
          <span className="chart-tooltip__dot" style={{ background: p.payload.fill }} />
          <span className="chart-tooltip__name">{p.name}</span>
          <span className="chart-tooltip__val">{formatCompactCurrency(p.value, currency)}</span>
        </div>
      </div>
    )
  }
}

export { formatStatementPercent }
