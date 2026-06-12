import type { ChartSeries } from '@/types/financialAnalysis'
import { ProfessionalBarChart } from './ProfessionalBarChart'

/** Thin convenience wrapper: a stacked variant of the professional bar chart. */
export function ProfessionalStackedBarChart(props: {
  data: Record<string, number | string>[]
  series: ChartSeries[]
  currency: string
  unit: string
}) {
  return <ProfessionalBarChart {...props} stacked />
}
