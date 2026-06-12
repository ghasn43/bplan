import { Outlet, useNavigate, useParams } from 'react-router-dom'
import { LoadingScreen } from '@/components/ui/Spinner'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { ProjectProvider, useProjectContext } from './ProjectContext'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

function ProjectError({ message }: { message: string }) {
  const navigate = useNavigate()
  return (
    <div className="center-screen">
      <div className="card" style={{ maxWidth: 560, padding: 8 }}>
        <div className="card__body stack--sm">
          <div className="banner banner--warning">
            <span className="banner__icon">⚠</span>
            <div>
              <strong>This business plan could not be loaded.</strong>
              <div style={{ marginTop: 6, fontSize: 13 }}>{message}</div>
            </div>
          </div>
          <p className="muted" style={{ fontSize: 13 }}>
            This usually means the project was saved by an older version of the app. Delete it and
            create a new one, or reset the backend <code>data/</code> folder.
          </p>
          <div>
            <button className="btn btn--primary" onClick={() => navigate('/projects')}>
              ← Back to Projects
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function Shell() {
  const { isLoading, isError, error, project } = useProjectContext()
  if (isLoading) return <LoadingScreen label="Loading business plan…" />
  if (isError || !project)
    return <ProjectError message={error?.message ?? 'The project may not exist or the backend is unreachable.'} />

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <TopBar />
        <main className="app-content">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  )
}

export function AppLayout() {
  const { projectId } = useParams()
  if (!projectId) return <LoadingScreen />
  return (
    <ProjectProvider projectId={projectId}>
      <Shell />
    </ProjectProvider>
  )
}
