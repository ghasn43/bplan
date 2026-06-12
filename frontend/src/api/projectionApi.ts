/* Projection grid API hooks. */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type {
  CellPatch,
  ProjectionGrid,
  ProjectionMode,
  ProjectionSection,
} from '@/types/projection'

const PATH: Record<ProjectionSection, string> = {
  revenue: 'revenue-projection',
  direct_costs: 'direct-cost-projection',
  operating_expenses: 'operating-expense-projection',
}

export function useProjectionGrid(
  projectId: string | undefined,
  section: ProjectionSection,
  mode: ProjectionMode,
) {
  return useQuery({
    queryKey: ['projection-grid', projectId, section, mode],
    queryFn: () => api.get<ProjectionGrid>(`/projects/${projectId}/${PATH[section]}?mode=${mode}`),
    enabled: !!projectId,
    // The Vite dev proxy can intermittently reset the connection (ECONNRESET);
    // retry a few times before surfacing an error.
    retry: 3,
    retryDelay: (attempt) => Math.min(400 * 2 ** attempt, 2000),
  })
}

function useGridMutation(projectId: string, section: ProjectionSection) {
  const qc = useQueryClient()
  return (fn: () => Promise<ProjectionGrid>) =>
    fn().then((grid) => {
      qc.setQueryData(['projection-grid', projectId, section, grid.mode], grid)
      qc.invalidateQueries({ queryKey: ['income-statement', projectId] })
      qc.invalidateQueries({ queryKey: ['income-statement-summary', projectId] })
      return grid
    })
}

export function useSaveCells(projectId: string, section: ProjectionSection) {
  const run = useGridMutation(projectId, section)
  return useMutation({
    mutationFn: ({ mode, cells }: { mode: ProjectionMode; cells: CellPatch[] }) =>
      run(() => api.put<ProjectionGrid>(`/projects/${projectId}/${PATH[section]}/bulk`, { mode, cells })),
  })
}

export function useFillRight(projectId: string, section: ProjectionSection) {
  const run = useGridMutation(projectId, section)
  return useMutation({
    mutationFn: ({ mode, itemId, fromIndex }: { mode: ProjectionMode; itemId: string; fromIndex: number }) =>
      run(() =>
        api.post<ProjectionGrid>(`/projects/${projectId}/${PATH[section]}/fill-right`, {
          mode,
          item_id: itemId,
          from_index: fromIndex,
        }),
      ),
  })
}

export function useApplyGrowth(projectId: string, section: ProjectionSection) {
  const run = useGridMutation(projectId, section)
  const endpoint = section === 'revenue' ? 'apply-growth' : 'apply-inflation'
  return useMutation({
    mutationFn: (body: {
      mode: ProjectionMode
      item_id?: string | null
      base_value?: number | null
      growth_percent: number
      start_index?: number
    }) => run(() => api.post<ProjectionGrid>(`/projects/${projectId}/${PATH[section]}/${endpoint}`, body)),
  })
}
