import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { AXIS, CHART_HEIGHT, GRID_COLOR, axisFormatter } from './chartUtils'
import { formatCompactCurrency } from '@/utils/statementFormat'

const TOTAL_POS = '#334155'
const TOTAL_NEG = '#dc2626'
const POS = '#059669'
const NEG = '#d97706'

export function ProfessionalWaterfallChart({
  data, currency,
}: {
  data: Record<string, number | string>[]
  currency: string
}) {
  let running = 0
  const rows = data.map((it) => {
    const value = Number(it.value)
    const kind = String(it.kind)
    let base: number, seg: number, color: string
    if (kind === 'total' || kind === 'subtotal') {
      base = Math.min(0, value)
      seg = Math.abs(value)
      color = value >= 0 ? TOTAL_POS : TOTAL_NEG
      running = value
    } else {
      const start = running
      const end = running + value
      base = Math.min(start, end)
      seg = Math.abs(value)
      color = value >= 0 ? POS : NEG
      running = end
    }
    return { name: String(it.name), base, seg, color, value }
  })

  const tooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null
    const row = payload[0].payload
    return (
      <div className="chart-tooltip">
        <div className="chart-tooltip__label">{row.name}</div>
        <div className="chart-tooltip__row">
          <span className="chart-tooltip__val">{formatCompactCurrency(row.value, currency)}</span>
        </div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart data={rows} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
        <CartesianGrid stroke={GRID_COLOR} vertical={false} />
        <XAxis dataKey="name" tick={{ ...AXIS, fontSize: 10 }} tickLine={false} axisLine={{ stroke: GRID_COLOR }} interval={0} angle={-12} textAnchor="end" height={48} />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={56} tickFormatter={axisFormatter('currency', currency)} />
        <Tooltip content={tooltip} cursor={{ fill: 'rgba(148,163,184,0.08)' }} />
        <Bar dataKey="base" stackId="w" fill="transparent" />
        <Bar dataKey="seg" stackId="w" radius={[3, 3, 0, 0]} maxBarSize={54}>
          {rows.map((r, i) => <Cell key={i} fill={r.color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
