/* Cash Flow Statement API hooks. */
import { useQuery } from '@tanstack/react-query'
import { api } from './client'
import type {
  CashFlowReconciliation,
  CashFlowStatement,
  CashFlowSummary,
  CFView,
  ScenarioKey,
} from '@/types/cashFlow'

export function useCashFlow(projectId: string | undefined, scenario: ScenarioKey, view: CFView) {
  return useQuery({
    queryKey: ['cash-flow', projectId, scenario, view],
    queryFn: () => api.get<CashFlowStatement>(`/projects/${projectId}/cash-flow?scenario=${scenario}&view=${view}&method=indirect`),
    enabled: !!projectId,
    retry: 2,
  })
}

export function useCashFlowSummary(projectId: string | undefined, scenario: ScenarioKey) {
  return useQuery({
    queryKey: ['cash-flow-summary', projectId, scenario],
    queryFn: () => api.get<CashFlowSummary>(`/projects/${projectId}/cash-flow/summary?scenario=${scenario}`),
    enabled: !!projectId,
  })
}

export function useCashFlowReconciliation(projectId: string | undefined, scenario: ScenarioKey) {
  return useQuery({
    queryKey: ['cash-flow-recon', projectId, scenario],
    queryFn: () => api.get<CashFlowReconciliation>(`/projects/${projectId}/cash-flow/reconciliation?scenario=${scenario}`),
    enabled: !!projectId,
  })
}
