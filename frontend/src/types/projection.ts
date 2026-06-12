/* Types mirroring backend/app/schemas/projection.py */

export type ProjectionMode = 'monthly' | 'annual'
export type ProjectionSection = 'revenue' | 'direct_costs' | 'operating_expenses'

export interface ProjectionPeriod {
  id: string
  period_index: number
  period_label: string
  period_type: ProjectionMode
  start_date: string
  end_date: string
  fiscal_year: number
  projection_year: number
  month_number: number | null
  quarter_number: number | null
}

export interface GridCell {
  period_index: number
  quantity?: number | null
  amount?: number | null
  price_override?: number | null
  discount_override?: number | null
  refund_override?: number | null
  quantity_driver?: number | null
  amount_override?: number | null
  percentage_override?: number | null
  manual_cost_amount?: number | null
  active: boolean
  notes?: string | null
  value: number
  gross?: number | null
  discount_amount?: number | null
  refund_amount?: number | null
}

export interface GridRow {
  item_id: string
  label: string
  group?: string | null
  note?: string | null
  cells: GridCell[]
  total: number
}

export interface ProjectionGrid {
  project_id: string
  section: ProjectionSection
  mode: ProjectionMode
  currency: string
  periods: ProjectionPeriod[]
  rows: GridRow[]
  totals_by_period: number[]
  grand_total: number
  warnings: string[]
}

export interface CellPatch {
  item_id: string
  period_index: number
  quantity?: number | null
  amount?: number | null
  manual_cost_amount?: number | null
  amount_override?: number | null
  active?: boolean | null
}

/** Which editable field a section's primary cell value maps to. */
export const PRIMARY_FIELD: Record<ProjectionSection, 'quantity' | 'amount' | 'manual_cost_amount'> = {
  revenue: 'quantity',
  operating_expenses: 'amount',
  direct_costs: 'manual_cost_amount',
}
