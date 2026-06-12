/* Business plan report generator API hooks. */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { ReportFile, ReportPreview, ReportRequest, ReportStyle, ReportView } from '@/types/reports'
import type { ScenarioKey } from '@/types/incomeStatement'

const base = (projectId: string) => `/projects/${projectId}/reports`

export function useReportPreview(
  projectId: string | undefined,
  scenario: ScenarioKey,
  view: ReportView,
  style: ReportStyle,
) {
  return useQuery({
    queryKey: ['report-preview', projectId, scenario, view, style],
    queryFn: () =>
      api.get<ReportPreview>(
        `${base(projectId!)}/business-plan/preview?scenario=${scenario}&view=${view}&report_style=${style}`,
      ),
    enabled: !!projectId,
    retry: 1,
  })
}

export function useGeneratedReports(projectId: string | undefined) {
  return useQuery({
    queryKey: ['reports', projectId],
    queryFn: () => api.get<ReportFile[]>(base(projectId!)),
    enabled: !!projectId,
  })
}

export function useGenerateReport(projectId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (request: ReportRequest) => {
      const path =
        request.output_format === 'pdf'
          ? `${base(projectId!)}/business-plan/generate-pdf`
          : `${base(projectId!)}/business-plan/generate-word`
      return api.post<ReportFile>(path, request)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reports', projectId] }),
  })
}

export function useDeleteReport(projectId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (reportId: string) => api.delete<void>(`${base(projectId!)}/${reportId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reports', projectId] }),
  })
}
