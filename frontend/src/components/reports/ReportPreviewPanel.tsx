import { Badge } from '@/components/ui/Badge'
import type { ReportPreview } from '@/types/reports'

const SEV_TONE = { info: 'blue', warning: 'amber', critical: 'red' } as const

export function ReportPreviewPanel({ preview }: { preview: ReportPreview }) {
  return (
    <div className="stack--sm">
      <div className="row row--wrap" style={{ gap: 24 }}>
        <Meta label="Company" value={preview.company} />
        {preview.project_name && <Meta label="Project" value={preview.project_name} />}
        <Meta label="Scenario" value={preview.scenario_label} />
        <Meta label="Period" value={preview.period_range} />
        <Meta label="Currency" value={preview.currency} />
        <Meta label="Prepared for" value={preview.prepared_for} />
        <Meta label="Completion" value={`${preview.completion_percent}%`} />
      </div>

      {preview.highlights.length > 0 && (
        <div className="row row--wrap" style={{ gap: 12 }}>
          {preview.highlights.map((h) => (
            <div
              key={h.label}
              style={{
                border: '1px solid var(--border, #e2e8f0)',
                borderLeft: '3px solid #2563eb',
                borderRadius: 6,
                padding: '8px 12px',
                minWidth: 150,
              }}
            >
              <div className="muted" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.3 }}>
                {h.label}
              </div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{h.value}</div>
            </div>
          ))}
        </div>
      )}

      <div>
        <div className="field__label">Report contents ({preview.sections.length} sections)</div>
        <div className="row row--wrap" style={{ gap: 6, marginTop: 4 }}>
          {preview.sections.map((s, i) => (
            <Badge key={s.key} tone="neutral">
              {i + 1}. {s.title}
            </Badge>
          ))}
        </div>
      </div>

      {preview.blocking.length > 0 && (
        <div className="stack--sm">
          {preview.blocking.map((b) => (
            <div
              key={b}
              style={{ background: '#fef2f2', borderLeft: '3px solid #dc2626', color: '#991b1b', padding: '8px 12px', borderRadius: 6, fontSize: 13 }}
            >
              {b}
            </div>
          ))}
        </div>
      )}

      {preview.warnings.length > 0 && (
        <details>
          <summary style={{ cursor: 'pointer', fontSize: 13 }}>
            {preview.warnings.length} warning{preview.warnings.length > 1 ? 's' : ''} will be included in the report
          </summary>
          <div className="stack--sm" style={{ marginTop: 8 }}>
            {preview.warnings.map((w, i) => (
              <div key={i} className="row" style={{ gap: 8, alignItems: 'baseline' }}>
                <Badge tone={SEV_TONE[w.severity]}>{w.severity}</Badge>
                <span style={{ fontSize: 13 }}>{w.message}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="muted" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.3 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{value}</div>
    </div>
  )
}
