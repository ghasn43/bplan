import { useEffect, useState } from 'react'
import { useForm, type FieldValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { PageHeader } from '@/components/PageHeader'
import { SaveBar } from '@/components/SaveBar'
import { SectionCard } from '@/components/SectionCard'
import { SummaryCard } from '@/components/SummaryCard'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/ui/EmptyState'
import { Badge } from '@/components/ui/Badge'
import { LoadingScreen } from '@/components/ui/Spinner'
import { SchemaFields } from '@/components/form/SchemaFields'
import { AddEditModal } from '@/components/pages/AddEditModal'
import { buildZodSchema, defaultsFromConfig } from '@/components/form/schema'
import type { FormConfig } from '@/components/form/types'
import { useSaveSingletonSection, useSingletonSection } from '@/api/hooks'
import { useProjectContext } from '@/layouts/ProjectContext'
import { useToast } from '@/components/ui/Toast'
import type { EquityFunding, Financing, GrantFunding, LoanFunding } from '@/types'
import { formatCurrency, formatDate, formatPercent } from '@/utils/format'
import { labelFor, repaymentTypeOptions } from '@/utils/options'

const equityConfig: FormConfig = [
  {
    title: 'Equity Funding',
    subtitle: 'Capital contributed by founders and investors.',
    icon: '◳',
    fields: [
      { name: 'founder_capital', label: 'Founder Capital', kind: 'currency' },
      { name: 'investor_equity', label: 'Investor Equity', kind: 'currency' },
      { name: 'investment_date', label: 'Investment Date', kind: 'date' },
      { name: 'shareholding_percent', label: 'Investor Shareholding %', kind: 'percent', help: 'Equity stake given to investors.' },
      { name: 'investor_name', label: 'Investor Name', kind: 'text' },
      { name: 'dividend_policy_percent', label: 'Dividend Policy %', kind: 'percent', help: 'Share of profits distributed to shareholders.' },
      { name: 'use_of_funds', label: 'Use of Funds', kind: 'textarea', span: 2, placeholder: 'How the raised capital will be deployed.' },
    ],
  },
]

const loanConfig: FormConfig = [
  {
    title: 'Loan',
    fields: [
      { name: 'name', label: 'Loan Name', kind: 'text', required: true, span: 2 },
      { name: 'lender', label: 'Lender', kind: 'text' },
      { name: 'amount', label: 'Loan Amount', kind: 'currency', required: true },
      { name: 'drawdown_date', label: 'Drawdown Date', kind: 'date' },
      { name: 'interest_rate', label: 'Interest Rate', kind: 'percent', help: 'Annual interest rate.' },
      { name: 'repayment_period_months', label: 'Repayment Period', kind: 'number', unit: 'months', required: true, min: 1 },
      { name: 'grace_period_months', label: 'Grace Period', kind: 'number', unit: 'months', help: 'Months before repayments begin.' },
      { name: 'repayment_type', label: 'Repayment Type', kind: 'select', options: repaymentTypeOptions },
      { name: 'arrangement_fee', label: 'Arrangement Fee', kind: 'currency' },
      { name: 'collateral', label: 'Collateral', kind: 'text', span: 2 },
    ],
  },
]

const grantConfig: FormConfig = [
  {
    title: 'Grant / Other Funding',
    fields: [
      { name: 'name', label: 'Grant Name', kind: 'text', required: true, span: 2 },
      { name: 'amount', label: 'Amount', kind: 'currency', required: true },
      { name: 'expected_date', label: 'Expected Date', kind: 'date' },
      { name: 'restrictions', label: 'Restrictions', kind: 'textarea', span: 2 },
    ],
  },
]

const uid = () =>
  (typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `tmp-${Date.now()}-${Math.random()}`)

export function FinancingPage() {
  const { projectId, currency } = useProjectContext()
  const { data, isLoading } = useSingletonSection<Financing>(projectId, 'financing')
  const save = useSaveSingletonSection<Record<string, unknown>>(projectId, 'financing')
  const { notify } = useToast()

  const [loans, setLoans] = useState<LoanFunding[]>([])
  const [grants, setGrants] = useState<GrantFunding[]>([])
  const [dirty, setDirty] = useState(false)
  const [loanModal, setLoanModal] = useState<{ open: boolean; editing: LoanFunding | null }>({ open: false, editing: null })
  const [grantModal, setGrantModal] = useState<{ open: boolean; editing: GrantFunding | null }>({ open: false, editing: null })

  const equityForm = useForm<FieldValues>({
    resolver: zodResolver(buildZodSchema(equityConfig)),
    defaultValues: defaultsFromConfig(equityConfig),
  })

  useEffect(() => {
    if (data === undefined) return
    const eq = data?.equity
    equityForm.reset({ ...defaultsFromConfig(equityConfig), ...(eq ?? {}) })
    setLoans(data?.loans ?? [])
    setGrants(data?.grants ?? [])
    setDirty(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data])

  if (isLoading) return <LoadingScreen />

  const handleSave = equityForm.handleSubmit(
    (equityValues) => {
      const payload = {
        ...(data ?? {}),
        equity: { ...(data?.equity ?? {}), ...equityValues } as EquityFunding,
        loans,
        grants,
      }
      save.mutate(payload as Record<string, unknown>, {
        onSuccess: () => {
          notify('Financing saved')
          setDirty(false)
        },
        onError: (e) => notify((e as Error).message || 'Save failed', 'error'),
      })
    },
    () => notify('Please fix the highlighted equity fields', 'error'),
  )

  const saveLoan = (values: FieldValues) => {
    const editing = loanModal.editing
    const item = { ...(editing ?? { id: uid() }), ...values } as LoanFunding
    setLoans((cur) => (editing ? cur.map((l) => (l.id === editing.id ? item : l)) : [...cur, item]))
    setLoanModal({ open: false, editing: null })
    setDirty(true)
  }
  const saveGrant = (values: FieldValues) => {
    const editing = grantModal.editing
    const item = { ...(editing ?? { id: uid() }), ...values } as GrantFunding
    setGrants((cur) => (editing ? cur.map((g) => (g.id === editing.id ? item : g)) : [...cur, item]))
    setGrantModal({ open: false, editing: null })
    setDirty(true)
  }

  const equityVals = equityForm.watch()
  const totalEquity = (Number(equityVals.founder_capital) || 0) + (Number(equityVals.investor_equity) || 0)
  const totalLoans = loans.reduce((s, l) => s + (l.amount || 0), 0)
  const totalGrants = grants.reduce((s, g) => s + (g.amount || 0), 0)
  const totalFunding = totalEquity + totalLoans + totalGrants

  const loanColumns: Column<LoanFunding>[] = [
    { header: 'Loan', cell: (r) => <strong>{r.name}</strong> },
    { header: 'Lender', cell: (r) => r.lender || '—' },
    { header: 'Amount', align: 'right', cell: (r) => formatCurrency(r.amount, currency) },
    { header: 'Rate', align: 'right', cell: (r) => formatPercent(r.interest_rate) },
    { header: 'Term', align: 'right', cell: (r) => `${r.repayment_period_months} mo` },
    { header: 'Type', cell: (r) => <Badge tone="neutral">{labelFor(repaymentTypeOptions, r.repayment_type)}</Badge> },
  ]
  const grantColumns: Column<GrantFunding>[] = [
    { header: 'Grant', cell: (r) => <strong>{r.name}</strong> },
    { header: 'Amount', align: 'right', cell: (r) => formatCurrency(r.amount, currency) },
    { header: 'Expected', cell: (r) => formatDate(r.expected_date) },
    { header: 'Restrictions', cell: (r) => r.restrictions || '—' },
  ]

  return (
    <>
      <PageHeader
        breadcrumb="Business Plan · Capital & Compliance"
        title="Financing"
        subtitle="How the business will be funded — equity, debt, and grants."
      />

      <div className="stack">
        <div className="stat-grid">
          <SummaryCard label="Total Equity" value={formatCurrency(totalEquity, currency)} accent="blue" />
          <SummaryCard label="Total Loans" value={formatCurrency(totalLoans, currency)} accent="amber" />
          <SummaryCard label="Total Grants" value={formatCurrency(totalGrants, currency)} accent="green" />
          <SummaryCard label="Total Funding" value={formatCurrency(totalFunding, currency)} accent="slate" help="Equity + debt + grants." />
        </div>

        <SchemaFields config={equityConfig} control={equityForm.control} currency={currency} />

        <SectionCard
          title="Loans"
          subtitle={`${loans.length} loan${loans.length === 1 ? '' : 's'}`}
          icon="◳"
          actions={
            <button className="btn btn--secondary btn--sm" onClick={() => setLoanModal({ open: true, editing: null })}>
              + Add Loan
            </button>
          }
        >
          {loans.length === 0 ? (
            <EmptyState icon="◳" title="No loans" description="Add debt facilities with their repayment terms." />
          ) : (
            <DataTable
              columns={loanColumns}
              rows={loans}
              onEdit={(r) => setLoanModal({ open: true, editing: r })}
              onDelete={(r) => {
                setLoans((cur) => cur.filter((l) => l.id !== r.id))
                setDirty(true)
              }}
            />
          )}
        </SectionCard>

        <SectionCard
          title="Grants & Other Funding"
          subtitle={`${grants.length} item${grants.length === 1 ? '' : 's'}`}
          icon="⊞"
          actions={
            <button className="btn btn--secondary btn--sm" onClick={() => setGrantModal({ open: true, editing: null })}>
              + Add Grant
            </button>
          }
        >
          {grants.length === 0 ? (
            <EmptyState icon="⊞" title="No grants" description="Add grants or non-dilutive funding sources." />
          ) : (
            <DataTable
              columns={grantColumns}
              rows={grants}
              onEdit={(r) => setGrantModal({ open: true, editing: r })}
              onDelete={(r) => {
                setGrants((cur) => cur.filter((g) => g.id !== r.id))
                setDirty(true)
              }}
            />
          )}
        </SectionCard>
      </div>

      <AddEditModal
        key={loanModal.editing?.id ?? 'new-loan'}
        open={loanModal.open}
        wide
        title={loanModal.editing ? 'Edit Loan' : 'Add Loan'}
        config={loanConfig}
        currency={currency}
        initialValues={loanModal.editing as unknown as FieldValues | null}
        onClose={() => setLoanModal({ open: false, editing: null })}
        onSubmit={saveLoan}
      />
      <AddEditModal
        key={grantModal.editing?.id ?? 'new-grant'}
        open={grantModal.open}
        title={grantModal.editing ? 'Edit Grant' : 'Add Grant'}
        config={grantConfig}
        currency={currency}
        initialValues={grantModal.editing as unknown as FieldValues | null}
        onClose={() => setGrantModal({ open: false, editing: null })}
        onSubmit={saveGrant}
      />

      <SaveBar slug="financing" onSave={handleSave} saving={save.isPending} dirty={dirty || equityForm.formState.isDirty} />
    </>
  )
}
