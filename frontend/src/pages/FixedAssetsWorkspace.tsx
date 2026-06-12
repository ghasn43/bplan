import { useState } from 'react'
import { PageHeader } from '@/components/PageHeader'
import { SaveBar } from '@/components/SaveBar'
import { useProjectContext } from '@/layouts/ProjectContext'
import { pageBySlug } from '@/routes/nav'
import { AssetSummaryCards } from '@/components/assets/AssetSummaryCards'
import { DepreciationScheduleTable } from '@/components/assets/DepreciationScheduleTable'
import { FixedAssetsPage } from './FixedAssetsPage'

export function FixedAssetsWorkspace() {
  const { projectId } = useProjectContext()
  const page = pageBySlug('fixed-assets')
  const [tab, setTab] = useState<'register' | 'schedule'>('register')

  return (
    <>
      <PageHeader
        breadcrumb="Financial Inputs"
        title={page?.label ?? 'Fixed Assets / CapEx'}
        subtitle="Register long-term business assets and project their depreciation over the plan."
      />

      <div className="stack">
        <AssetSummaryCards projectId={projectId} />

        <div className="tabs" style={{ marginBottom: 0 }}>
          <button className={`tab${tab === 'register' ? ' tab--active' : ''}`} onClick={() => setTab('register')}>
            Asset Register
          </button>
          <button className={`tab${tab === 'schedule' ? ' tab--active' : ''}`} onClick={() => setTab('schedule')}>
            Depreciation Schedule
          </button>
        </div>

        {tab === 'register' ? (
          <FixedAssetsPage embedded />
        ) : (
          <DepreciationScheduleTable projectId={projectId} />
        )}
      </div>

      <SaveBar slug="fixed-assets" />
    </>
  )
}
