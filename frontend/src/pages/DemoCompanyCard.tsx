import type { ReactNode } from 'react'
import type { DemoPreview } from '@/api/hooks'
import { Badge } from '@/components/ui/Badge'
import { formatCurrency } from '@/utils/format'

const METRIC_LABELS: { key: string; label: string }[] = [
  { key: 'products', label: 'Products' },
  { key: 'direct_cost_items', label: 'Direct Costs' },
  { key: 'staff_roles', label: 'Staff Roles' },
  { key: 'operating_expenses', label: 'Op. Expenses' },
  { key: 'fixed_assets', label: 'Fixed Assets' },
  { key: 'scenarios', label: 'Scenarios' },
]

export function DemoCompanyCard({
  preview,
  loading,
  onLoad,
  isLoading,
  spinner,
}: {
  preview?: DemoPreview
  loading: boolean
  onLoad: () => void
  isLoading: boolean
  spinner: ReactNode
}) {
  const tags = preview?.tags ?? ['Product Sales', 'Installation', 'Maintenance', 'Subscription', 'UAE VAT', 'Working Capital']
  const title = preview?.name ?? 'AquaPure Smart Filters FZE'
  const subtitle = preview?.subtitle ?? 'Complete 5-year UAE smart water filtration business plan scenario'

  return (
    <section className="demo-card">
      <div className="demo-card__glow" />
      <div className="demo-card__content">
        <div className="demo-card__main">
          <div className="demo-card__eyebrow">
            <span className="demo-card__droplet">💧</span> Demo Company
            {preview?.already_loaded && <Badge tone="green" dot>Loaded</Badge>}
          </div>
          <h2 className="demo-card__title">{title}</h2>
          <p className="demo-card__subtitle">{subtitle}</p>

          <div className="row row--wrap demo-card__tags">
            {tags.map((t) => (
              <span key={t} className="demo-card__tag">{t}</span>
            ))}
          </div>

          {preview && (
            <div className="demo-card__metrics">
              {METRIC_LABELS.map((m) => (
                <div key={m.key} className="demo-card__metric">
                  <strong>{preview.metrics[m.key] ?? 0}</strong>
                  <span>{m.label}</span>
                </div>
              ))}
              <div className="demo-card__metric">
                <strong>{formatCurrency(preview.metrics.total_funding ?? 0, preview.currency)}</strong>
                <span>Total Funding</span>
              </div>
            </div>
          )}
        </div>

        <div className="demo-card__action">
          <div className="demo-card__completion">
            <span>{preview?.completion_percent ?? 100}%</span>
            <small>complete</small>
          </div>
          <button className="btn btn--lg demo-card__btn" onClick={onLoad} disabled={isLoading || loading}>
            {isLoading ? <>{spinner} Loading…</> : preview?.already_loaded ? '↻ Reload Demo Company' : '+ Load Demo Company'}
          </button>
          <span className="demo-card__hint">Populates every page with realistic data</span>
        </div>
      </div>
    </section>
  )
}
