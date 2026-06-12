import { useEffect, useState } from 'react'
import type { Option } from '@/utils/options'
import { parseNumeric, withThousands } from '@/utils/format'

interface BaseProps {
  id?: string
  error?: boolean
  disabled?: boolean
}

const cls = (base: string, error?: boolean) => `${base}${error ? ` ${base}--error` : ''}`

// -- Text -------------------------------------------------------------------
export function TextInput({
  value,
  onChange,
  placeholder,
  id,
  error,
  disabled,
}: BaseProps & {
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <input
      id={id}
      className={cls('input', error)}
      value={value ?? ''}
      placeholder={placeholder}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

export function TextAreaInput({
  value,
  onChange,
  placeholder,
  id,
  error,
  disabled,
}: BaseProps & {
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <textarea
      id={id}
      className={cls('textarea', error)}
      value={value ?? ''}
      placeholder={placeholder}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

// -- Numeric (with visual thousands separators, stored as number) ----------
function NumericInput({
  value,
  onChange,
  placeholder,
  id,
  error,
  disabled,
  adornmentLeft,
  adornmentRight,
  allowNegative,
}: BaseProps & {
  value: number | null
  onChange: (v: number | null) => void
  placeholder?: string
  adornmentLeft?: string
  adornmentRight?: string
  allowNegative?: boolean
}) {
  // Keep a local string so the user can type intermediate states ("1," etc.).
  const [text, setText] = useState(() => (value === null || value === undefined ? '' : withThousands(String(value))))

  // Sync when the external value changes (e.g. form reset / edit).
  useEffect(() => {
    const next = value === null || value === undefined ? '' : withThousands(String(value))
    setText((prev) => (parseNumeric(prev) === value ? prev : next))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value])

  return (
    <>
      {adornmentLeft && <span className="field__adornment field__adornment--left">{adornmentLeft}</span>}
      <input
        id={id}
        inputMode="decimal"
        className={`${cls('input', error)}${adornmentLeft ? ' input--with-adornment-left' : ''}${
          adornmentRight ? ' input--with-adornment-right' : ''
        }`}
        value={text}
        placeholder={placeholder}
        disabled={disabled}
        onChange={(e) => {
          let raw = e.target.value
          if (!allowNegative) raw = raw.replace(/-/g, '')
          const formatted = withThousands(raw)
          setText(formatted)
          onChange(parseNumeric(formatted))
        }}
      />
      {adornmentRight && <span className="field__adornment field__adornment--right">{adornmentRight}</span>}
    </>
  )
}

export function NumberInput(props: BaseProps & {
  value: number | null
  onChange: (v: number | null) => void
  placeholder?: string
  unit?: string
  allowNegative?: boolean
}) {
  return <NumericInput {...props} adornmentRight={props.unit} />
}

export function CurrencyInput(props: BaseProps & {
  value: number | null
  onChange: (v: number | null) => void
  placeholder?: string
  currency: string
  allowNegative?: boolean
}) {
  return <NumericInput {...props} adornmentLeft={props.currency} />
}

export function PercentageInput(props: BaseProps & {
  value: number | null
  onChange: (v: number | null) => void
  placeholder?: string
  allowNegative?: boolean
}) {
  return <NumericInput {...props} adornmentRight="%" />
}

// -- Date -------------------------------------------------------------------
export function DateInput({
  value,
  onChange,
  id,
  error,
  disabled,
}: BaseProps & {
  value: string | null
  onChange: (v: string | null) => void
}) {
  return (
    <input
      id={id}
      type="date"
      className={cls('input', error)}
      value={value ?? ''}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value || null)}
    />
  )
}

// -- Select -----------------------------------------------------------------
export function SelectInput({
  value,
  onChange,
  options,
  id,
  error,
  disabled,
  placeholder = 'Select…',
}: BaseProps & {
  value: string | null
  onChange: (v: string | null) => void
  options: Option[]
  placeholder?: string
}) {
  return (
    <select
      id={id}
      className={cls('select', error)}
      value={value ?? ''}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value || null)}
    >
      <option value="" disabled>
        {placeholder}
      </option>
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  )
}

// -- Switch / Checkbox ------------------------------------------------------
export function Switch({
  checked,
  onChange,
  id,
  disabled,
}: {
  checked: boolean
  onChange: (v: boolean) => void
  id?: string
  disabled?: boolean
}) {
  return (
    <label className="switch">
      <input
        id={id}
        type="checkbox"
        checked={!!checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="switch__track" />
    </label>
  )
}
