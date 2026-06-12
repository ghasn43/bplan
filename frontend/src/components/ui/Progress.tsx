export function ProgressBar({ percent }: { percent: number }) {
  const clamped = Math.max(0, Math.min(100, percent))
  return (
    <div className="progress" role="progressbar" aria-valuenow={clamped} aria-valuemin={0} aria-valuemax={100}>
      <div
        className={`progress__bar${clamped >= 100 ? ' progress__bar--complete' : ''}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}

/** Circular completion indicator used in the top bar. */
export function CompletionRing({ percent, size = 40 }: { percent: number; size?: number }) {
  const clamped = Math.max(0, Math.min(100, percent))
  const stroke = 4
  const r = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  const offset = circ - (clamped / 100) * circ
  const complete = clamped >= 100
  const color = complete ? 'var(--emerald-500)' : 'var(--blue-600)'
  return (
    <svg width={size} height={size} className="progress-ring">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--slate-200)" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.5s ease' }}
      />
    </svg>
  )
}

/** Completion badge: a coloured pill showing N% or a check. */
export function CompletionBadge({ percent }: { percent: number }) {
  if (percent >= 100) {
    return <span className="badge badge--green badge--dot">Complete</span>
  }
  if (percent === 0) {
    return <span className="badge badge--neutral badge--dot">Not started</span>
  }
  return <span className="badge badge--amber badge--dot">{percent}% complete</span>
}
