import { Fragment } from 'react'
import type { ISLineItem } from '@/types/incomeStatement'
import { formatStatementNumber, isNegative } from '@/utils/statementFormat'

function numClass(v: number): string {
  return `stmt__num${isNegative(v) ? ' stmt__num--neg' : ''}`
}

/** Renders a line-item row plus its expandable children (drill-down). */
export function StatementRow({
  item,
  depth,
  expanded,
  toggle,
}: {
  item: ISLineItem
  depth: number
  expanded: Set<string>
  toggle: (key: string) => void
}) {
  const hasChildren = item.drilldown_available && item.children.length > 0
  const isOpen = expanded.has(item.key)
  const rowClass = item.is_grand_total
    ? 'stmt__row stmt__row--grandtotal'
    : item.is_subtotal
      ? 'stmt__row stmt__row--subtotal'
      : 'stmt__row'

  return (
    <Fragment>
      <tr className={rowClass}>
        <td className="stmt__label" style={{ paddingLeft: 14 + depth * 20 }}>
          {hasChildren ? (
            <button className="stmt__toggle" onClick={() => toggle(item.key)} aria-label="Toggle details">
              <span className={`collapsible__chevron${isOpen ? ' collapsible__chevron--open' : ''}`}>▸</span>
            </button>
          ) : (
            <span className="stmt__toggle-spacer" />
          )}
          <span>{item.label}</span>
          {item.note && <span className="stmt__note">{item.note}</span>}
        </td>
        {item.values_by_period.map((v, i) => (
          <td key={i} className={numClass(v)}>{formatStatementNumber(v)}</td>
        ))}
        <td className={`${numClass(item.total)} stmt__total`}>{formatStatementNumber(item.total)}</td>
      </tr>
      {hasChildren && isOpen &&
        item.children.map((c) => (
          <StatementRow key={c.key} item={c} depth={depth + 1} expanded={expanded} toggle={toggle} />
        ))}
    </Fragment>
  )
}
