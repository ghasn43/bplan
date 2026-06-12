/* IFRS-style financial-statement number formatting.
 *  - thousands separators
 *  - negatives in parentheses: (350,000)
 *  - zero shown as an en-dash: –
 *  - percentages to one decimal place
 */

export function formatStatementNumber(value: number | null | undefined, decimals = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  const rounded = Number(value.toFixed(decimals))
  if (rounded === 0) return '–'
  const abs = Math.abs(rounded).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
  return rounded < 0 ? `(${abs})` : abs
}

/** Currency value in statement style: "AED 1,250,000", negatives as
 *  "(AED 1,187,395)", zero as an en-dash. Always renders on a single token. */
export function formatStatementCurrency(
  value: number | null | undefined,
  currency: string,
  decimals = 0,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  const rounded = Number(value.toFixed(decimals))
  if (rounded === 0) return '–'
  const abs = Math.abs(rounded).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
  const body = `${currency} ${abs}` // non-breaking space keeps code + number together
  return rounded < 0 ? `(${body})` : body
}

export function formatStatementPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  const rounded = Number(value.toFixed(1))
  const abs = Math.abs(rounded).toLocaleString('en-US', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })
  return rounded < 0 ? `(${abs}%)` : `${abs}%`
}

/** True when a number should be rendered in the "negative" visual style. */
export function isNegative(value: number | null | undefined): boolean {
  return typeof value === 'number' && Number(value.toFixed(0)) < 0
}

/** Compact money: "AED 1.2M", negatives as "(AED 350K)", zero as en-dash. */
export function formatCompactCurrency(value: number | null | undefined, currency: string): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  if (Math.round(value) === 0) return '–'
  const abs = Math.abs(value)
  let body: string
  if (abs >= 1_000_000_000) body = `${(abs / 1_000_000_000).toFixed(1)}B`
  else if (abs >= 1_000_000) body = `${(abs / 1_000_000).toFixed(1)}M`
  else if (abs >= 1_000) body = `${(abs / 1_000).toFixed(abs >= 100_000 ? 0 : 1)}K`
  else body = abs.toFixed(0)
  const out = `${currency} ${body}`
  return value < 0 ? `(${out})` : out
}

/** Ratio: "1.4x", negatives as "(0.8x)", zero/null as en-dash. */
export function formatRatio(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  const abs = Math.abs(value).toFixed(2)
  return value < 0 ? `(${abs}x)` : `${abs}x`
}

/** Format a value by its declared series/KPI format. */
export function formatByKind(
  value: number | null | undefined,
  kind: string,
  currency: string,
  compact = false,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '–'
  if (kind === 'percent') return formatStatementPercent(value)
  if (kind === 'ratio') return formatRatio(value)
  if (kind === 'number') return formatStatementNumber(value)
  return compact ? formatCompactCurrency(value, currency) : formatStatementCurrency(value, currency)
}
