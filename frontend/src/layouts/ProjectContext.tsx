import { createContext, useContext, type ReactNode } from 'react'
import { useCompletion, useProject } from '@/api/hooks'
import type { BusinessPlanProject, CompletionReport } from '@/types'

interface ProjectContextValue {
  projectId: string
  project?: BusinessPlanProject
  completion?: CompletionReport
  /** Currency selected once in Setup, reused app-wide. Defaults to USD. */
  currency: string
  isLoading: boolean
  isError: boolean
  error?: Error
  /** Quick lookup: section key -> complete? */
  isSectionComplete: (key: string) => boolean
}

const Ctx = createContext<ProjectContextValue | null>(null)

export function ProjectProvider({ projectId, children }: { projectId: string; children: ReactNode }) {
  const projectQ = useProject(projectId)
  const completionQ = useCompletion(projectId)

  const completion = completionQ.data
  const value: ProjectContextValue = {
    projectId,
    project: projectQ.data,
    completion,
    currency: projectQ.data?.setup?.currency ?? 'USD',
    isLoading: projectQ.isLoading,
    isError: projectQ.isError,
    error: projectQ.error ?? undefined,
    isSectionComplete: (key) =>
      completion?.sections.find((s) => s.key === key)?.complete ?? false,
  }

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useProjectContext(): ProjectContextValue {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useProjectContext must be used within ProjectProvider')
  return ctx
}
