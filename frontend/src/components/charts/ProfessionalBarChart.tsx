import {
  Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import type { ChartSeries } from '@/types/financialAnalysis'
import { AXIS, CHART_HEIGHT, GRID_COLOR, axisFormatter, makeTooltip, seriesColor } from './chartUtils'

export function ProfessionalBarChart({
  data, series, currency, unit, stacked = false, horizontal = false,
}: {
  data: Record<string, number | string>[]
  series: ChartSeries[]
  currency: string
  unit: string
  stacked?: boolean
  horizontal?: boolean
}) {
  const singleNeg = series.length === 1
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <BarChart data={data} layout={horizontal ? 'vertical' : 'horizontal'}
                margin={{ top: 8, right: 12, left: horizontal ? 8 : 4, bottom: 0 }}>
        <CartesianGrid stroke={GRID_COLOR} vertical={horizontal} horizontal={!horizontal} />
        {horizontal ? (
          <>
            <XAxis type="number" tick={AXIS} tickLine={false} axisLine={false} tickFormatter={axisFormatter(unit, currency)} />
            <YAxis type="category" dataKey="name" tick={AXIS} tickLine={false} axisLine={false} width={140} />
          </>
        ) : (
          <>
            <XAxis dataKey={data[0]?.name !== undefined ? 'name' : 'period'} tick={AXIS} tickLine={false} axisLine={{ stroke: GRID_COLOR }} />
            <YAxis tick={AXIS} tickLine={false} axisLine={false} width={56} tickFormatter={axisFormatter(unit, currency)} />
          </>
        )}
        <Tooltip content={makeTooltip(series, currency)} cursor={{ fill: 'rgba(148,163,184,0.08)' }} />
        {series.length > 1 && <Legend wrapperStyle={{ fontSize: 12, paddingTop: 6 }} />}
        {series.map((s, i) => (
          <Bar key={s.key} dataKey={s.key} name={s.label} stackId={stacked ? 'a' : undefined}
               fill={seriesColor(s, i)} radius={stacked ? [0, 0, 0, 0] : [3, 3, 0, 0]} maxBarSize={48}>
            {singleNeg && data.map((row, j) => (
              <Cell key={j} fill={Number(row[s.key]) < 0 ? '#dc2626' : seriesColor(s, i)} />
            ))}
          </Bar>
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
