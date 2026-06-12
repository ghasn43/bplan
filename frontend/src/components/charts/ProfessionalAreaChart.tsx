import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import type { ChartSeries } from '@/types/financialAnalysis'
import { AXIS, CHART_HEIGHT, GRID_COLOR, axisFormatter, makeTooltip, seriesColor } from './chartUtils'

export function ProfessionalAreaChart({
  data, series, currency, unit,
}: {
  data: Record<string, number | string>[]
  series: ChartSeries[]
  currency: string
  unit: string
}) {
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <AreaChart data={data} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
        <defs>
          {series.map((s, i) => (
            <linearGradient key={s.key} id={`grad-${s.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={seriesColor(s, i)} stopOpacity={0.28} />
              <stop offset="95%" stopColor={seriesColor(s, i)} stopOpacity={0.02} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid stroke={GRID_COLOR} vertical={false} />
        <XAxis dataKey="period" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID_COLOR }} />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={56} tickFormatter={axisFormatter(unit, currency)} />
        <Tooltip content={makeTooltip(series, currency)} />
        {series.map((s, i) => (
          <Area key={s.key} type="monotone" dataKey={s.key} name={s.label} stroke={seriesColor(s, i)}
                strokeWidth={2.2} fill={`url(#grad-${s.key})`} />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  )
}
