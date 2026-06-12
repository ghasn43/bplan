import { useNavigate, useParams } from 'react-router-dom'
import type { ReactNode } from 'react'
import { SectionCard } from './SectionCard'
import { CompletionBadge } from './ui/Progress'

export interface SummaryRow {
  label: string
  value: ReactNode
}

/** A review card summarising one section, with an Edit link back to its page. */
export function ReviewSection({
  title,
  slug,
  icon,
  percent,
  rows,
  empty,
  children,
}: {
  title: string
  slug: string
  icon?: string
  percent?: number
  rows?: SummaryRow[]
  empty?: string
  children?: ReactNode
}) {
  const navigate = useNavigate()
  const { projectId } = useParams()

  return (
    <SectionCard
      title={title}
      icon={icon}
      actions={
        <>
          {percent !== undefined && <CompletionBadge percent={percent} />}
          <button className="btn btn--ghost btn--sm" onClick={() => navigate(`/projects/${projectId}/${slug}`)}>
            Edit
          </button>
        </>
      }
    >
      {rows && rows.length > 0 ? (
        <div className="review-grid">
          {rows.map((r, i) => (
            <div key={i} className="review-row">
              <span className="review-row__label">{r.label}</span>
              <span className="review-row__value">{r.value}</span>
            </div>
          ))}
        </div>
      ) : children ? (
        children
      ) : (
        <p className="muted" style={{ fontSize: 13 }}>
          {empty ?? 'Nothing entered yet.'}
        </p>
      )}
    </SectionCard>
  )
}
