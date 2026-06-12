/* Fixed-asset depreciation schedule + summary hooks.
   (CRUD uses the generic section hooks against the `fixed-assets` collection.) */
import { useQuery } from '@tanstack/react-query'
import { api } from './client'
import type { DepreciationSchedule, FixedAssetSummary } from '@/types/fixedAssets'

export function useDepreciationSchedule(projectId: string | undefined, view: 'monthly' | 'annual') {
  return useQuery({
    queryKey: ['depreciation-schedule', projectId, view],
    queryFn: () =>
      api.get<DepreciationSchedule>(`/projects/${projectId}/fixed-assets/depreciation-schedule?view=${view}`),
    enabled: !!projectId,
  })
}

export function useFixedAssetSummary(projectId: string | undefined) {
  return useQuery({
    queryKey: ['fixed-asset-summary', projectId],
    queryFn: () => api.get<FixedAssetSummary>(`/projects/${projectId}/fixed-assets/summary`),
    enabled: !!projectId,
  })
}
