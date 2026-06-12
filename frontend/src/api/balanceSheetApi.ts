/* Balance Sheet API hooks. */
import { useQuery } from '@tanstack/react-query'
import { api } from './client'
import type {
  BalanceSheet,
  BalanceSheetReconciliation,
  BalanceSheetSummary,
  BSView,
  CashBridge,
  ScenarioKey,
} from '@/types/balanceSheet'

export function useBalanceSheet(projectId: string | undefined, scenario: ScenarioKey, view: BSView) {
  return useQuery({
    queryKey: ['balance-sheet', projectId, scenario, view],
    queryFn: () => api.get<BalanceSheet>(`/projects/${projectId}/balance-sheet?scenario=${scenario}&view=${view}`),
    enabled: !!projectId,
    retry: 2,
  })
}

export function useBalanceSheetSummary(projectId: string | undefined, scenario: ScenarioKey) {
  return useQuery({
    queryKey: ['balance-sheet-summary', projectId, scenario],
    queryFn: () => api.get<BalanceSheetSummary>(`/projects/${projectId}/balance-sheet/summary?scenario=${scenario}`),
    enabled: !!projectId,
  })
}

export function useBalanceSheetReconciliation(projectId: string | undefined, scenario: ScenarioKey) {
  return useQuery({
    queryKey: ['balance-sheet-recon', projectId, scenario],
    queryFn: () =>
      api.get<BalanceSheetReconciliation>(`/projects/${projectId}/balance-sheet/reconciliation?scenario=${scenario}`),
    enabled: !!projectId,
  })
}

export function useCashBridge(projectId: string | undefined, scenario: ScenarioKey, enabled: boolean) {
  return useQuery({
    queryKey: ['cash-bridge', projectId, scenario],
    queryFn: () => api.get<CashBridge>(`/projects/${projectId}/balance-sheet/drilldown/cash?scenario=${scenario}&view=yearly`),
    enabled: !!projectId && enabled,
  })
}
