import { useState } from 'react'
import { PageHeader } from '@/components/PageHeader'
import { SectionCard } from '@/components/SectionCard'
import { LoadingScreen } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useProjectContext } from '@/layouts/ProjectContext'
import { useFinancialAnalysis, useScenarioComparison } from '@/api/financialAnalysisApi'
import type { FAView, ScenarioKey } from '@/types/financialAnalysis'
import { AnalysisControls } from '@/components/analysis/AnalysisControls'
import { AnalysisKpiCards } from '@/components/analysis/AnalysisKpiCards'
import { AnalysisWarningBanner } from '@/components/analysis/AnalysisWarningBanner'
import { FinancialInsightsPanel } from '@/components/analysis/FinancialInsightsPanel'
import { ChartCard } from '@/components/analysis/ChartCard'
import { ScenarioComparisonChart } from '@/components/analysis/ScenarioComparisonChart'

export function FinancialAnalysisPage() {
  const { projectId } = useProjectContext()
  const [scenario, setScenario] = useState<ScenarioKey>('base')
  const [view, setView] = useState<FAView>('yearly')
  const [section, setSection] = useState('overview')

  const faQ = useFinancialAnalysis(projectId, scenario, view)
  const scenarioMode = section === 'scenarios'
  const scQ = useScenarioComparison(projectId, view)

  const currency = faQ.data?.metadata.currency ?? 'USD'
  const activeSection = faQ.data?.sections.find((s) => s.key === section)

  return (
    <>
      <PageHeader
        breadcrumb="Financial Statements"
        title="Financial Analysis"
        subtitle="Investor-grade visual analysis generated from the projected financial statements."
      />

      <div className="stack">
        <AnalysisControls
          scenario={scenario} onScenario={setScenario}
          view={view} onView={setView}
          section={section} onSection={setSection}
          projectId={projectId}
        />

        {faQ.isLoading ? (
          <LoadingScreen label="Building the financial analysis…" />
        ) : faQ.isError || !faQ.data ? (
          <SectionCard>
            <EmptyState icon="⚠" title="Could not generate the analysis"
              description={(faQ.error as Error)?.message ?? 'Ensure assumptions and statements are available.'} />
          </SectionCard>
        ) : (
          <>
            <AnalysisKpiCards kpis={faQ.data.kpis} currency={currency} />
            <AnalysisWarningBanner warnings={faQ.data.warnings} />

            {scenarioMode ? (
              scQ.isLoading || !scQ.data ? (
                <LoadingScreen label="Comparing scenarios…" />
              ) : (
                <div className="chart-grid">
                  {scQ.data.metrics.map((m) => (
                    <ScenarioComparisonChart key={m.key} metric={m} periods={scQ.data!.periods} currency={scQ.data!.currency} />
                  ))}
                </div>
              )
            ) : activeSection ? (
              <>
                {activeSection.description && (
                  <div className="muted" style={{ fontSize: 13.5 }}>{activeSection.description}</div>
                )}
                <div className="chart-grid">
                  {activeSection.charts.map((c) => <ChartCard key={c.key} chart={c} currency={currency} />)}
                </div>
              </>
            ) : (
              <SectionCard><EmptyState icon="◇" title="No charts in this section" /></SectionCard>
            )}

            {section === 'overview' && <FinancialInsightsPanel insights={faQ.data.insights} />}
          </>
        )}
      </div>
    </>
  )
}
