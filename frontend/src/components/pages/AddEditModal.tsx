import { useForm, type FieldValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Modal } from '@/components/ui/Modal'
import { SchemaFields } from '@/components/form/SchemaFields'
import { buildZodSchema, defaultsFromConfig } from '@/components/form/schema'
import type { FormConfig } from '@/components/form/types'

export function AddEditModal({
  open,
  title,
  config,
  currency,
  initialValues,
  onClose,
  onSubmit,
  saving,
  wide,
}: {
  open: boolean
  title: string
  config: FormConfig
  currency: string
  initialValues?: Partial<FieldValues> | null
  onClose: () => void
  onSubmit: (values: FieldValues) => void
  saving?: boolean
  wide?: boolean
}) {
  const form = useForm<FieldValues>({
    resolver: zodResolver(buildZodSchema(config)),
    defaultValues: { ...defaultsFromConfig(config), ...(initialValues ?? {}) },
  })
  const { control, handleSubmit } = form

  // Remount on open ensures defaultValues reflect the row being edited.
  if (!open) return null

  return (
    <Modal
      title={title}
      open={open}
      onClose={onClose}
      wide={wide}
      footer={
        <>
          <button className="btn btn--ghost" onClick={onClose} type="button">
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="button"
            disabled={saving}
            onClick={handleSubmit(onSubmit)}
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <SchemaFields config={config} control={control} currency={currency} bare />
      </form>
    </Modal>
  )
}
