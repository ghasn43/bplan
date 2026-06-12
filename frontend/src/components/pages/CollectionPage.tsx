import { useState, type ReactNode } from 'react'
import type { FieldValues } from 'react-hook-form'
import { PageHeader } from '@/components/PageHeader'
import { SaveBar } from '@/components/SaveBar'
import { SectionCard } from '@/components/SectionCard'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { AddEditModal } from './AddEditModal'
import type { FormConfig } from '@/components/form/types'
import {
  useCollectionSection,
  useDeleteCollectionItem,
  useSaveCollectionItem,
} from '@/api/hooks'
import { useProjectContext } from '@/layouts/ProjectContext'
import { useToast } from '@/components/ui/Toast'
import { pageBySlug } from '@/routes/nav'
import type { EntityBase } from '@/types'

interface Props<T extends EntityBase> {
  slug: string
  sectionKey: string
  itemNoun: string
  config: FormConfig
  columns: Column<T>[]
  emptyIcon?: string
  emptyDescription?: string
  modalWide?: boolean
  /** Summary tiles / extra UI above the table. */
  renderSummary?: (rows: T[]) => ReactNode
  /** Inject computed/linking fields before POST/PUT (e.g. product_id). */
  beforeSave?: (values: FieldValues, editing: T | null) => FieldValues
  /** When embedded in a tabbed workspace, hide the page header + save bar. */
  embedded?: boolean
}

export function CollectionPage<T extends EntityBase>({
  slug,
  sectionKey,
  itemNoun,
  config,
  columns,
  emptyIcon = '◫',
  emptyDescription,
  modalWide,
  renderSummary,
  beforeSave,
  embedded,
}: Props<T>) {
  const { projectId, currency } = useProjectContext()
  const page = pageBySlug(slug)
  const { data: rows, isLoading } = useCollectionSection<T>(projectId, sectionKey)
  const saveItem = useSaveCollectionItem(projectId, sectionKey)
  const deleteItem = useDeleteCollectionItem(projectId, sectionKey)
  const { notify } = useToast()

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<T | null>(null)

  const openAdd = () => {
    setEditing(null)
    setModalOpen(true)
  }
  const openEdit = (row: T) => {
    setEditing(row)
    setModalOpen(true)
  }

  const handleSubmit = (values: FieldValues) => {
    const payload = beforeSave ? beforeSave(values, editing) : values
    const merged = editing ? { ...editing, ...payload } : payload
    saveItem.mutate(merged as Partial<EntityBase> as T, {
      onSuccess: () => {
        notify(editing ? `${itemNoun} updated` : `${itemNoun} added`)
        setModalOpen(false)
      },
      onError: (e) => notify((e as Error).message || 'Save failed', 'error'),
    })
  }

  const handleDelete = (row: T) => {
    if (!window.confirm(`Delete this ${itemNoun.toLowerCase()}? This cannot be undone.`)) return
    deleteItem.mutate(row.id, {
      onSuccess: () => notify(`${itemNoun} deleted`),
      onError: (e) => notify((e as Error).message || 'Delete failed', 'error'),
    })
  }

  if (isLoading) return <LoadingScreen />
  const list = rows ?? []

  return (
    <>
      {!embedded ? (
        <PageHeader
          breadcrumb={`Business Plan · ${page?.group ?? ''}`}
          title={page?.label ?? ''}
          subtitle={page?.subtitle}
          actions={
            <button className="btn btn--primary" onClick={openAdd}>
              + Add {itemNoun}
            </button>
          }
        />
      ) : (
        <div className="row row--between" style={{ marginBottom: 16 }}>
          <span className="muted">{list.length} item{list.length === 1 ? '' : 's'}</span>
          <button className="btn btn--primary btn--sm" onClick={openAdd}>+ Add {itemNoun}</button>
        </div>
      )}

      <div className="stack">
        {list.length > 0 && renderSummary?.(list)}

        <SectionCard title={`${page?.label ?? ''}`} subtitle={`${list.length} ${itemNoun.toLowerCase()}${list.length === 1 ? '' : 's'}`}
          actions={
            list.length > 0 ? (
              <button className="btn btn--secondary btn--sm" onClick={openAdd}>
                + Add
              </button>
            ) : undefined
          }
        >
          {list.length === 0 ? (
            <EmptyState
              icon={emptyIcon}
              title={`No ${itemNoun.toLowerCase()}s yet`}
              description={emptyDescription ?? `Add your first ${itemNoun.toLowerCase()} to get started.`}
              action={
                <button className="btn btn--primary" onClick={openAdd}>
                  + Add {itemNoun}
                </button>
              }
            />
          ) : (
            <DataTable columns={columns} rows={list} onEdit={openEdit} onDelete={handleDelete} />
          )}
        </SectionCard>
      </div>

      <AddEditModal
        key={editing?.id ?? 'new'}
        open={modalOpen}
        wide={modalWide}
        title={editing ? `Edit ${itemNoun}` : `Add ${itemNoun}`}
        config={config}
        currency={currency}
        initialValues={editing as unknown as FieldValues | null}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
        saving={saveItem.isPending}
      />

      {!embedded && <SaveBar slug={slug} />}
    </>
  )
}
