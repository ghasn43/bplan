import { SectionCard } from '@/components/SectionCard'
import { Badge } from '@/components/ui/Badge'
import { LoadingScreen, Spinner } from '@/components/ui/Spinner'
import type { IncomeStatementReconciliation } from '@/types/incomeStatement'

export function ReconciliationPanel({
  data,
  loading,
}: {
  data?: IncomeStatementReconciliation
  loading: boolean
}) {
  return (
    <SectionCard
      title="Reconciliation & controls"
      subtitle="Big 4-style checks that the statement ties back to the assumptions."
      icon="✓"
      actions={
        data ? (
          <Badge tone={data.all_passed ? 'green' : 'amber'} dot>
            {data.all_passed ? 'All checks passed' : 'Review required'}
          </Badge>
        ) : undefined
      }
    >
      {loading || !data ? (
        loading ? <div className="row" style={{ gap: 10 }}><Spinner /> Running checks…</div> : <LoadingScreen />
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
              {!c.passed && (
                <Badge tone={c.severity === 'critical' ? 'red' : 'amber'}>{c.severity}</Badge>
              )}
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  )
}
