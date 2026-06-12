import { SectionCard } from '@/components/SectionCard'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import type { BalanceSheetReconciliation } from '@/types/balanceSheet'

export function BalanceSheetReconciliationPanel({
  data,
  loading,
}: {
  data?: BalanceSheetReconciliation
  loading: boolean
}) {
  return (
    <SectionCard
      title="Reconciliation & controls"
      subtitle="Big 4-style checks tying the statement back to the schedules and the income statement."
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
