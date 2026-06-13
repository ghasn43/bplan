import { useState } from 'react'
import type { JSONContent } from '@tiptap/react'
import { Badge } from '@/components/ui/Badge'
import { RichTextEditor } from '@/components/editor/RichTextEditor'
import { useUpdateSection } from '@/api/textPlanApi'
import type { TextPlanSection, TextPlanTopic } from '@/types/textPlan'

type Tab = 'guidance' | 'settings' | 'preview'

export function TextPlanRightPanel({
  projectId,
  section,
  topic,
}: {
  projectId: string
  section: TextPlanSection | null
  topic: TextPlanTopic | null
}) {
  const [tab, setTab] = useState<Tab>('guidance')
  const updateSection = useUpdateSection(projectId)

  return (
    <div className="tb-right">
      <div className="tb-right__tabs">
        {(['guidance', 'settings', 'preview'] as Tab[]).map((t) => (
          <button key={t} className={`tb-right__tab${tab === t ? ' tb-right__tab--active' : ''}`} onClick={() => setTab(t)}>
            {t === 'guidance' ? 'Guidance' : t === 'settings' ? 'Settings' : 'Preview'}
          </button>
        ))}
      </div>

      <div className="tb-right__body">
        {tab === 'guidance' && (
          <div className="stack--sm">
            {section && (
              <div>
                <div className="field__label">Section · {section.title}</div>
                <p className="tb-muted-text">{section.description || 'No section description.'}</p>
                {section.guidance_text && <div className="tb-guide-card">{section.guidance_text}</div>}
              </div>
            )}
            {topic ? (
              <div>
                <div className="field__label">Topic · {topic.title}</div>
                {topic.guidance_text ? (
                  <div className="tb-guide-card">{topic.guidance_text}</div>
                ) : (
                  <p className="tb-muted-text">
                    Write clear, evidence-based prose. Keep each topic focused on a single idea and link the
                    narrative to your financial assumptions where relevant.
                  </p>
                )}
                <ul className="tb-tips">
                  <li>Lead with the key message.</li>
                  <li>Use short paragraphs and bullet points.</li>
                  <li>Reconcile numbers with the financial model.</li>
                </ul>
              </div>
            ) : (
              <p className="tb-muted-text">Select a topic to see writing guidance.</p>
            )}
          </div>
        )}

        {tab === 'settings' && (
          <div className="stack--sm">
            {section && (
              <div>
                <div className="field__label">Section settings</div>
                <label className="tb-setting-row">
                  <span>Include in report</span>
                  <input
                    type="checkbox"
                    checked={section.include_in_report}
                    onChange={(e) => updateSection.mutate({ id: section.id, body: { include_in_report: e.target.checked } })}
                  />
                </label>
                <label className="tb-setting-row">
                  <span>Page break before</span>
                  <input
                    type="checkbox"
                    checked={section.page_break_before}
                    onChange={(e) => updateSection.mutate({ id: section.id, body: { page_break_before: e.target.checked } })}
                  />
                </label>
                <label className="tb-setting-row" style={{ alignItems: 'flex-start', flexDirection: 'column', gap: 4 }}>
                  <span>Section description</span>
                  <textarea
                    className="input"
                    rows={3}
                    defaultValue={section.description}
                    onBlur={(e) =>
                      e.target.value !== section.description &&
                      updateSection.mutate({ id: section.id, body: { description: e.target.value } })
                    }
                  />
                </label>
              </div>
            )}
            {topic && (
              <div>
                <div className="field__label">Topic details</div>
                <div className="tb-setting-row"><span>Status</span><Badge tone={topic.status === 'completed' ? 'green' : topic.status === 'draft' ? 'amber' : 'neutral'}>{topic.status.replace('_', ' ')}</Badge></div>
                <div className="tb-setting-row"><span>Word count</span><b>{topic.word_count}</b></div>
                <div className="tb-setting-row"><span>Reading time</span><b>~{topic.reading_time_minutes} min</b></div>
                <div className="tb-setting-row"><span>Images</span><b>{topic.images.length}</b></div>
                <div className="tb-setting-row"><span>In report</span><b>{topic.include_in_report ? 'Yes' : 'No'}</b></div>
                <div className="tb-setting-row"><span>Last edited</span><b>{new Date(topic.updated_at).toLocaleString()}</b></div>
              </div>
            )}
          </div>
        )}

        {tab === 'preview' && (
          <div>
            <div className="field__label">Report preview</div>
            {topic ? (
              <div className="tb-preview-card">
                <h3>{topic.title}</h3>
                {topic.content_html || topic.content_json ? (
                  <RichTextEditor
                    key={`preview-${topic.id}-${topic.updated_at}`}
                    editable={false}
                    content={
                      topic.content_json && Object.keys(topic.content_json).length > 0
                        ? (topic.content_json as JSONContent)
                        : topic.content_html
                    }
                  />
                ) : (
                  <p className="tb-muted-text">This topic has no content yet.</p>
                )}
              </div>
            ) : (
              <p className="tb-muted-text">Select a topic to preview it.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
