/* Types mirroring backend/app/schemas/reports.py */
import type { ScenarioKey } from '@/types/incomeStatement'

export type ReportView = 'yearly' | 'monthly'
export type ReportStyle = 'investor' | 'bank' | 'board' | 'management' | 'full'
export type ReportFormat = 'docx' | 'pdf' | 'html'
export type ReportSeverity = 'info' | 'warning' | 'critical'

export interface ReportRequest {
  scenario: ScenarioKey
  view: ReportView
  report_style: ReportStyle
  include_charts: boolean
  include_appendices: boolean
  include_assumptions: boolean
  include_warnings: boolean
  output_format: 'docx' | 'pdf'
  include_text_plan: boolean
  text_plan_include_completed: boolean
  text_plan_include_drafts: boolean
  text_plan_include_images: boolean
  text_plan_include_guidance: boolean
}

export interface ReportWarning {
  code: string
  severity: ReportSeverity
  message: string
}

export interface ReportSectionInfo {
  key: string
  title: string
  available: boolean
}

export interface ReportHighlight {
  label: string
  value: string
}

export interface ReportPreview {
  project_id: string
  title: string
  company: string
  project_name?: string | null
  scenario: ScenarioKey
  scenario_label: string
  view: ReportView
  currency: string
  period_range: string
  prepared_date: string
  prepared_for: string
  sections: ReportSectionInfo[]
  completion_percent: number
  data_ready: boolean
  can_generate: boolean
  blocking: string[]
  warnings: ReportWarning[]
  highlights: ReportHighlight[]
}

export interface ReportFile {
  report_id: string
  file_name: string
  format: ReportFormat
  scenario: string
  view: string
  report_style: string
  status: string
  size_bytes: number
  created_at: string
  download_url: string
  message?: string | null
}
