/* Income statement API hooks. */
import { useQuery } from '@tanstack/react-query'
import { api } from './client'
import type {
  IncomeStatement,
  IncomeStatementReconciliation,
  IncomeStatementSummary,
  ScenarioKey,
  ViewKey,
} from '@/types/incomeStatement'

export function useIncomeStatement(
  projectId: string | undefined,
  scenario: ScenarioKey,
  view: ViewKey,
) {
  return useQuery({
    queryKey: ['income-statement', projectId, scenario, view],
    queryFn: () =>
      api.get<IncomeStatement>(
        `/projects/${projectId}/income-statement?scenario=${scenario}&view=${view}`,
      ),
    enabled: !!projectId,
  })
}

export function useIncomeStatementSummary(projectId: string | undefined, scenario: ScenarioKey) {
  return useQuery({
    queryKey: ['income-statement-summary', projectId, scenario],
    queryFn: () =>
      api.get<IncomeStatementSummary>(
        `/projects/${projectId}/income-statement/summary?scenario=${scenario}`,
      ),
    enabled: !!projectId,
  })
}

export function useIncomeStatementReconciliation(projectId: string | undefined, scenario: ScenarioKey) {
  return useQuery({
    queryKey: ['income-statement-recon', projectId, scenario],
    queryFn: () =>
      api.get<IncomeStatementReconciliation>(
        `/projects/${projectId}/income-statement/reconciliation?scenario=${scenario}`,
      ),
    enabled: !!projectId,
  })
}
