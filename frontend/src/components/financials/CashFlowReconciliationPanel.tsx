import { SectionCard } from '@/components/SectionCard'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import type { CashFlowReconciliation } from '@/types/cashFlow'

export function CashFlowReconciliationPanel({
  data,
  loading,
}: {
  data?: CashFlowReconciliation
  loading: boolean
}) {
  return (
    <SectionCard
      title="Reconciliation & controls"
      subtitle="Big 4-style checks tying the cash flow to the income statement, balance sheet and schedules."
      icon="✓"
      actions={data ? <Badge tone={data.all_passed ? 'green' : 'amber'} dot>{data.all_passed ? 'All checks passed' : 'Review required'}</Badge> : undefined}
    >
      {loading || !data ? (
        <div className="row" style={{ gap: 10 }}><Spinner /> Running checks…</div>
      ) : (
        <div className="checklist">
          {data.checks.map((c) => (
            <div className="checklist__item" key={c.key}>
              <span className={`checklist__mark checklist__mark--${c.passed ? 'done' : c.severity === 'critical' ? 'required' : 'todo'}`}>
                {c.passed ? '✓' : c.severity === 'critical' ? '!' : '○'}
              </span>
              <span style={{ flex: 1 }}>
                {c.label}
                {c.detail && <span className="muted" style={{ fontSize: 12 }}> — {c.detail}</span>}
              </span>
              {!c.passed && <Badge tone={c.severity === 'critical' ? 'red' : 'amber'}>{c.severity}</Badge>}
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  )
}
