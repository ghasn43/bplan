import type { ReactNode } from 'react'

type Tone = 'neutral' | 'blue' | 'green' | 'amber' | 'red'

export function Badge({
  tone = 'neutral',
  dot = false,
  children,
}: {
  tone?: Tone
  dot?: boolean
  children: ReactNode
}) {
  return <span className={`badge badge--${tone}${dot ? ' badge--dot' : ''}`}>{children}</span>
}

export function ActiveBadge({ active }: { active: boolean }) {
  return (
    <Badge tone={active ? 'green' : 'neutral'} dot>
      {active ? 'Active' : 'Inactive'}
    </Badge>
  )
}
