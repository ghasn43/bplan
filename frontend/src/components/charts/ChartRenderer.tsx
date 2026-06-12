import {
  Bar, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import type { FinancialAnalysisChart } from '@/types/financialAnalysis'
import { AXIS, CHART_HEIGHT, GRID_COLOR, axisFormatter, makeTooltip, seriesColor } from './chartUtils'
import { ProfessionalLineChart } from './ProfessionalLineChart'
import { ProfessionalAreaChart } from './ProfessionalAreaChart'
import { ProfessionalBarChart } from './ProfessionalBarChart'
import { ProfessionalStackedBarChart } from './ProfessionalStackedBarChart'
import { ProfessionalPieChart } from './ProfessionalPieChart'
import { ProfessionalWaterfallChart } from './ProfessionalWaterfallChart'

function ComboChart({ chart, currency }: { chart: FinancialAnalysisChart; currency: string }) {
  const hasRight = chart.series.some((s) => s.axis === 'right')
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <ComposedChart data={chart.data} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
        <CartesianGrid stroke={GRID_COLOR} vertical={false} />
        <XAxis dataKey="period" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID_COLOR }} />
        <YAxis yAxisId="left" tick={AXIS} tickLine={false} axisLine={false} width={56} tickFormatter={axisFormatter('currency', currency)} />
        {hasRight && <YAxis yAxisId="right" orientation="right" tick={AXIS} tickLine={false} axisLine={false} width={44} tickFormatter={axisFormatter('percent', currency)} />}
        <Tooltip content={makeTooltip(chart.series, currency)} cursor={{ fill: 'rgba(148,163,184,0.08)' }} />
        <Legend wrapperStyle={{ fontSize: 12, paddingTop: 6 }} />
        {chart.series.map((s, i) =>
          s.type === 'line' ? (
            <Line key={s.key} yAxisId={s.axis === 'right' ? 'right' : 'left'} type="monotone" dataKey={s.key}
                  name={s.label} stroke={seriesColor(s, i)} strokeWidth={2.2} dot={false} />
          ) : (
            <Bar key={s.key} yAxisId="left" dataKey={s.key} name={s.label} stackId="bars"
                 fill={seriesColor(s, i)} maxBarSize={48} />
          ),
        )}
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function ChartRenderer({ chart, currency }: { chart: FinancialAnalysisChart; currency: string }) {
  const empty = chart.data.length === 0 || chart.series.length === 0 && chart.chart_type !== 'waterfall' && chart.chart_type !== 'donut' && chart.chart_type !== 'pie'
  if (empty && chart.data.length === 0) {
    return <div className="chart-empty">No data available for this chart.</div>
  }
  const { chart_type, data, series, unit } = chart
  switch (chart_type) {
    case 'line':
      return <ProfessionalLineChart data={data} series={series} currency={currency} unit={unit} />
    case 'area':
      return <ProfessionalAreaChart data={data} series={series} currency={currency} unit={unit} />
    case 'stacked_bar':
      return <ProfessionalStackedBarChart data={data} series={series} currency={currency} unit={unit} />
    case 'grouped_bar':
      return <ProfessionalBarChart data={data} series={series} currency={currency} unit={unit} />
    case 'bar': {
      const horizontal = data[0]?.name !== undefined && data[0]?.period === undefined
      return <ProfessionalBarChart data={data} series={series} currency={currency} unit={unit} horizontal={horizontal} />
    }
    case 'donut':
      return <ProfessionalPieChart data={data} currency={currency} donut />
    case 'pie':
      return <ProfessionalPieChart data={data} currency={currency} donut={false} />
    case 'waterfall':
      return <ProfessionalWaterfallChart data={data} currency={currency} />
    case 'combo':
      return <ComboChart chart={chart} currency={currency} />
    default:
      return <div className="chart-empty">Unsupported chart type.</div>
  }
}
