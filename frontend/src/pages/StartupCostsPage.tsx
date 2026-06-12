import { CollectionPage } from '@/components/pages/CollectionPage'
import type { Column } from '@/components/DataTable'
import type { FormConfig } from '@/components/form/types'
import { SummaryCard } from '@/components/SummaryCard'
import { Badge } from '@/components/ui/Badge'
import type { StartupCost } from '@/types'
import { formatCurrency, formatDate } from '@/utils/format'
import { labelFor, startupCostCategoryOptions } from '@/utils/options'
import { useProjectContext } from '@/layouts/ProjectContext'

const config: FormConfig = [
  {
    title: 'Startup Cost',
    fields: [
      { name: 'name', label: 'Cost Name', kind: 'text', required: true, span: 2, placeholder: 'e.g. Company Registration' },
      { name: 'category', label: 'Category', kind: 'select', options: startupCostCategoryOptions, required: true },
      { name: 'amount', label: 'Amount', kind: 'currency', required: true },
      { name: 'payment_date', label: 'Payment Date', kind: 'date', required: true },
      {
        name: 'capitalized', label: 'Capitalized', kind: 'switch',
        help: 'Capitalized costs become assets and are depreciated; expensed costs hit the P&L immediately.',
      },
      { name: 'notes', label: 'Notes', kind: 'textarea', span: 2 },
    ],
  },
]

export function StartupCostsPage() {
  const { currency } = useProjectContext()

  const columns: Column<StartupCost>[] = [
    { header: 'Name', cell: (r) => <strong>{r.name}</strong> },
    { header: 'Category', cell: (r) => labelFor(startupCostCategoryOptions, r.category) },
    { header: 'Amount', align: 'right', cell: (r) => formatCurrency(r.amount, currency) },
    { header: 'Payment Date', cell: (r) => formatDate(r.payment_date) },
    { header: 'Treatment', cell: (r) => <Badge tone={r.capitalized ? 'blue' : 'neutral'}>{r.capitalized ? 'Capitalized' : 'Expensed'}</Badge> },
  ]

  return (
    <CollectionPage<StartupCost>
      slug="startup-costs"
      sectionKey="startup-costs"
      itemNoun="Startup Cost"
      config={config}
      columns={columns}
      emptyIcon="◰"
      emptyDescription="Capture all pre-opening and launch costs required before the business starts trading."
      renderSummary={(rows) => {
        const total = rows.reduce((s, r) => s + r.amount, 0)
        const capitalized = rows.filter((r) => r.capitalized).reduce((s, r) => s + r.amount, 0)
        const expensed = total - capitalized
        return (
          <div className="stat-grid">
            <SummaryCard label="Total Startup Funding" value={formatCurrency(total, currency)} accent="amber" help="Total cash required before opening." />
            <SummaryCard label="Capitalized" value={formatCurrency(capitalized, currency)} accent="blue" />
            <SummaryCard label="Expensed" value={formatCurrency(expensed, currency)} accent="slate" />
          </div>
        )
      }}
    />
  )
}
