import type { ReactNode } from 'react'

export function SectionCard({
  title,
  subtitle,
  icon,
  actions,
  footer,
  children,
}: {
  title?: string
  subtitle?: string
  icon?: string
  actions?: ReactNode
  footer?: ReactNode
  children: ReactNode
}) {
  return (
    <section className="card">
      {(title || actions) && (
        <header className="card__header">
          <div className="card__header-main">
            {icon && <div className="card__icon">{icon}</div>}
            <div>
              {title && <div className="card__title">{title}</div>}
              {subtitle && <div className="card__subtitle">{subtitle}</div>}
            </div>
          </div>
          {actions && <div className="row">{actions}</div>}
        </header>
      )}
      <div className="card__body">{children}</div>
      {footer && <div className="card__footer">{footer}</div>}
    </section>
  )
}
