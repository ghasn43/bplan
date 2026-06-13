import { Badge } from '@/components/ui/Badge'
import type { CompanySummary } from '@/types/company'

function PencilIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
    </svg>
  )
}

export function CompanyProfileCard({
  company,
  onEdit,
  onReloadDemo,
  reloadDisabled,
}: {
  company: CompanySummary
  onEdit: () => void
  onReloadDemo?: () => void
  reloadDisabled?: boolean
}) {
  const location = [company.city, company.country].filter(Boolean).join(', ')
  const isDemo = company.status === 'demo'

  return (
    <section className="demo-card">
      <div className="demo-card__glow" />
      <div className="demo-card__content">
        <div className="demo-card__main">
          <div className="demo-card__eyebrow">
            <span className="demo-card__droplet">🏢</span>
            {isDemo ? 'Demo Company' : 'Company'}
            {isDemo && <Badge tone="green" dot>Loaded</Badge>}
          </div>

          <div className="company-card__title-row">
            <h2 className="demo-card__title">{company.company_name}</h2>
            <button type="button" className="company-card__edit" onClick={onEdit}
              title="Edit company name" aria-label="Edit company name">
              <PencilIcon />
            </button>
          </div>

          {(company.industry_sector || location) && (
            <p className="company-card__meta">
              {company.industry_sector}
              {company.industry_sector && location ? <br /> : null}
              {location}
            </p>
          )}
          {company.business_description && (
            <p className="demo-card__subtitle">{company.business_description}</p>
          )}

          <div className="row" style={{ gap: 10, marginTop: 16 }}>
            <button className="btn btn--lg demo-card__btn" onClick={onEdit}>✎ Edit Company Profile</button>
            {isDemo && onReloadDemo && (
              <button className="btn btn--lg btn--ghost-light" onClick={onReloadDemo} disabled={reloadDisabled}>
                ↻ Reload Demo Company
              </button>
            )}
          </div>
        </div>

        <div className="demo-card__action">
          <div className="company-card__stats">
            <div className="company-card__stat">
              <strong>{company.total_projects}</strong>
              <span>Projects</span>
            </div>
            <div className="company-card__stat">
              <strong>{company.active_projects}</strong>
              <span>Active</span>
            </div>
            <div className="company-card__stat">
              <strong>{company.draft_projects}</strong>
              <span>Draft</span>
            </div>
          </div>
          <div className="demo-card__completion" style={{ marginTop: 12 }}>
            <span>{company.profile_completion_percent}%</span>
            <small>profile</small>
          </div>
        </div>
      </div>
    </section>
  )
}
