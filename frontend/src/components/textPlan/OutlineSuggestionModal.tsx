import { useState } from 'react'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { useToast } from '@/components/ui/Toast'
import { useApplyTemplate, useOutlineSuggestions } from '@/api/textPlanApi'
import type { OutlineTemplateInfo } from '@/types/textPlan'

export function OutlineSuggestionModal({
  projectId,
  open,
  onClose,
  hasExisting,
}: {
  projectId: string
  open: boolean
  onClose: () => void
  hasExisting: boolean
}) {
  const { notify } = useToast()
  const suggestionsQ = useOutlineSuggestions(projectId, open)
  const apply = useApplyTemplate(projectId)
  const [selected, setSelected] = useState<string | null>(null)
  const [mode, setMode] = useState<'replace' | 'append'>(hasExisting ? 'append' : 'replace')
  const [withSample, setWithSample] = useState(false)

  const data = suggestionsQ.data
  const templates = data?.templates ?? []
  const recommended = data?.recommended_template_id
  const active = selected ?? recommended ?? null
  const activeTemplate = templates.find((t) => t.id === active)

  const onApply = () => {
    if (!active) return
    apply.mutate(
      { template_id: active, mode, with_sample_content: withSample },
      {
        onSuccess: () => {
          notify('Outline applied to your business plan.', 'success')
          onClose()
        },
        onError: (e) => notify((e as Error).message ?? 'Failed to apply outline.', 'error'),
      },
    )
  }

  return (
    <Modal
      title="Suggested business plan outlines"
      open={open}
      onClose={onClose}
      wide
      footer={
        <div className="row" style={{ justifyContent: 'space-between', width: '100%' }}>
          <label className="row" style={{ gap: 8, fontSize: 13, alignItems: 'center' }}>
            <input type="checkbox" checked={withSample} onChange={(e) => setWithSample(e.target.checked)} />
            Include sample guidance content
          </label>
          <div className="row" style={{ gap: 8 }}>
            {hasExisting && (
              <div className="segmented">
                <button className={`segmented__btn${mode === 'append' ? ' segmented__btn--active' : ''}`} onClick={() => setMode('append')}>
                  Append
                </button>
                <button className={`segmented__btn${mode === 'replace' ? ' segmented__btn--active' : ''}`} onClick={() => setMode('replace')}>
                  Replace all
                </button>
              </div>
            )}
            <button className="btn btn--secondary" onClick={onClose}>
              Cancel
            </button>
            <button className="btn btn--primary" disabled={!active || apply.isPending} onClick={onApply}>
              {apply.isPending ? 'Applying…' : `Apply ${activeTemplate?.name ?? 'outline'}`}
            </button>
          </div>
        </div>
      }
    >
      {suggestionsQ.isLoading ? (
        <p className="muted">Analysing your business setup…</p>
      ) : (
        <>
          {data && (
            <div
              style={{
                background: '#eff6ff',
                border: '1px solid #bfdbfe',
                borderRadius: 8,
                padding: '10px 14px',
                marginBottom: 14,
                fontSize: 13.5,
                color: '#1e40af',
              }}
            >
              💡 {data.explanation}
            </div>
          )}
          <div className="tb-template-grid">
            {templates.map((t) => (
              <TemplateCard
                key={t.id}
                template={t}
                active={active === t.id}
                recommended={recommended === t.id}
                onSelect={() => setSelected(t.id)}
              />
            ))}
          </div>
          {activeTemplate && (
            <div style={{ marginTop: 16 }}>
              <div className="field__label">Preview — {activeTemplate.name}</div>
              <div className="tb-template-preview">
                {activeTemplate.sections.map((s) => (
                  <div key={s.title} className="tb-template-preview__section">
                    <div className="tb-template-preview__title">{s.title}</div>
                    <div className="tb-template-preview__topics">
                      {s.topics.map((tp) => (
                        <span key={tp.title} className="tb-chip">
                          {tp.title}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </Modal>
  )
}

function TemplateCard({
  template,
  active,
  recommended,
  onSelect,
}: {
  template: OutlineTemplateInfo
  active: boolean
  recommended: boolean
  onSelect: () => void
}) {
  return (
    <button type="button" className={`tb-template-card${active ? ' tb-template-card--active' : ''}`} onClick={onSelect}>
      <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="tb-template-card__name">{template.name}</span>
        {recommended && <Badge tone="green">Recommended</Badge>}
      </div>
      <div className="tb-template-card__desc">{template.description}</div>
      <div className="tb-template-card__meta">
        {template.section_count} sections · {template.topic_count} topics
      </div>
    </button>
  )
}
