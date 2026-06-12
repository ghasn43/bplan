import type { FinancialAnalysisChart } from '@/types/financialAnalysis'
import { ChartCard } from './ChartCard'

/** Convenience wrapper around the generic chart card (backend supplies chart-ready data). */
export function CashFlowActivityChart({ chart, currency }: { chart: FinancialAnalysisChart; currency: string }) {
  return <ChartCard chart={chart} currency={currency} />
}
