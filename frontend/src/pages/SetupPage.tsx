import { SingletonFormPage } from '@/components/pages/SingletonFormPage'
import type { FormConfig } from '@/components/form/types'
import type { ProjectSetup } from '@/types'
import {
  businessModelOptions,
  currencyOptions,
  projectionFrequencyOptions,
  projectionPeriodOptions,
  reportingStandardOptions,
} from '@/utils/options'

const config: FormConfig = [
  {
    title: 'Business Identity',
    subtitle: 'Who the plan is for and what the business does.',
    icon: '◧',
    fields: [
      {
        name: 'business_name', label: 'Company Name', kind: 'text', required: true,
        placeholder: 'e.g. AquaPure Smart Filters FZE',
        help: 'The legal or trading name of the business (the reporting entity).',
      },
      {
        name: 'project_name', label: 'Project Name', kind: 'text', required: true,
        placeholder: 'e.g. Dubai Smart Water Filtration Expansion Plan',
        help: 'The name of this specific business plan, expansion, investment case, or financial study.',
      },
      { name: 'business_description', label: 'Business Description', kind: 'textarea', span: 2, placeholder: 'A short description of the business, its customers, and value proposition.' },
      { name: 'industry', label: 'Industry / Sector', kind: 'text', placeholder: 'e.g. Software / Fintech' },
      { name: 'business_model', label: 'Business Model', kind: 'select', options: businessModelOptions, placeholder: 'Select a model' },
      { name: 'country', label: 'Country', kind: 'text', placeholder: 'e.g. United Arab Emirates' },
      { name: 'city', label: 'City', kind: 'text', placeholder: 'e.g. Dubai' },
    ],
  },
  {
    title: 'Projection Settings',
    subtitle: 'The structure and horizon of your financial model.',
    icon: '◷',
    fields: [
      {
        name: 'currency', label: 'Reporting Currency', kind: 'select', options: currencyOptions, required: true,
        help: 'Selected once here and reused across every page and statement.',
      },
      { name: 'projection_start_date', label: 'Projection Start Date', kind: 'date', required: true },
      {
        name: 'projection_period', label: 'Projection Period', kind: 'select', options: projectionPeriodOptions, required: true,
        help: 'How many years the model will forecast. The engine supports 3, 5, or 10 years.',
      },
      {
        name: 'projection_frequency', label: 'Projection Frequency', kind: 'select', options: projectionFrequencyOptions,
        help: 'The granularity of each period — monthly gives the most detail.',
      },
    ],
  },
  {
    title: 'Reporting Preferences',
    subtitle: 'Tax context and the presentation style of outputs.',
    icon: '⊞',
    fields: [
      { name: 'tax_jurisdiction', label: 'Tax Jurisdiction', kind: 'text', placeholder: 'e.g. UAE' },
      {
        name: 'reporting_standard', label: 'Reporting Standard', kind: 'select', options: reportingStandardOptions,
        help: 'Tailors how statements are presented for the intended audience.',
      },
      {
        name: 'scenario_mode_enabled', label: 'Enable Scenario Mode', kind: 'switch', span: 2,
        help: 'Turn on to model Base, Conservative, and Optimistic cases side by side.',
      },
    ],
  },
]

export function SetupPage() {
  return (
    <SingletonFormPage<ProjectSetup>
      slug="setup"
      sectionKey="setup"
      config={config}
    />
  )
}
