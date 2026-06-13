/* React Query hooks for projects, sections, and completion/review. */
import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryResult,
} from '@tanstack/react-query'
import { api, API_BASE } from './client'
import type {
  BusinessPlanProject,
  CompletionReport,
  EntityBase,
  ProjectSummary,
  ReviewStatus,
} from '@/types'

// -- Project list / CRUD ----------------------------------------------------
export function useProjects(): UseQueryResult<ProjectSummary[]> {
  return useQuery({ queryKey: ['projects'], queryFn: () => api.get<ProjectSummary[]>('/projects') })
}

export function useProject(projectId: string | undefined) {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: () => api.get<BusinessPlanProject>(`/projects/${projectId}`),
    enabled: !!projectId,
  })
}

export function useCreateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => api.post<BusinessPlanProject>('/projects', { name }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  })
}

export function useDeleteProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (projectId: string) => api.delete<void>(`/projects/${projectId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  })
}

export function useUpdateCompanyName() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ projectId, businessName }: { projectId: string; businessName: string }) =>
      api.put(`/projects/${projectId}/company-name`, { business_name: businessName }),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      qc.invalidateQueries({ queryKey: ['project', vars.projectId] })
      qc.invalidateQueries({ queryKey: ['section', vars.projectId, 'setup'] })
    },
  })
}

export function useCompletion(projectId: string | undefined) {
  return useQuery({
    queryKey: ['completion', projectId],
    queryFn: () => api.get<CompletionReport>(`/projects/${projectId}/completion`),
    enabled: !!projectId,
  })
}

export function useReview(projectId: string | undefined) {
  return useQuery({
    queryKey: ['review', projectId],
    queryFn: () => api.get<ReviewStatus>(`/projects/${projectId}/review`),
    enabled: !!projectId,
  })
}

// Invalidate everything that depends on the document after a section write.
function invalidateProject(qc: ReturnType<typeof useQueryClient>, projectId: string) {
  qc.invalidateQueries({ queryKey: ['project', projectId] })
  qc.invalidateQueries({ queryKey: ['completion', projectId] })
  qc.invalidateQueries({ queryKey: ['review', projectId] })
  qc.invalidateQueries({ queryKey: ['section', projectId] })
  qc.invalidateQueries({ queryKey: ['projects'] })
}

// -- Singleton section (setup, working-capital, financing, tax, kpis) -------
export function useSingletonSection<T>(projectId: string | undefined, key: string) {
  return useQuery({
    queryKey: ['section', projectId, key],
    queryFn: () => api.get<T | null>(`/projects/${projectId}/${key}`),
    enabled: !!projectId,
  })
}

export function useSaveSingletonSection<T>(projectId: string, key: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: T) => api.put<T>(`/projects/${projectId}/${key}`, payload),
    onSuccess: () => invalidateProject(qc, projectId),
  })
}

// -- Collection sections ----------------------------------------------------
export function useCollectionSection<T>(projectId: string | undefined, key: string) {
  return useQuery({
    queryKey: ['section', projectId, key],
    queryFn: () => api.get<T[]>(`/projects/${projectId}/${key}`),
    enabled: !!projectId,
  })
}

export function useSaveCollectionItem<T extends Partial<EntityBase>>(
  projectId: string,
  key: string,
) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (item: T) =>
      item.id
        ? api.put<T>(`/projects/${projectId}/${key}/${item.id}`, item)
        : api.post<T>(`/projects/${projectId}/${key}`, item),
    onSuccess: () => invalidateProject(qc, projectId),
  })
}

export function useDeleteCollectionItem(projectId: string, key: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (itemId: string) => api.delete<void>(`/projects/${projectId}/${key}/${itemId}`),
    onSuccess: () => invalidateProject(qc, projectId),
  })
}

export const exportJsonUrl = (projectId: string) =>
  `${API_BASE}/projects/${projectId}/export-json`

// -- Demo company -----------------------------------------------------------
export interface DemoPreview {
  id: string
  name: string
  company_name: string
  project_name: string
  business_name: string
  subtitle: string
  description?: string
  tags: string[]
  currency: string
  projection_period: string | null
  already_loaded: boolean
  completion_percent: number
  metrics: Record<string, number>
}

export function useDemoPreview() {
  return useQuery({
    queryKey: ['demo-preview'],
    queryFn: () => api.get<DemoPreview>('/demo/aquapure-preview'),
  })
}

export function useLoadDemo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api.post<BusinessPlanProject>('/demo/load-aquapure'),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      qc.invalidateQueries({ queryKey: ['demo-preview'] })
    },
  })
}
