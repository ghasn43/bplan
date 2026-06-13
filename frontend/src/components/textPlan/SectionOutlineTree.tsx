import { useEffect, useMemo, useState } from 'react'
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  closestCorners,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { SortableContext, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { TextPlanDocument, TextPlanSection, TextPlanTopic } from '@/types/textPlan'

const STATUS_DOT: Record<string, string> = {
  not_started: '#cbd5e1',
  draft: '#d97706',
  in_review: '#2563eb',
  completed: '#059669',
}

type Handlers = {
  onReorderSections: (ids: string[]) => void
  onReorderTopics: (sectionId: string, ids: string[]) => void
  onMoveTopic: (topicId: string, targetSectionId: string, index: number) => void
}

export function SectionOutlineTree({
  doc,
  selectedTopicId,
  onSelectTopic,
  onSelectSection,
  selectedSectionId,
  handlers,
}: {
  doc: TextPlanDocument
  selectedTopicId: string | null
  selectedSectionId: string | null
  onSelectTopic: (sectionId: string, topicId: string) => void
  onSelectSection: (sectionId: string) => void
  handlers: Handlers
}) {
  const [sections, setSections] = useState<TextPlanSection[]>(doc.sections)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})

  // Keep local mirror in sync when not mid-drag.
  useEffect(() => {
    if (!activeId) setSections(doc.sections)
  }, [doc, activeId])

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }))

  const sectionIds = useMemo(() => sections.map((s) => `S:${s.id}`), [sections])

  const findContainer = (id: string): string | null => {
    if (id.startsWith('S:')) return id.slice(2)
    const tid = id.slice(2)
    const sec = sections.find((s) => s.topics.some((t) => t.id === tid))
    return sec?.id ?? null
  }

  const activeTopic: TextPlanTopic | null = activeId?.startsWith('T:')
    ? sections.flatMap((s) => s.topics).find((t) => t.id === activeId.slice(2)) ?? null
    : null
  const activeSection: TextPlanSection | null = activeId?.startsWith('S:')
    ? sections.find((s) => s.id === activeId.slice(2)) ?? null
    : null

  function onDragStart(e: DragStartEvent) {
    setActiveId(String(e.active.id))
  }

  function onDragOver(e: DragOverEvent) {
    const { active, over } = e
    if (!over) return
    const activeStr = String(active.id)
    const overStr = String(over.id)
    if (!activeStr.startsWith('T:')) return // only topics move across containers

    const fromSection = findContainer(activeStr)
    const toSection = findContainer(overStr)
    if (!fromSection || !toSection || fromSection === toSection) return

    setSections((prev) => {
      const next = prev.map((s) => ({ ...s, topics: [...s.topics] }))
      const src = next.find((s) => s.id === fromSection)!
      const dst = next.find((s) => s.id === toSection)!
      const topicId = activeStr.slice(2)
      const idx = src.topics.findIndex((t) => t.id === topicId)
      if (idx < 0) return prev
      const [moved] = src.topics.splice(idx, 1)
      let insertAt = dst.topics.length
      if (overStr.startsWith('T:')) {
        const overIdx = dst.topics.findIndex((t) => t.id === overStr.slice(2))
        insertAt = overIdx < 0 ? dst.topics.length : overIdx
      }
      dst.topics.splice(insertAt, 0, moved)
      return next
    })
  }

  function onDragEnd(e: DragEndEvent) {
    const { active, over } = e
    const activeStr = String(active.id)
    setActiveId(null)
    if (!over) {
      setSections(doc.sections)
      return
    }
    const overStr = String(over.id)

    if (activeStr.startsWith('S:') && overStr.startsWith('S:')) {
      const oldIndex = sections.findIndex((s) => `S:${s.id}` === activeStr)
      const newIndex = sections.findIndex((s) => `S:${s.id}` === overStr)
      if (oldIndex !== newIndex && oldIndex >= 0 && newIndex >= 0) {
        const next = [...sections]
        const [moved] = next.splice(oldIndex, 1)
        next.splice(newIndex, 0, moved)
        setSections(next)
        handlers.onReorderSections(next.map((s) => s.id))
      }
      return
    }

    if (activeStr.startsWith('T:')) {
      const topicId = activeStr.slice(2)
      const targetSectionId = findContainer(overStr) ?? findContainer(activeStr)
      if (!targetSectionId) return
      const target = sections.find((s) => s.id === targetSectionId)!
      // reorder within target so the dropped position is final
      let ids = target.topics.map((t) => t.id)
      if (overStr.startsWith('T:') && overStr.slice(2) !== topicId) {
        const from = ids.indexOf(topicId)
        const to = ids.indexOf(overStr.slice(2))
        if (from >= 0 && to >= 0) {
          ids = [...ids]
          ids.splice(from, 1)
          ids.splice(to, 0, topicId)
        }
      }
      const origSection = doc.sections.find((s) => s.topics.some((t) => t.id === topicId))
      if (origSection && origSection.id === targetSectionId) {
        handlers.onReorderTopics(targetSectionId, ids)
      } else {
        handlers.onMoveTopic(topicId, targetSectionId, Math.max(0, ids.indexOf(topicId)))
      }
    }
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragEnd={onDragEnd}
      onDragCancel={() => {
        setActiveId(null)
        setSections(doc.sections)
      }}
    >
      <SortableContext items={sectionIds} strategy={verticalListSortingStrategy}>
        <div className="tb-tree">
          {sections.map((section, i) => (
            <SortableSection
              key={section.id}
              section={section}
              index={i + 1}
              collapsed={!!collapsed[section.id]}
              onToggle={() => setCollapsed((c) => ({ ...c, [section.id]: !c[section.id] }))}
              selected={selectedSectionId === section.id}
              selectedTopicId={selectedTopicId}
              onSelectSection={onSelectSection}
              onSelectTopic={onSelectTopic}
            />
          ))}
        </div>
      </SortableContext>
      <DragOverlay>
        {activeTopic ? (
          <div className="tb-topic tb-topic--ghost">{activeTopic.title}</div>
        ) : activeSection ? (
          <div className="tb-section-head tb-section-head--ghost">{activeSection.title}</div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

function SortableSection({
  section,
  index,
  collapsed,
  onToggle,
  selected,
  selectedTopicId,
  onSelectSection,
  onSelectTopic,
}: {
  section: TextPlanSection
  index: number
  collapsed: boolean
  onToggle: () => void
  selected: boolean
  selectedTopicId: string | null
  onSelectSection: (id: string) => void
  onSelectTopic: (sectionId: string, topicId: string) => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `S:${section.id}`,
    data: { type: 'section' },
  })
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.5 : 1 }
  return (
    <div ref={setNodeRef} style={style} className="tb-section">
      <div className={`tb-section-head${selected ? ' tb-section-head--active' : ''}`}>
        <span className="tb-drag" {...attributes} {...listeners} title="Drag to reorder section">
          ⠿
        </span>
        <button className="tb-caret" onClick={onToggle} aria-label={collapsed ? 'Expand' : 'Collapse'}>
          {collapsed ? '▸' : '▾'}
        </button>
        <button className="tb-section-title" onClick={() => onSelectSection(section.id)}>
          <span className="tb-section-index">{index}</span>
          <span className="tb-section-name">{section.title}</span>
          {!section.include_in_report && <span className="tb-excluded" title="Excluded from report">⊘</span>}
        </button>
        <span className="tb-count">{section.topics.length}</span>
      </div>
      {!collapsed && (
        <SortableContext items={section.topics.map((t) => `T:${t.id}`)} strategy={verticalListSortingStrategy}>
          <div className="tb-topics">
            {section.topics.map((topic) => (
              <SortableTopic
                key={topic.id}
                topic={topic}
                sectionId={section.id}
                selected={selectedTopicId === topic.id}
                onSelect={() => onSelectTopic(section.id, topic.id)}
              />
            ))}
            {section.topics.length === 0 && <div className="tb-topics-empty">No topics — add one</div>}
          </div>
        </SortableContext>
      )}
    </div>
  )
}

function SortableTopic({
  topic,
  selected,
  onSelect,
}: {
  topic: TextPlanTopic
  sectionId: string
  selected: boolean
  onSelect: () => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `T:${topic.id}`,
    data: { type: 'topic' },
  })
  const style = { transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.4 : 1 }
  return (
    <div ref={setNodeRef} style={style} className={`tb-topic${selected ? ' tb-topic--active' : ''}`}>
      <span className="tb-drag tb-drag--sm" {...attributes} {...listeners} title="Drag to reorder / move">
        ⠿
      </span>
      <span className="tb-status-dot" style={{ background: STATUS_DOT[topic.status] ?? '#cbd5e1' }} />
      <button className="tb-topic-title" onClick={onSelect}>
        {topic.title}
      </button>
      {!topic.include_in_report && <span className="tb-excluded tb-excluded--sm" title="Excluded from report">⊘</span>}
    </div>
  )
}
