import { Fragment, useState } from 'react'
import type { IncomeStatement } from '@/types/incomeStatement'
import { StatementRow } from './LineItemDrilldown'
import { formatStatementNumber, formatStatementPercent, isNegative } from '@/utils/statementFormat'

const SECTIONS_WITH_HEADER = new Set(['revenue', 'cost_of_sales', 'other_income', 'operating_expenses', 'finance_costs'])

export function FinancialStatementTable({ statement }: { statement: IncomeStatement }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const toggle = (key: string) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })

  const periods = statement.periods
  const colCount = periods.length

  const marginRows: { label: string; values: number[]; pct: boolean }[] = [
    { label: 'Gross margin %', values: statement.margins.gross_margin_pct, pct: true },
    { label: 'EBITDA', values: statement.margins.ebitda, pct: false },
    { label: 'EBITDA margin %', values: statement.margins.ebitda_margin_pct, pct: true },
    { label: 'Operating margin %', values: statement.margins.operating_margin_pct, pct: true },
    { label: 'Net profit margin %', values: statement.margins.net_margin_pct, pct: true },
  ]

  return (
    <div className="stmt-wrap">
      <table className={`stmt ${statement.metadata.view === 'monthly' ? 'stmt--monthly' : ''}`}>
        <thead>
          <tr>
            <th className="stmt__label-head">Line item</th>
            {periods.map((p) => (
              <th key={p.index} className="stmt__num">{p.label}</th>
            ))}
            <th className="stmt__num stmt__total">Total</th>
          </tr>
        </thead>
        <tbody>
          {statement.sections.map((section) => (
            <Fragment key={section.key}>
              {SECTIONS_WITH_HEADER.has(section.key) && (
                <tr className="stmt__row stmt__row--section">
                  <td className="stmt__label" colSpan={colCount + 2}>{section.title}</td>
                </tr>
              )}
              {section.line_items.map((li) => (
                <StatementRow key={li.key} item={li} depth={SECTIONS_WITH_HEADER.has(section.key) ? 1 : 0} expanded={expanded} toggle={toggle} />
              ))}
              {section.subtotal && (
                <StatementRow item={section.subtotal} depth={0} expanded={expanded} toggle={toggle} />
              )}
            </Fragment>
          ))}

          {/* Analytical metrics */}
          <tr className="stmt__row stmt__row--analytical-head">
            <td className="stmt__label" colSpan={colCount + 2}>Analytical metrics</td>
          </tr>
          {marginRows.map((m) => (
            <tr className="stmt__row stmt__row--analytical" key={m.label}>
              <td className="stmt__label" style={{ paddingLeft: 14 }}>{m.label}</td>
              {m.values.map((v, i) => (
                <td key={i} className={`stmt__num${!m.pct && isNegative(v) ? ' stmt__num--neg' : ''}`}>
                  {m.pct ? formatStatementPercent(v) : formatStatementNumber(v)}
                </td>
              ))}
              <td className="stmt__num stmt__total">
                {m.pct
                  ? formatStatementPercent(
                      m.label.startsWith('Gross')
                        ? statement.margins.gross_margin_total_pct
                        : m.label.startsWith('EBITDA margin')
                          ? statement.margins.ebitda_margin_total_pct
                          : m.label.startsWith('Operating')
                            ? statement.margins.operating_margin_total_pct
                            : statement.margins.net_margin_total_pct,
                    )
                  : formatStatementNumber(statement.totals.ebitda)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
