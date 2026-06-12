import { SectionCard } from '@/components/SectionCard'

export function FinancialInsightsPanel({ insights }: { insights: string[] }) {
  const items = insights.length ? insights : ['Insufficient data to generate insights.']
  return (
    <SectionCard title="Automated insights" subtitle="Generated from the projected financial statements." icon="✦">
      <div className="insight-grid">
        {items.map((text, i) => (
          <div className="insight-card" key={i}>
            <span className="insight-card__icon">▸</span>
            <span>{text}</span>
          </div>
        ))}
      </div>
    </SectionCard>
  )
}
