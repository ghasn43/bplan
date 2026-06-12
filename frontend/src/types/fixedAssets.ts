/* Types for the fixed-asset depreciation schedule + summary. */

export interface DepreciationPeriod {
  index: number
  label: string
  period_type: 'monthly' | 'annual'
  start_date: string
  end_date: string
}

export interface DepreciationAssetRow {
  asset_id: string
  label: string
  category: string
  category_label: string
  depreciation_by_period: number[]
  total_depreciation: number
  closing_net_book_value: number
}

export interface DepreciationRollforward {
  opening_cost: number[]
  additions: number[]
  depreciation_charge: number[]
  accumulated_depreciation: number[]
  closing_net_book_value: number[]
}

export interface DepreciationSchedule {
  project_id: string
  view: 'monthly' | 'annual'
  currency: string
  periods: DepreciationPeriod[]
  assets: DepreciationAssetRow[]
  rollforward: DepreciationRollforward
  totals_by_period: number[]
  grand_total_depreciation: number
  total_closing_nbv: number
  warnings: string[]
}

export interface FixedAssetSummary {
  project_id: string
  currency: string
  total_asset_cost: number
  annual_depreciation: number
  net_book_value: number
  active_assets: number
  loan_financed_assets: number
  software_intangible_assets: number
  total_assets: number
}
