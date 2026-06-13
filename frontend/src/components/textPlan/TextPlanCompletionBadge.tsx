import type { TextPlanCompletion } from '@/types/textPlan'

export function TextPlanCompletionBadge({ completion }: { completion?: TextPlanCompletion }) {
  const pct = completion?.completion_percent ?? 0
  const color = pct >= 80 ? '#059669' : pct >= 40 ? '#2563eb' : '#d97706'
  return (
    <div className="tb-completion">
      <div className="row" style={{ justifyContent: 'space-between', alignItems: 'baseline' }}>
        <span style={{ fontSize: 12, color: 'var(--slate-500, #64748b)' }}>Written plan</span>
        <span style={{ fontSize: 13, fontWeight: 700, color }}>{pct}%</span>
      </div>
      <div className="tb-progress">
        <div className="tb-progress__bar" style={{ width: `${pct}%`, background: color }} />
      </div>
      {completion && (
        <div style={{ fontSize: 11, color: 'var(--slate-500, #64748b)', marginTop: 4 }}>
          {completion.completed_topics}/{completion.topic_count} topics done · {completion.word_count.toLocaleString()} words
        </div>
      )}
    </div>
  )
}
