import { ScenarioSelector } from '@/components/financials/ScenarioSelector'
import { PeriodViewToggle } from '@/components/financials/PeriodViewToggle'
import type { ReportRequest, ReportStyle } from '@/types/reports'
import type { ScenarioKey } from '@/types/incomeStatement'

const STYLES: { value: ReportStyle; label: string; hint: string }[] = [
  { value: 'investor', label: 'Investor', hint: 'For prospective investors' },
  { value: 'bank', label: 'Bank / Lender', hint: 'For financing banks' },
  { value: 'board', label: 'Board', hint: 'For the board of directors' },
  { value: 'management', label: 'Management', hint: 'Internal management copy' },
  { value: 'full', label: 'Full / Combined', hint: 'Investors, lenders & management' },
]

const TOGGLES: { key: keyof ReportRequest; label: string; hint: string }[] = [
  { key: 'include_assumptions', label: 'Assumptions', hint: 'Revenue, costs, staffing, capex, financing' },
  { key: 'include_charts', label: 'Charts & analysis', hint: 'KPIs and chart data tables' },
  { key: 'include_warnings', label: 'Warnings & reconciliations', hint: 'Balance and cash-flow checks' },
  { key: 'include_appendices', label: 'Appendices', hint: 'Detailed schedules and registers' },
]

export function ReportOptionsForm({
  value,
  onChange,
}: {
  value: ReportRequest
  onChange: (next: ReportRequest) => void
}) {
  const set = (patch: Partial<ReportRequest>) => onChange({ ...value, ...patch })

  return (
    <div className="stack--sm">
      <div className="row row--wrap" style={{ gap: 28, alignItems: 'flex-end' }}>
        <ScenarioSelector value={value.scenario} onChange={(s: ScenarioKey) => set({ scenario: s })} />
        <PeriodViewToggle
          value={value.view}
          onChange={(v) => set({ view: v === 'yearly' ? 'yearly' : 'monthly' })}
        />
        <div className="field" style={{ minWidth: 220 }}>
          <span className="field__label">Report style</span>
          <select
            className="input"
            value={value.report_style}
            onChange={(e) => set({ report_style: e.target.value as ReportStyle })}
          >
            {STYLES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label} — {s.hint}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="field">
        <span className="field__label">Include in report</span>
        <div className="row row--wrap" style={{ gap: 18 }}>
          {TOGGLES.map((t) => (
            <label key={t.key} className="row" style={{ gap: 8, alignItems: 'center', cursor: 'pointer' }} title={t.hint}>
              <input
                type="checkbox"
                checked={value[t.key] as boolean}
                onChange={(e) => set({ [t.key]: e.target.checked } as Partial<ReportRequest>)}
              />
              <span style={{ fontSize: 13.5 }}>{t.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
