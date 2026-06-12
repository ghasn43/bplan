import { SingletonFormPage } from '@/components/pages/SingletonFormPage'
import { SectionCard } from '@/components/SectionCard'
import { SummaryCard } from '@/components/SummaryCard'
import type { FormConfig } from '@/components/form/types'
import type { WorkingCapitalAssumption } from '@/types'
import { stockPurchaseCycleOptions } from '@/utils/options'

const config: FormConfig = [
  {
    title: 'Receivables',
    subtitle: 'How quickly customers pay you.',
    icon: '◲',
    fields: [
      { name: 'accounts_receivable_days', label: 'Accounts Receivable Days', kind: 'number', unit: 'days', help: 'Average days customers take to pay (DSO).' },
      { name: 'percent_sales_on_credit', label: '% of Sales on Credit', kind: 'percent' },
      { name: 'bad_debt_percent', label: 'Bad Debt %', kind: 'percent', help: 'Share of credit sales never collected.' },
      { name: 'customer_deposit_percent', label: 'Customer Deposit %', kind: 'percent', help: 'Upfront deposit collected from customers.' },
    ],
  },
  {
    title: 'Payables & Inventory',
    subtitle: 'How you manage supplier terms and stock.',
    icon: '◳',
    fields: [
      { name: 'accounts_payable_days', label: 'Accounts Payable Days', kind: 'number', unit: 'days', help: 'Average days you take to pay suppliers (DPO).' },
      { name: 'inventory_days', label: 'Inventory Days', kind: 'number', unit: 'days', help: 'Average days inventory is held (DIO).' },
      { name: 'safety_stock_percent', label: 'Safety Stock %', kind: 'percent' },
      { name: 'supplier_advance_percent', label: 'Supplier Advance %', kind: 'percent' },
      { name: 'stock_purchase_cycle', label: 'Stock Purchase Cycle', kind: 'select', options: stockPurchaseCycleOptions },
    ],
  },
  {
    title: 'Cash Reserve',
    icon: '◰',
    fields: [
      { name: 'minimum_cash_balance', label: 'Minimum Cash Balance', kind: 'currency', help: 'Floor the model should keep available at all times.' },
      { name: 'collection_warning_threshold_days', label: 'Collection Warning Threshold', kind: 'number', unit: 'days' },
      { name: 'notes', label: 'Notes', kind: 'textarea', span: 2 },
    ],
  },
]

export function WorkingCapitalPage() {
  return (
    <SingletonFormPage<WorkingCapitalAssumption>
      slug="working-capital"
      sectionKey="working-capital"
      config={config}
      renderTop={(v) => {
        const dso = Number(v.accounts_receivable_days) || 0
        const dpo = Number(v.accounts_payable_days) || 0
        const dio = Number(v.inventory_days) || 0
        const ccc = dio + dso - dpo
        const squeeze = dso > 2 * Math.max(dpo, 1)
        return (
          <SectionCard title="Cash Conversion Cycle" subtitle="Live preview from your inputs" icon="◷">
            <div className="stat-grid">
              <SummaryCard label="DSO (Receivables)" value={`${dso} days`} accent="blue" />
              <SummaryCard label="DIO (Inventory)" value={`${dio} days`} accent="slate" />
              <SummaryCard label="DPO (Payables)" value={`${dpo} days`} accent="amber" />
              <SummaryCard
                label="Cash Conversion Cycle"
                value={`${ccc} days`}
                accent={ccc <= 0 ? 'green' : 'amber'}
                help="DIO + DSO − DPO. Lower (or negative) is better for cash."
                hint={squeeze ? '⚠ Receivables far exceed payables — possible cash squeeze.' : undefined}
              />
            </div>
          </SectionCard>
        )
      }}
    />
  )
}
