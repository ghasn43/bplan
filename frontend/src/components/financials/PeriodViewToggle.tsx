import type { ViewKey } from '@/types/incomeStatement'

export function PeriodViewToggle({
  value,
  onChange,
}: {
  value: ViewKey
  onChange: (v: ViewKey) => void
}) {
  return (
    <div className="field" style={{ minWidth: 0 }}>
      <span className="field__label">Period view</span>
      <div className="segmented">
        <button
          type="button"
          className={`segmented__btn${value === 'yearly' ? ' segmented__btn--active' : ''}`}
          onClick={() => onChange('yearly')}
        >
          Annual
        </button>
        <button
          type="button"
          className={`segmented__btn${value === 'monthly' ? ' segmented__btn--active' : ''}`}
          onClick={() => onChange('monthly')}
        >
          Monthly
        </button>
      </div>
    </div>
  )
}
