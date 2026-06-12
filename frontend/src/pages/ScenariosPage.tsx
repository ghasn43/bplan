import { useEffect, useState } from 'react'
import { PageHeader } from '@/components/PageHeader'
import { SaveBar } from '@/components/SaveBar'
import { SectionCard } from '@/components/SectionCard'
import { LoadingScreen } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { TooltipInfo } from '@/components/ui/Tooltip'
import {
  useCollectionSection,
  useSaveCollectionItem,
} from '@/api/hooks'
import { useProjectContext } from '@/layouts/ProjectContext'
import { useToast } from '@/components/ui/Toast'
import { scenarioTypeOptions } from '@/utils/options'
import type { ScenarioAssumption, ScenarioType } from '@/types'

const ADJUSTMENTS: { key: keyof ScenarioAssumption; label: string; help?: string }[] = [
  { key: 'sales_volume_adjustment', label: 'Sales Volume' },
  { key: 'selling_price_adjustment', label: 'Selling Price' },
  { key: 'direct_cost_adjustment', label: 'Direct Costs' },
  { key: 'salary_adjustment', label: 'Salaries' },
  { key: 'rent_adjustment', label: 'Rent' },
  { key: 'marketing_adjustment', label: 'Marketing' },
  { key: 'customer_growth_adjustment', label: 'Customer Growth' },
  { key: 'collection_days_adjustment', label: 'Collection Days' },
  { key: 'inventory_days_adjustment', label: 'Inventory Days' },
  { key: 'interest_rate_adjustment', label: 'Interest Rate' },
  { key: 'exchange_rate_adjustment', label: 'Exchange Rate' },
  { key: 'tax_rate_adjustment', label: 'Tax Rate' },
  { key: 'inflation_adjustment', label: 'Inflation' },
]

const EXTREME = 50

function emptyAdjustments(): Record<string, number> {
  return Object.fromEntries(ADJUSTMENTS.map((a) => [a.key, 0]))
}

export function ScenariosPage() {
  const { projectId } = useProjectContext()
  const { data, isLoading } = useCollectionSection<ScenarioAssumption>(projectId, 'scenarios')
  const save = useSaveCollectionItem(projectId, 'scenarios')
  const { notify } = useToast()

  const [activeType, setActiveType] = useState<ScenarioType>('base')
  const [draft, setDraft] = useState<Record<string, number>>(emptyAdjustments())
  const [dirty, setDirty] = useState(false)

  const scenarios = data ?? []
  const current = scenarios.find((s) => s.scenario_type === activeType)
  const baseScenario = scenarios.find((s) => s.scenario_type === 'base')

  useEffect(() => {
    if (current) {
      setDraft(Object.fromEntries(ADJUSTMENTS.map((a) => [a.key, Number(current[a.key]) || 0])))
    } else {
      setDraft(emptyAdjustments())
    }
    setDirty(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeType, data])

  if (isLoading) return <LoadingScreen />

  const setVal = (key: string, value: number) => {
    setDraft((d) => ({ ...d, [key]: value }))
    setDirty(true)
  }

  const handleSave = () => {
    const payload = {
      ...(current ?? {}),
      scenario_type: activeType,
      label: current?.label ?? scenarioTypeOptions.find((o) => o.value === activeType)?.label,
      ...draft,
    }
    save.mutate(payload as Partial<ScenarioAssumption> as ScenarioAssumption, {
      onSuccess: () => {
        notify('Scenario saved')
        setDirty(false)
      },
      onError: (e) => notify((e as Error).message || 'Save failed', 'error'),
    })
  }

  const duplicateBase = () => {
    if (!baseScenario) return
    setDraft(Object.fromEntries(ADJUSTMENTS.map((a) => [a.key, Number(baseScenario[a.key]) || 0])))
    setDirty(true)
  }
  const resetScenario = () => {
    setDraft(emptyAdjustments())
    setDirty(true)
  }

  const extremeCount = Object.values(draft).filter((v) => Math.abs(v) >= EXTREME).length

  return (
    <>
      <PageHeader
        breadcrumb="Business Plan · Planning"
        title="Scenario Assumptions"
        subtitle="Model Base, Conservative, and Optimistic cases as percentage adjustments over the base plan."
      />

      <div className="tabs">
        {scenarioTypeOptions.map((opt) => {
          const exists = scenarios.some((s) => s.scenario_type === opt.value)
          return (
            <button
              key={opt.value}
              className={`tab${activeType === opt.value ? ' tab--active' : ''}`}
              onClick={() => setActiveType(opt.value)}
            >
              {opt.label}
              {exists && <span style={{ marginLeft: 8, color: 'var(--emerald-500)' }}>•</span>}
            </button>
          )
        })}
      </div>

      <div className="stack">
        <SectionCard
          title={`${scenarioTypeOptions.find((o) => o.value === activeType)?.label} Adjustments`}
          subtitle="Drag a slider to set each adjustment. 0% = same as base. Negative reduces; positive increases."
          icon="⊟"
          actions={
            <>
              {activeType !== 'base' && baseScenario && (
                <button className="btn btn--ghost btn--sm" onClick={duplicateBase}>
                  Copy from Base
                </button>
              )}
              <button className="btn btn--ghost btn--sm" onClick={resetScenario}>
                Reset
              </button>
            </>
          }
        >
          {extremeCount > 0 && (
            <div className="badge badge--amber" style={{ marginBottom: 16 }}>
              ⚠ {extremeCount} extreme assumption{extremeCount === 1 ? '' : 's'} (±{EXTREME}% or more)
            </div>
          )}
          <div className="form-grid">
            {ADJUSTMENTS.map((a) => {
              const value = draft[a.key as string] ?? 0
              const extreme = Math.abs(value) >= EXTREME
              return (
                <div className="field" key={a.key as string}>
                  <label className="field__label">
                    {a.label}
                    {a.help && <TooltipInfo text={a.help} />}
                    <span style={{ marginLeft: 'auto', fontWeight: 700, color: extreme ? 'var(--amber-600)' : 'var(--text-primary)' }}>
                      {value > 0 ? '+' : ''}
                      {value}%
                    </span>
                  </label>
                  <div className="slider-row">
                    <input
                      className="slider"
                      type="range"
                      min={-100}
                      max={100}
                      step={1}
                      value={value}
                      onChange={(e) => setVal(a.key as string, Number(e.target.value))}
                    />
                    <input
                      className="input"
                      type="number"
                      value={value}
                      onChange={(e) => setVal(a.key as string, Number(e.target.value) || 0)}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </SectionCard>

        {scenarios.length > 0 && (
          <SectionCard title="Scenario Comparison" subtitle="All saved scenarios side by side." icon="⊡">
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Adjustment</th>
                    {scenarios.map((s) => (
                      <th key={s.id} style={{ textAlign: 'right' }}>
                        {s.label || s.scenario_type}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ADJUSTMENTS.map((a) => (
                    <tr key={a.key as string}>
                      <td>{a.label}</td>
                      {scenarios.map((s) => {
                        const v = Number(s[a.key]) || 0
                        return (
                          <td key={s.id} className="table__num">
                            {v === 0 ? (
                              <span className="muted">—</span>
                            ) : (
                              <Badge tone={v > 0 ? 'green' : 'amber'}>
                                {v > 0 ? '+' : ''}
                                {v}%
                              </Badge>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>
        )}
      </div>

      <SaveBar slug="scenarios" onSave={handleSave} saving={save.isPending} dirty={dirty} />
    </>
  )
}
