import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { CHART_HEIGHT, PALETTE, pctTooltip } from './chartUtils'

export function ProfessionalPieChart({
  data, currency, donut = true,
}: {
  data: Record<string, number | string>[]
  currency: string
  donut?: boolean
}) {
  const items = data.map((d) => ({ name: String(d.name), value: Number(d.value) }))
  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <PieChart>
        <Pie data={items} dataKey="value" nameKey="name" cx="50%" cy="50%"
             innerRadius={donut ? 58 : 0} outerRadius={92} paddingAngle={1.5} stroke="#fff" strokeWidth={2}>
          {items.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
        </Pie>
        <Tooltip content={pctTooltip(currency)} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
