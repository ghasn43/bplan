import { useState, type ReactNode } from 'react'
import type { FieldValues } from 'react-hook-form'
import { PageHeader } from '@/components/PageHeader'
import { SaveBar } from '@/components/SaveBar'
import { SectionCard } from '@/components/SectionCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingScreen } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { AddEditModal } from './AddEditModal'
import type { FormConfig } from '@/components/form/types'
import {
  useCollectionSection,
  useSaveCollectionItem,
} from '@/api/hooks'
import { useProjectContext } from '@/layouts/ProjectContext'
import { useToast } from '@/components/ui/Toast'
import { pageBySlug } from '@/routes/nav'
import type { EntityBase, ProductService } from '@/types'

interface WithProduct extends EntityBase {
  product_id: string
}

interface Props<T extends WithProduct> {
  slug: string
  sectionKey: string
  itemNoun: string
  /** Build the modal form config for a given product (enables dynamic fields). */
  configFor: (product: ProductService) => FormConfig
  /** Compact per-product summary line shown on each product card. */
  renderSummary: (assumption: T | undefined, product: ProductService) => ReactNode
  modalWide?: boolean
  /** When embedded in a tabbed workspace, hide the page header + save bar. */
  embedded?: boolean
}

export function PerProductPage<T extends WithProduct>({
  slug,
  sectionKey,
  itemNoun,
  configFor,
  renderSummary,
  modalWide,
  embedded,
}: Props<T>) {
  const { projectId, currency } = useProjectContext()
  const page = pageBySlug(slug)
  const productsQ = useCollectionSection<ProductService>(projectId, 'products')
  const assumptionsQ = useCollectionSection<T>(projectId, sectionKey)
  const save = useSaveCollectionItem(projectId, sectionKey)
  const { notify } = useToast()

  const [editing, setEditing] = useState<{ product: ProductService; assumption: T | null } | null>(null)

  if (productsQ.isLoading || assumptionsQ.isLoading) return <LoadingScreen />

  const products = productsQ.data ?? []
  const assumptions = assumptionsQ.data ?? []
  const byProduct = new Map(assumptions.map((a) => [a.product_id, a]))

  const handleSubmit = (values: FieldValues) => {
    if (!editing) return
    const existing = editing.assumption
    const merged = {
      ...(existing ?? {}),
      ...values,
      product_id: editing.product.id,
    }
    save.mutate(merged as Partial<EntityBase> as T, {
      onSuccess: () => {
        notify(`${itemNoun} saved`)
        setEditing(null)
      },
      onError: (e) => notify((e as Error).message || 'Save failed', 'error'),
    })
  }

  return (
    <>
      {!embedded && (
        <PageHeader
          breadcrumb={`Business Plan · ${page?.group ?? ''}`}
          title={page?.label ?? ''}
          subtitle={page?.subtitle}
        />
      )}

      {products.length === 0 ? (
        <SectionCard>
          <EmptyState
            icon="◫"
            title="No products yet"
            description="Add products and services first — these assumptions are defined per product."
          />
        </SectionCard>
      ) : (
        <div className="stack">
          {products.map((product) => {
            const assumption = byProduct.get(product.id)
            const hasData = !!assumption
            return (
              <SectionCard
                key={product.id}
                title={product.name}
                subtitle={product.category || undefined}
                icon="◴"
                actions={
                  <>
                    {hasData ? (
                      <Badge tone="green" dot>
                        Configured
                      </Badge>
                    ) : (
                      <Badge tone="amber" dot>
                        Not configured
                      </Badge>
                    )}
                    <button
                      className="btn btn--secondary btn--sm"
                      onClick={() => setEditing({ product, assumption: assumption ?? null })}
                    >
                      {hasData ? 'Edit assumptions' : 'Configure'}
                    </button>
                  </>
                }
              >
                {renderSummary(assumption, product)}
              </SectionCard>
            )
          })}
        </div>
      )}

      {editing && (
        <AddEditModal
          key={editing.product.id}
          open
          wide={modalWide}
          title={`${itemNoun} — ${editing.product.name}`}
          config={configFor(editing.product)}
          currency={currency}
          initialValues={editing.assumption as unknown as FieldValues | null}
          onClose={() => setEditing(null)}
          onSubmit={handleSubmit}
          saving={save.isPending}
        />
      )}

      {!embedded && <SaveBar slug={slug} />}
    </>
  )
}
