import type { ReactNode } from 'react'

export function PageHeader({
  breadcrumb,
  title,
  subtitle,
  actions,
}: {
  breadcrumb?: string
  title: string
  subtitle?: string
  actions?: ReactNode
}) {
  return (
    <header className="page-header">
      {breadcrumb && <div className="page-header__breadcrumb">{breadcrumb}</div>}
      <div className="page-header__row">
        <div>
          <h1 className="page-header__title">{title}</h1>
          {subtitle && <p className="page-header__subtitle">{subtitle}</p>}
        </div>
        {actions && <div className="row row--wrap">{actions}</div>}
      </div>
    </header>
  )
}
