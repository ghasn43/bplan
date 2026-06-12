import { useLocation } from 'react-router-dom'
import { CompletionRing } from '@/components/ui/Progress'
import { pageBySlug } from '@/routes/nav'
import { useProjectContext } from './ProjectContext'

export function TopBar() {
  const { project, completion } = useProjectContext()
  const location = useLocation()
  const slug = location.pathname.split('/').pop() ?? ''
  const page = pageBySlug(slug)

  const businessName = project?.setup?.business_name ?? project?.name ?? 'Untitled Plan'
  const percent = completion?.completion_percent ?? 0

  return (
    <header className="topbar">
      <div className="topbar__left">
        <div className="topbar__eyebrow">{page?.group ?? 'Business Plan'}</div>
        <div className="topbar__title">{businessName}</div>
      </div>

      <div className="topbar__right">
        <div className="topbar__completion">
          <div className="topbar__completion-label">
            <small>Plan Completion</small>
            <strong>{percent}%</strong>
          </div>
          <div style={{ position: 'relative', width: 40, height: 40 }}>
            <CompletionRing percent={percent} />
          </div>
        </div>
      </div>
    </header>
  )
}
