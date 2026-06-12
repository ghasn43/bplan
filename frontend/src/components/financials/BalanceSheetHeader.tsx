import type { BalanceSheetMetadata } from '@/types/balanceSheet'

export function BalanceSheetHeader({ meta }: { meta: BalanceSheetMetadata }) {
  return (
    <div className="stmt-masthead">
      <div className="stmt-masthead__company">{meta.project_name}</div>
      <div className="stmt-masthead__title">{meta.statement_title}</div>
      <div className="stmt-masthead__caption">{meta.as_at_caption}</div>
      <div className="stmt-masthead__meta">
        <span>Currency: <strong>{meta.currency}</strong></span>
        <span className="stmt-masthead__dot">•</span>
        <span>Scenario: <strong>{meta.scenario_label}</strong></span>
        <span className="stmt-masthead__dot">•</span>
        <span>{meta.view === 'monthly' ? 'Monthly view' : 'Annual view'}</span>
      </div>
    </div>
  )
}
