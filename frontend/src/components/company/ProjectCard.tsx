import { Badge } from '@/components/ui/Badge'
import { ProgressBar } from '@/components/ui/Progress'
import { labelFor, projectionPeriodOptions } from '@/utils/options'
import { formatCurrency, timeAgo } from '@/utils/format'
import type { ProjectSummary } from '@/types'

export function ProjectCard({
  project,
  onOpen,
  onDelete,
}: {
  project: ProjectSummary
  onOpen: () => void
  onDelete: () => void
}) {
  const title = project.project_name || project.name
  const metrics: { label: string; value: number }[] = [
    { label: 'Products', value: project.products_count ?? 0 },
    { label: 'Direct Costs', value: project.direct_costs_count ?? 0 },
    { label: 'Staff Roles', value: project.staff_roles_count ?? 0 },
    { label: 'Op. Expenses', value: project.operating_expenses_count ?? 0 },
    { label: 'Fixed Assets', value: project.fixed_assets_count ?? 0 },
    { label: 'Scenarios', value: project.scenarios_count ?? 0 },
  ]

  return (
    <div className="project-card" role="button" tabIndex={0} onClick={onOpen}>
      <div className="row row--between" style={{ alignItems: 'flex-start' }}>
        <div style={{ minWidth: 0 }}>
          <div className="project-card__name" title={title}>{title}</div>
          <div className="muted" style={{ fontSize: 12 }}>
            {project.projection_period ? `${labelFor(projectionPeriodOptions, project.projection_period)} Business Plan` : 'Business plan'}
          </div>
        </div>
        <button className="icon-btn icon-btn--danger" title="Delete project"
          onClick={(e) => { e.stopPropagation(); onDelete() }}>🗑</button>
      </div>

      <div className="row row--wrap" style={{ gap: 6, margin: '10px 0' }}>
        {project.currency && <Badge tone="blue">{project.currency}</Badge>}
        <Badge tone="neutral">{project.completion_percent}% complete</Badge>
      </div>

      <div className="project-card__metrics">
        {metrics.map((m) => (
          <div key={m.label} className="project-card__metric">
            <strong>{m.value}</strong>
            <span>{m.label}</span>
          </div>
        ))}
      </div>

      {(project.total_funding ?? 0) > 0 && (
        <div className="project-card__funding">
          <strong>{formatCurrency(project.total_funding ?? 0, project.currency ?? 'USD')}</strong>
          <span>Total Funding</span>
        </div>
      )}

      <div className="project-card__progress">
        <div className="row row--between" style={{ marginBottom: 6 }}>
          <span className="muted" style={{ fontSize: 12 }}>Project completion</span>
          <strong style={{ fontSize: 13 }}>{project.completion_percent}%</strong>
        </div>
        <ProgressBar percent={project.completion_percent} />
      </div>

      <div className="row row--between" style={{ marginTop: 14, alignItems: 'center' }}>
        <span className="muted" style={{ fontSize: 11.5 }}>Updated {timeAgo(project.updated_at)}</span>
        <button className="btn btn--primary btn--sm" onClick={(e) => { e.stopPropagation(); onOpen() }}>
          Open Project →
        </button>
      </div>
    </div>
  )
}
