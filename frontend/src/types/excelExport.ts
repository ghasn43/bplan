/* Types mirroring backend/app/schemas/excel_export.py */
import type { ScenarioKey } from '@/types/incomeStatement'

export type ExcelScenario = ScenarioKey | 'all'
export type ProjectionDetail = 'monthly' | 'annual' | 'both'
export type WorkbookType = 'editable' | 'presentation' | 'full'

export interface ExcelExportRequest {
  scenario: ExcelScenario
  projection_detail: ProjectionDetail
  workbook_type: WorkbookType
  include_assumptions: boolean
  include_schedules: boolean
  include_statements: boolean
  include_ratios: boolean
  include_scenarios: boolean
  include_charts: boolean
  include_checks: boolean
  include_text_summary: boolean
  protect_formulas: boolean
}

export interface ExcelExportResponse {
  export_id: string
  project_id: string
  file_name: string
  file_size: number
  scenario: string
  status: string
  generated_at: string
  warnings: string[]
  message?: string | null
  download_url: string
}

export interface ExcelExportPreview {
  project_id: string
  company_name: string
  project_name: string
  currency: string
  period_range: string
  scenario: string
  scenario_label: string
  sheets: string[]
  protect_formulas: boolean
  data_ready: boolean
  can_generate: boolean
  blocking: string[]
  warnings: string[]
  estimated_size_kb: number
}
