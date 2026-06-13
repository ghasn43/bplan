import { useState } from 'react'
import { NodeViewWrapper, type NodeViewProps } from '@tiptap/react'
import { API_BASE } from '@/api/client'

const ALIGNMENTS: { value: string; label: string }[] = [
  { value: 'left', label: '⯇' },
  { value: 'center', label: '☰' },
  { value: 'right', label: '⯈' },
  { value: 'full_width', label: '⤢' },
]

function resolveSrc(src: string): string {
  if (!src) return ''
  if (src.startsWith('http') || src.startsWith('data:')) return src
  if (src.startsWith('/api')) return src // served through the dev proxy
  return `${API_BASE}${src}`
}

export function BusinessPlanImageNodeView({ node, updateAttributes, deleteNode, selected, editor }: NodeViewProps) {
  const { src, alt, caption, alignment, widthPercentage } = node.attrs as Record<string, any>
  const editable = editor.isEditable
  const [broken, setBroken] = useState(false)

  return (
    <NodeViewWrapper
      className={`business-plan-image align-${alignment || 'center'}${selected ? ' is-selected' : ''}`}
      data-drag-handle
    >
      <figure style={{ width: alignment === 'full_width' ? '100%' : `${widthPercentage || 80}%` }}>
        {broken ? (
          <div className="business-plan-image__broken">⚠ Image unavailable</div>
        ) : (
          <img src={resolveSrc(src)} alt={alt || ''} draggable={false} onError={() => setBroken(true)} />
        )}
        {caption ? <figcaption>{caption}</figcaption> : null}

        {editable && selected && (
          <div className="business-plan-image__toolbar" contentEditable={false}>
            {ALIGNMENTS.map((a) => (
              <button
                key={a.value}
                type="button"
                className={`bpi-btn${alignment === a.value ? ' bpi-btn--active' : ''}`}
                title={`Align ${a.value}`}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => updateAttributes({ alignment: a.value })}
              >
                {a.label}
              </button>
            ))}
            <span className="bpi-sep" />
            <input
              type="range"
              min={20}
              max={100}
              step={5}
              value={widthPercentage || 80}
              title={`Width ${widthPercentage || 80}%`}
              onMouseDown={(e) => e.stopPropagation()}
              onChange={(e) => updateAttributes({ widthPercentage: Number(e.target.value) })}
            />
            <span className="bpi-sep" />
            <button
              type="button"
              className="bpi-btn"
              title="Edit caption"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => {
                const next = window.prompt('Caption', caption || '')
                if (next !== null) updateAttributes({ caption: next, title: next })
              }}
            >
              ✎ Caption
            </button>
            <button
              type="button"
              className="bpi-btn"
              title="Edit alt text"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => {
                const next = window.prompt('Alt text (for accessibility)', alt || '')
                if (next !== null) updateAttributes({ alt: next })
              }}
            >
              alt
            </button>
            <button
              type="button"
              className="bpi-btn bpi-btn--danger"
              title="Delete image"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => deleteNode()}
            >
              🗑
            </button>
          </div>
        )}
      </figure>
    </NodeViewWrapper>
  )
}
