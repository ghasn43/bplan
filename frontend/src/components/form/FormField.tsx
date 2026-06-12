import type { ReactNode } from 'react'
import { TooltipInfo } from '@/components/ui/Tooltip'

/** Label + tooltip + error/hint wrapper shared by every input. */
export function FormField({
  label,
  htmlFor,
  required,
  help,
  hint,
  error,
  span = 1,
  children,
}: {
  label: string
  htmlFor?: string
  required?: boolean
  help?: string
  hint?: string
  error?: string
  span?: 1 | 2
  children: ReactNode
}) {
  return (
    <div className={`field field--span-${span}`}>
      <label className="field__label" htmlFor={htmlFor}>
        {label}
        {required && <span className="field__required">*</span>}
        {help && <TooltipInfo text={help} />}
      </label>
      <div className="field__control">{children}</div>
      {error ? (
        <span className="field__error">⚠ {error}</span>
      ) : (
        hint && <span className="field__hint">{hint}</span>
      )}
    </div>
  )
}
