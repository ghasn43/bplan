/* Company entity — the parent of one or more projects. */

export type CompanyStatus = 'active' | 'inactive' | 'demo'

export interface Company {
  id: string
  company_name: string
  trading_name?: string | null
  legal_name?: string | null
  industry_sector?: string | null
  business_description?: string | null
  country?: string | null
  city?: string | null
  website?: string | null
  logo_path?: string | null
  status: CompanyStatus
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface CompanySummary {
  id: string
  company_name: string
  industry_sector?: string | null
  country?: string | null
  city?: string | null
  business_description?: string | null
  status: CompanyStatus
  total_projects: number
  active_projects: number
  draft_projects: number
  profile_completion_percent: number
  created_at: string
  updated_at: string
}

export interface CompanyUpdate {
  company_name?: string
  trading_name?: string | null
  legal_name?: string | null
  industry_sector?: string | null
  business_description?: string | null
  country?: string | null
  city?: string | null
  website?: string | null
  status?: CompanyStatus
  notes?: string | null
}
