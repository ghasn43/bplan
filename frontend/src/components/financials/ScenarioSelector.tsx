import type { ScenarioKey } from '@/types/incomeStatement'

const OPTIONS: { value: ScenarioKey; label: string }[] = [
  { value: 'base', label: 'Base Case' },
  { value: 'conservative', label: 'Conservative' },
  { value: 'optimistic', label: 'Optimistic' },
]

export function ScenarioSelector({
  value,
  onChange,
}: {
  value: ScenarioKey
  onChange: (v: ScenarioKey) => void
}) {
  return (
    <div className="field" style={{ minWidth: 0 }}>
      <span className="field__label">Scenario</span>
      <div className="segmented">
        {OPTIONS.map((o) => (
          <button
            key={o.value}
            type="button"
            className={`segmented__btn${value === o.value ? ' segmented__btn--active' : ''}`}
            onClick={() => onChange(o.value)}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}
