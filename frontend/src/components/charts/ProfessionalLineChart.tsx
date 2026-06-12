import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import type { ChartSeries } from '@/types/financialAnalysis'
import { AXIS, CHART_HEIGHT, GRID_COLOR, axisFormatter, makeTooltip, seriesColor } from './chartUtils'

export function ProfessionalLineChart({
  data, series, currency, unit,
}: {
  data: Record<string, number | string>[]
  series: ChartSeries[]
  currency: string
  unit: string
}) {
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart data={data} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
        <CartesianGrid stroke={GRID_COLOR} vertical={false} />
        <XAxis dataKey="period" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID_COLOR }} />
        <YAxis tick={AXIS} tickLine={false} axisLine={false} width={56} tickFormatter={axisFormatter(unit, currency)} />
        <Tooltip content={makeTooltip(series, currency)} />
        <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, paddingTop: 6 }} />
        {series.map((s, i) => (
          <Line key={s.key} type="monotone" dataKey={s.key} name={s.label} stroke={seriesColor(s, i)}
                strokeWidth={2.2} dot={false} activeDot={{ r: 4 }} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
