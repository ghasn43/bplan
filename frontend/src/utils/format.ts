/* Formatting helpers — currency, numbers, percentages, dates. */

export function formatNumber(value: number | null | undefined, fractionDigits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return value.toLocaleString('en-US', {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  })
}

export function formatCurrency(
  value: number | null | undefined,
  currency = 'USD',
  fractionDigits = 0,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: fractionDigits,
      maximumFractionDigits: fractionDigits,
    }).format(value)
  } catch {
    // Unknown ISO code — fall back to code prefix.
    return `${currency} ${formatNumber(value, fractionDigits)}`
  }
}

export function formatPercent(value: number | null | undefined, fractionDigits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return `${value.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: fractionDigits,
  })}%`
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

/** Insert thousands separators into a numeric input string (preserves decimals). */
export function withThousands(raw: string): string {
  if (raw === '' || raw === '-') return raw
  const negative = raw.startsWith('-')
  const cleaned = raw.replace(/[^0-9.]/g, '')
  const [intPart, ...rest] = cleaned.split('.')
  const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const decimal = rest.length ? `.${rest.join('')}` : ''
  return `${negative ? '-' : ''}${grouped}${decimal}`
}

/** Strip formatting back to a number (or null when empty). */
export function parseNumeric(raw: string): number | null {
  if (raw === '' || raw === '-') return null
  const n = Number(raw.replace(/,/g, ''))
  return Number.isNaN(n) ? null : n
}

export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return formatDate(iso)
}
