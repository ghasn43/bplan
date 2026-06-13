/* Excel financial model export API hooks. */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { ExcelExportPreview, ExcelExportRequest, ExcelExportResponse } from '@/types/excelExport'

const base = (projectId: string) => `/projects/${projectId}/exports`

export function useExcelPreview(projectId: string | undefined, scenario: string, protect: boolean) {
  return useQuery({
    queryKey: ['excel-preview', projectId, scenario, protect],
    queryFn: () =>
      api.get<ExcelExportPreview>(
        `${base(projectId!)}/excel-financial-model/preview?scenario=${scenario}&protect_formulas=${protect}`,
      ),
    enabled: !!projectId,
    retry: 1,
  })
}

export function useExcelExports(projectId: string | undefined) {
  return useQuery({
    queryKey: ['excel-exports', projectId],
    queryFn: () => api.get<ExcelExportResponse[]>(base(projectId!)),
    enabled: !!projectId,
  })
}

export function useGenerateExcel(projectId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (request: ExcelExportRequest) =>
      api.post<ExcelExportResponse>(`${base(projectId!)}/excel-financial-model`, request),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['excel-exports', projectId] }),
  })
}

export function useDeleteExcel(projectId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (exportId: string) => api.delete<void>(`${base(projectId!)}/${exportId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['excel-exports', projectId] }),
  })
}
