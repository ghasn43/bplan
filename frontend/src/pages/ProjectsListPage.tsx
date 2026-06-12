import { useNavigate } from 'react-router-dom'
import { useDeleteProject, useDemoPreview, useLoadDemo, useProjects } from '@/api/hooks'
import { LoadingScreen, Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { ProgressBar } from '@/components/ui/Progress'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/components/ui/Toast'
import { labelFor, projectionPeriodOptions } from '@/utils/options'
import { timeAgo } from '@/utils/format'
import { DemoCompanyCard } from './DemoCompanyCard'

export function ProjectsListPage() {
  const navigate = useNavigate()
  const { data: projects, isLoading } = useProjects()
  const demoPreview = useDemoPreview()
  const loadDemo = useLoadDemo()
  const del = useDeleteProject()
  const { notify } = useToast()

  const handleLoadDemo = () => {
    loadDemo.mutate(undefined, {
      onSuccess: (project) => {
        notify('AquaPure demo company loaded')
        navigate(`/projects/${project.id}/setup`)
      },
      onError: (e) => notify((e as Error).message || 'Failed to load demo', 'error'),
    })
  }

  if (isLoading) return <LoadingScreen label="Loading projects…" />

  const list = projects ?? []

  return (
    <div className="landing">
      <header className="landing__header">
        <div className="landing__brand">
          <div className="sidebar__logo">B</div>
          <div>
            <div className="landing__title">Business Plan Studio</div>
            <div className="muted" style={{ fontSize: 13 }}>Investor-grade financial projection workspace</div>
          </div>
        </div>
        <button className="btn btn--primary btn--lg" onClick={() => navigate('/projects/new')}>
          + New Business Plan
        </button>
      </header>

      <div className="landing__body">
        <DemoCompanyCard
          preview={demoPreview.data}
          loading={demoPreview.isLoading}
          onLoad={handleLoadDemo}
          isLoading={loadDemo.isPending}
          spinner={<Spinner />}
        />

        <div className="row row--between" style={{ margin: '32px 0 18px' }}>
          <h2 style={{ fontSize: 18 }}>Your Plans</h2>
          <span className="muted">{list.length} plan{list.length === 1 ? '' : 's'}</span>
        </div>

        {list.length === 0 ? (
          <div className="card">
            <EmptyState
              icon="◫"
              title="No business plans yet"
              description="Create your first plan to start capturing the assumptions behind your financial projections."
              action={
                <button className="btn btn--primary" onClick={() => navigate('/projects/new')}>
                  + New Business Plan
                </button>
              }
            />
          </div>
        ) : (
          <div className="project-grid">
            {list.map((p) => (
              <div
                key={p.id}
                className="project-card"
                onClick={() => navigate(`/projects/${p.id}/setup`)}
                role="button"
                tabIndex={0}
              >
                <div className="row row--between" style={{ alignItems: 'flex-start' }}>
                  <div>
                    <div className="project-card__name">{p.business_name || p.name}</div>
                    <div className="muted" style={{ fontSize: 12.5 }}>{p.name}</div>
                  </div>
                  <button
                    className="icon-btn icon-btn--danger"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (!window.confirm(`Delete “${p.name}”? This cannot be undone.`)) return
                      del.mutate(p.id, { onSuccess: () => notify('Project deleted') })
                    }}
                    title="Delete"
                  >
                    🗑
                  </button>
                </div>

                <div className="row row--wrap" style={{ gap: 6, margin: '14px 0' }}>
                  {p.currency && <Badge tone="blue">{p.currency}</Badge>}
                  {p.projection_period && (
                    <Badge tone="neutral">{labelFor(projectionPeriodOptions, p.projection_period)}</Badge>
                  )}
                </div>

                <div className="project-card__progress">
                  <div className="row row--between" style={{ marginBottom: 6 }}>
                    <span className="muted" style={{ fontSize: 12 }}>Completion</span>
                    <strong style={{ fontSize: 13 }}>{p.completion_percent}%</strong>
                  </div>
                  <ProgressBar percent={p.completion_percent} />
                </div>

                <div className="muted" style={{ fontSize: 11.5, marginTop: 14 }}>
                  Updated {timeAgo(p.updated_at)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
