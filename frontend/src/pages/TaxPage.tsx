import { SingletonFormPage } from '@/components/pages/SingletonFormPage'
import type { FormConfig } from '@/components/form/types'
import type { TaxAssumption } from '@/types'
import { taxFrequencyOptions } from '@/utils/options'

const config: FormConfig = [
  {
    title: 'Corporate Tax',
    icon: '⊞',
    fields: [
      { name: 'corporate_tax_enabled', label: 'Corporate Tax Applies', kind: 'switch' },
      { name: 'corporate_tax_rate', label: 'Corporate Tax Rate', kind: 'percent', visibleWhen: (v) => v.corporate_tax_enabled !== false },
      { name: 'tax_payment_frequency', label: 'Tax Payment Frequency', kind: 'select', options: taxFrequencyOptions, visibleWhen: (v) => v.corporate_tax_enabled !== false },
      { name: 'tax_loss_carryforward_enabled', label: 'Tax Loss Carryforward', kind: 'switch', help: 'Allow losses to offset future taxable profits.' },
      { name: 'withholding_tax_rate', label: 'Withholding Tax Rate', kind: 'percent' },
      { name: 'zakat_rate', label: 'Zakat Rate (optional)', kind: 'percent' },
    ],
  },
  {
    title: 'VAT / Sales Tax',
    icon: '◷',
    fields: [
      { name: 'vat_enabled', label: 'VAT / Sales Tax Applies', kind: 'switch' },
      { name: 'vat_rate', label: 'VAT / Sales Tax Rate', kind: 'percent', visibleWhen: (v) => v.vat_enabled !== false },
      { name: 'vat_registration_threshold', label: 'VAT Registration Threshold', kind: 'currency', visibleWhen: (v) => v.vat_enabled !== false, help: 'Revenue level above which VAT registration is required.' },
      { name: 'vat_payment_frequency', label: 'VAT Payment Frequency', kind: 'select', options: taxFrequencyOptions, visibleWhen: (v) => v.vat_enabled !== false },
    ],
  },
  {
    title: 'Duties & Regulatory Fees',
    advanced: true,
    fields: [
      { name: 'customs_duty_rate', label: 'Customs Duty Rate', kind: 'percent' },
      { name: 'municipality_fees', label: 'Municipality Fees', kind: 'currency' },
      { name: 'license_renewal_fees', label: 'License Renewal Fees', kind: 'currency' },
    ],
  },
  {
    title: 'Payroll Compliance',
    advanced: true,
    fields: [
      { name: 'employer_social_security_rate', label: 'Employer Social Security %', kind: 'percent' },
      { name: 'employee_social_security_rate', label: 'Employee Social Security %', kind: 'percent' },
    ],
  },
]

export function TaxPage() {
  return <SingletonFormPage<TaxAssumption> slug="tax" sectionKey="tax" config={config} />
}
