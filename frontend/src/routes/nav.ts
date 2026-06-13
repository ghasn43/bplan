/* Central navigation model — drives the sidebar, step navigation, and
   maps each page to its completion-report section key. */

export interface NavPage {
  /** Route segment under /projects/:projectId/ */
  slug: string
  /** Display label in the sidebar */
  label: string
  /** Short page subtitle */
  subtitle: string
  /** Completion-report section key (null = no tracked section, e.g. review) */
  sectionKey: string | null
  group:
    | 'Foundation'
    | 'Revenue & Costs'
    | 'People & Operations'
    | 'Capital & Compliance'
    | 'Planning'
    | 'Written Plan'
    | 'Financial Statements'
    | 'Reporting'
  icon: string
}

export const NAV_PAGES: NavPage[] = [
  { slug: 'setup', label: 'Project Setup', subtitle: 'Business identity and projection structure', sectionKey: 'setup', group: 'Foundation', icon: '◧' },
  { slug: 'products', label: 'Products & Services', subtitle: 'Define what the company sells', sectionKey: 'products', group: 'Revenue & Costs', icon: '◫' },
  { slug: 'revenue', label: 'Revenue Assumptions', subtitle: 'How revenue is forecast per product', sectionKey: 'revenue', group: 'Revenue & Costs', icon: '◴' },
  { slug: 'direct-costs', label: 'Direct Costs / COGS', subtitle: 'Costs tied directly to delivery', sectionKey: 'direct-costs', group: 'Revenue & Costs', icon: '◵' },
  { slug: 'staffing', label: 'Staffing Plan', subtitle: 'Team, salaries, and hiring schedule', sectionKey: 'staffing', group: 'People & Operations', icon: '◶' },
  { slug: 'operating-expenses', label: 'Operating Expenses', subtitle: 'Recurring running costs', sectionKey: 'operating-expenses', group: 'People & Operations', icon: '◷' },
  { slug: 'startup-costs', label: 'Startup Costs', subtitle: 'Pre-opening and launch costs', sectionKey: 'startup-costs', group: 'Capital & Compliance', icon: '◰' },
  { slug: 'fixed-assets', label: 'Fixed Assets / CapEx', subtitle: 'Fixed assets and depreciation schedule', sectionKey: 'fixed-assets', group: 'Capital & Compliance', icon: '◱' },
  { slug: 'working-capital', label: 'Working Capital', subtitle: 'Cash conversion cycle assumptions', sectionKey: 'working-capital', group: 'Capital & Compliance', icon: '◲' },
  { slug: 'financing', label: 'Financing', subtitle: 'Equity, loans, and grants', sectionKey: 'financing', group: 'Capital & Compliance', icon: '◳' },
  { slug: 'tax', label: 'Tax & Regulatory', subtitle: 'Tax, VAT, and compliance settings', sectionKey: 'tax', group: 'Capital & Compliance', icon: '⊞' },
  { slug: 'scenarios', label: 'Scenarios', subtitle: 'Base, conservative, and optimistic cases', sectionKey: 'scenarios', group: 'Planning', icon: '⊟' },
  { slug: 'kpis', label: 'KPIs & Targets', subtitle: 'Management and investor metrics', sectionKey: 'kpis', group: 'Planning', icon: '⊡' },
  { slug: 'review', label: 'Review & Completion', subtitle: 'Summary before generating statements', sectionKey: null, group: 'Planning', icon: '✓' },
  { slug: 'text-builder', label: 'Text Builder', subtitle: 'Write the narrative business plan', sectionKey: null, group: 'Written Plan', icon: '✎' },
  { slug: 'income-statement', label: 'Income Statement', subtitle: 'IFRS Statement of Profit or Loss', sectionKey: null, group: 'Financial Statements', icon: '∑' },
  { slug: 'balance-sheet', label: 'Balance Sheet', subtitle: 'IFRS Statement of Financial Position', sectionKey: null, group: 'Financial Statements', icon: '⚖' },
  { slug: 'cash-flow', label: 'Cash Flow Statement', subtitle: 'IFRS Statement of Cash Flows (indirect)', sectionKey: null, group: 'Financial Statements', icon: '◷' },
  { slug: 'financial-analysis', label: 'Financial Analysis', subtitle: 'Investor-grade charts & KPIs', sectionKey: null, group: 'Financial Statements', icon: '◑' },
  { slug: 'reports', label: 'Business Plan Report', subtitle: 'Generate Word / PDF investor report', sectionKey: null, group: 'Reporting', icon: '⎙' },
]

export const NAV_GROUPS = [
  'Foundation',
  'Revenue & Costs',
  'People & Operations',
  'Capital & Compliance',
  'Planning',
  'Written Plan',
  'Financial Statements',
  'Reporting',
] as const

export function pageBySlug(slug: string): NavPage | undefined {
  return NAV_PAGES.find((p) => p.slug === slug)
}

export function adjacentPages(slug: string): { prev?: NavPage; next?: NavPage } {
  const idx = NAV_PAGES.findIndex((p) => p.slug === slug)
  return {
    prev: idx > 0 ? NAV_PAGES[idx - 1] : undefined,
    next: idx >= 0 && idx < NAV_PAGES.length - 1 ? NAV_PAGES[idx + 1] : undefined,
  }
}
