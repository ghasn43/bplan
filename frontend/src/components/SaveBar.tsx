import { useNavigate, useParams } from 'react-router-dom'
import { adjacentPages } from '@/routes/nav'
import { CompletionBadge } from './ui/Progress'
import { Spinner } from './ui/Spinner'

/** Sticky bottom bar with save status, completion, and step navigation. */
export function SaveBar({
  slug,
  onSave,
  saving,
  dirty,
  lastSavedLabel,
  sectionPercent,
  canSave = true,
}: {
  slug: string
  onSave?: () => void
  saving?: boolean
  dirty?: boolean
  lastSavedLabel?: string
  sectionPercent?: number
  canSave?: boolean
}) {
  const navigate = useNavigate()
  const { projectId } = useParams()
  const { prev, next } = adjacentPages(slug)

  const go = (s?: string) => {
    if (s) navigate(`/projects/${projectId}/${s}`)
  }

  return (
    <div className="save-bar">
      <div className="save-bar__status">
        {saving ? (
          <>
            <Spinner /> Saving…
          </>
        ) : dirty ? (
          <span className="badge badge--amber badge--dot">Unsaved changes</span>
        ) : (
          <>
            {sectionPercent !== undefined && <CompletionBadge percent={sectionPercent} />}
            {lastSavedLabel && <span className="muted">Last saved {lastSavedLabel}</span>}
          </>
        )}
      </div>

      <div className="save-bar__actions">
        <button className="btn btn--secondary" disabled={!prev} onClick={() => go(prev?.slug)}>
          ← Previous
        </button>
        {onSave && (
          <button className="btn btn--primary" onClick={onSave} disabled={saving || !canSave}>
            Save
          </button>
        )}
        <button className="btn btn--secondary" disabled={!next} onClick={() => go(next?.slug)}>
          Next →
        </button>
      </div>
    </div>
  )
}
