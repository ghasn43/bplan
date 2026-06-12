import type { FinancialAnalysisChart } from '@/types/financialAnalysis'
import { ChartRenderer } from '@/components/charts/ChartRenderer'

export function ChartCard({ chart, currency }: { chart: FinancialAnalysisChart; currency: string }) {
  return (
    <section className="chart-card">
      <header className="chart-card__head">
        <div>
          <h3 className="chart-card__title">{chart.title}</h3>
          {chart.description && <p className="chart-card__desc">{chart.description}</p>}
        </div>
      </header>
      <div className="chart-card__body">
        <ChartRenderer chart={chart} currency={currency} />
      </div>
      {chart.insight && <div className="chart-card__insight">{chart.insight}</div>}
      <footer className="chart-card__footer">Source: {chart.source_statement}</footer>
    </section>
  )
}
