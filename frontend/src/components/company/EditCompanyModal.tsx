import { useEffect, useState } from 'react'
import { Modal } from '@/components/ui/Modal'
import { useToast } from '@/components/ui/Toast'
import { useCompany, useUpdateCompany } from '@/api/companyApi'
import type { CompanyStatus, CompanyUpdate } from '@/types/company'

const STATUSES: CompanyStatus[] = ['active', 'inactive', 'demo']

export function EditCompanyModal({
  companyId,
  open,
  onClose,
}: {
  companyId: string | null
  open: boolean
  onClose: () => void
}) {
  const { notify } = useToast()
  const companyQ = useCompany(open ? companyId : null)
  const update = useUpdateCompany()
  const [form, setForm] = useState<CompanyUpdate>({})

  useEffect(() => {
    if (companyQ.data) {
      const c = companyQ.data
      setForm({
        company_name: c.company_name,
        trading_name: c.trading_name ?? '',
        legal_name: c.legal_name ?? '',
        industry_sector: c.industry_sector ?? '',
        business_description: c.business_description ?? '',
        country: c.country ?? '',
        city: c.city ?? '',
        website: c.website ?? '',
        status: c.status,
        notes: c.notes ?? '',
      })
    }
  }, [companyQ.data])

  const set = (patch: Partial<CompanyUpdate>) => setForm((f) => ({ ...f, ...patch }))

  const save = () => {
    if (!companyId) return
    if (!(form.company_name ?? '').trim()) {
      notify('Company name is required', 'error')
      return
    }
    update.mutate(
      { companyId, patch: form },
      {
        onSuccess: () => {
          notify('Company profile saved')
          onClose()
        },
        onError: (e) => notify((e as Error).message || 'Save failed', 'error'),
      },
    )
  }

  return (
    <Modal
      title="Edit Company Profile"
      open={open}
      onClose={onClose}
      wide
      footer={
        <div className="row" style={{ gap: 8, justifyContent: 'flex-end', width: '100%' }}>
          <button className="btn btn--secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn--primary" onClick={save} disabled={update.isPending}>
            {update.isPending ? 'Saving…' : 'Save Company Profile'}
          </button>
        </div>
      }
    >
      {companyQ.isLoading ? (
        <p className="muted">Loading company…</p>
      ) : (
        <div className="form-grid">
          <Field label="Company Name" required span={2}>
            <input className="input" value={form.company_name ?? ''} onChange={(e) => set({ company_name: e.target.value })}
              placeholder="e.g. AquaPure Smart Filters FZE" autoFocus />
          </Field>
          <Field label="Trading Name">
            <input className="input" value={form.trading_name ?? ''} onChange={(e) => set({ trading_name: e.target.value })} />
          </Field>
          <Field label="Legal Name">
            <input className="input" value={form.legal_name ?? ''} onChange={(e) => set({ legal_name: e.target.value })} />
          </Field>
          <Field label="Industry / Sector">
            <input className="input" value={form.industry_sector ?? ''} onChange={(e) => set({ industry_sector: e.target.value })}
              placeholder="e.g. Water Treatment & Smart Home Services" />
          </Field>
          <Field label="Status">
            <select className="input" value={form.status ?? 'active'} onChange={(e) => set({ status: e.target.value as CompanyStatus })}>
              {STATUSES.map((s) => <option key={s} value={s}>{s[0].toUpperCase() + s.slice(1)}</option>)}
            </select>
          </Field>
          <Field label="Country">
            <input className="input" value={form.country ?? ''} onChange={(e) => set({ country: e.target.value })} />
          </Field>
          <Field label="City">
            <input className="input" value={form.city ?? ''} onChange={(e) => set({ city: e.target.value })} />
          </Field>
          <Field label="Website">
            <input className="input" value={form.website ?? ''} onChange={(e) => set({ website: e.target.value })} placeholder="https://" />
          </Field>
          <Field label="Business Description" span={2}>
            <textarea className="input" rows={3} value={form.business_description ?? ''}
              onChange={(e) => set({ business_description: e.target.value })}
              placeholder="What the company does, its customers and value proposition." />
          </Field>
        </div>
      )}
    </Modal>
  )
}

function Field({ label, required, span, children }: { label: string; required?: boolean; span?: number; children: React.ReactNode }) {
  return (
    <div className="field" style={span === 2 ? { gridColumn: '1 / -1' } : undefined}>
      <span className="field__label">{label}{required && ' *'}</span>
      {children}
    </div>
  )
}
