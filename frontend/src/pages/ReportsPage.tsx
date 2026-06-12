import { PageHeader } from '@/components/PageHeader'
import { useProjectContext } from '@/layouts/ProjectContext'
import { ReportGeneratorPanel } from '@/components/reports/ReportGeneratorPanel'

export function ReportsPage() {
  const { projectId } = useProjectContext()
  return (
    <>
      <PageHeader
        breadcrumb="Reporting"
        title="Business Plan Report"
        subtitle="Generate a complete, investor-ready business plan document (Word or PDF) from your projections."
      />
      <ReportGeneratorPanel projectId={projectId} />
    </>
  )
}
