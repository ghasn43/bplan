import type { ISMetadata } from '@/types/incomeStatement'

/** Centered IFRS-style statement masthead. */
export function FinancialStatementHeader({ meta }: { meta: ISMetadata }) {
  return (
    <div className="stmt-masthead">
      <div className="stmt-masthead__company">{meta.project_name}</div>
      <div className="stmt-masthead__title">{meta.statement_title}</div>
      <div className="stmt-masthead__caption">{meta.period_caption}</div>
      <div className="stmt-masthead__meta">
        <span>Currency: <strong>{meta.currency}</strong></span>
        <span className="stmt-masthead__dot">•</span>
        <span>Scenario: <strong>{meta.scenario_label}</strong></span>
        <span className="stmt-masthead__dot">•</span>
        <span>{meta.view === 'yearly' ? 'Annual view' : 'Monthly view'}</span>
      </div>
    </div>
  )
}
