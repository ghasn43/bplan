/* Company API hooks. */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type { Company, CompanySummary, CompanyUpdate } from '@/types/company'
import type { ProjectSummary } from '@/types'

export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: () => api.get<CompanySummary[]>('/companies'),
  })
}

export function useCompany(companyId: string | undefined | null) {
  return useQuery({
    queryKey: ['company', companyId],
    queryFn: () => api.get<Company>(`/companies/${companyId}`),
    enabled: !!companyId,
  })
}

export function useUpdateCompany() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ companyId, patch }: { companyId: string; patch: CompanyUpdate }) =>
      api.put<Company>(`/companies/${companyId}`, patch),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ['companies'] })
      qc.invalidateQueries({ queryKey: ['company', vars.companyId] })
    },
  })
}

export function useCreateCompanyProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ companyId, name }: { companyId: string; name: string }) =>
      api.post<{ id: string }>(`/companies/${companyId}/projects`, { name }),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ['companies'] })
      qc.invalidateQueries({ queryKey: ['projects'] })
      qc.invalidateQueries({ queryKey: ['company-projects', vars.companyId] })
    },
  })
}

export function useCompanyProjects(companyId: string | undefined) {
  return useQuery({
    queryKey: ['company-projects', companyId],
    queryFn: () => api.get<ProjectSummary[]>(`/companies/${companyId}/projects`),
    enabled: !!companyId,
  })
}
