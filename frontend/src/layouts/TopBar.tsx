import { useLocation, useNavigate } from 'react-router-dom'
import { CompletionRing } from '@/components/ui/Progress'
import { pageBySlug } from '@/routes/nav'
import { useProjectContext } from './ProjectContext'

function PencilIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
    </svg>
  )
}

export function TopBar() {
  const { projectId, project, completion } = useProjectContext()
  const navigate = useNavigate()
  const location = useLocation()
  const slug = location.pathname.split('/').pop() ?? ''
  const page = pageBySlug(slug)

  // The title is the saved company name (setup.business_name). It is never taken
  // from project_name; project.name is only a last-resort label for brand-new
  // projects that have no setup yet.
  const companyName = project?.setup?.business_name || project?.name || 'Untitled Company'
  const projectName = project?.setup?.project_name ?? ''
  const percent = completion?.completion_percent ?? 0

  return (
    <header className="topbar">
      <div className="topbar__left">
        <div className="topbar__eyebrow">{page?.group ?? 'Business Plan'}</div>
        <div className="topbar__title-row">
          <button
            type="button"
            className="topbar__title-link"
            onClick={() => navigate(`/projects/${projectId}/setup?focus=company_name`)}
            title="Edit company name"
          >
            {companyName}
          </button>
          <button
            type="button"
            className="topbar__edit"
            title="Edit company name"
            aria-label="Edit company name"
            onClick={() => navigate(`/projects/${projectId}/setup?focus=company_name`)}
          >
            <PencilIcon />
          </button>
        </div>
        {projectName && <div className="topbar__project">{projectName}</div>}
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
