import type { ReactNode } from 'react'

export interface Column<T> {
  header: string
  cell: (row: T) => ReactNode
  align?: 'left' | 'right'
  width?: string
}

export function DataTable<T extends { id: string }>({
  columns,
  rows,
  onEdit,
  onDelete,
}: {
  columns: Column<T>[]
  rows: T[]
  onEdit?: (row: T) => void
  onDelete?: (row: T) => void
}) {
  const hasActions = !!onEdit || !!onDelete
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((c, i) => (
              <th key={i} style={{ textAlign: c.align ?? 'left', width: c.width }}>
                {c.header}
              </th>
            ))}
            {hasActions && <th style={{ textAlign: 'right', width: 96 }}>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((c, i) => (
                <td key={i} className={c.align === 'right' ? 'table__num' : undefined}>
                  {c.cell(row)}
                </td>
              ))}
              {hasActions && (
                <td>
                  <div className="table__actions">
                    {onEdit && (
                      <button className="icon-btn" onClick={() => onEdit(row)} aria-label="Edit" title="Edit">
                        ✎
                      </button>
                    )}
                    {onDelete && (
                      <button
                        className="icon-btn icon-btn--danger"
                        onClick={() => onDelete(row)}
                        aria-label="Delete"
                        title="Delete"
                      >
                        🗑
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
