/* Textual business plan API hooks. */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, API_BASE } from './client'
import type {
  ApplyOutlineTemplateRequest,
  ImageUpdate,
  OutlineSuggestionResponse,
  SectionCreate,
  SectionUpdate,
  TextPlanCompletion,
  TextPlanDocument,
  TextPlanImage,
  TextPlanSection,
  TextPlanTopic,
  TopicCreate,
  TopicUpdate,
} from '@/types/textPlan'

const base = (projectId: string) => `/projects/${projectId}/text-plan`

export const textPlanKeys = {
  doc: (pid: string) => ['text-plan', pid] as const,
  completion: (pid: string) => ['text-plan-completion', pid] as const,
  suggestions: (pid: string) => ['text-plan-suggestions', pid] as const,
}

export function useTextPlan(projectId: string | undefined) {
  return useQuery({
    queryKey: textPlanKeys.doc(projectId ?? ''),
    queryFn: () => api.get<TextPlanDocument>(base(projectId!)),
    enabled: !!projectId,
  })
}

export function useTextPlanCompletion(projectId: string | undefined) {
  return useQuery({
    queryKey: textPlanKeys.completion(projectId ?? ''),
    queryFn: () => api.get<TextPlanCompletion>(`${base(projectId!)}/completion`),
    enabled: !!projectId,
  })
}

export function useOutlineSuggestions(projectId: string | undefined, enabled = true) {
  return useQuery({
    queryKey: textPlanKeys.suggestions(projectId ?? ''),
    queryFn: () => api.get<OutlineSuggestionResponse>(`${base(projectId!)}/outline-suggestions`),
    enabled: !!projectId && enabled,
  })
}

/* ---- mutations -------------------------------------------------------- */
function useInvalidate(projectId: string | undefined) {
  const qc = useQueryClient()
  return () => {
    if (!projectId) return
    qc.invalidateQueries({ queryKey: textPlanKeys.doc(projectId) })
    qc.invalidateQueries({ queryKey: textPlanKeys.completion(projectId) })
  }
}

export function useCreateSection(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (body: SectionCreate) => api.post<TextPlanSection>(`${base(projectId)}/sections`, body),
    onSuccess: invalidate,
  })
}

export function useUpdateSection(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: SectionUpdate }) =>
      api.put<TextPlanSection>(`${base(projectId)}/sections/${id}`, body),
    onSuccess: invalidate,
  })
}

export function useDeleteSection(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (id: string) => api.delete<void>(`${base(projectId)}/sections/${id}`),
    onSuccess: invalidate,
  })
}

export function useDuplicateSection(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (id: string) => api.post<TextPlanSection>(`${base(projectId)}/sections/${id}/duplicate`),
    onSuccess: invalidate,
  })
}

export function useCreateTopic(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (body: TopicCreate) => api.post<TextPlanTopic>(`${base(projectId)}/topics`, body),
    onSuccess: invalidate,
  })
}

export function useUpdateTopic(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: TopicUpdate }) =>
      api.put<TextPlanTopic>(`${base(projectId)}/topics/${id}`, body),
    onSuccess: invalidate,
  })
}

export function useDeleteTopic(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (id: string) => api.delete<void>(`${base(projectId)}/topics/${id}`),
    onSuccess: invalidate,
  })
}

export function useDuplicateTopic(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (id: string) => api.post<TextPlanTopic>(`${base(projectId)}/topics/${id}/duplicate`),
    onSuccess: invalidate,
  })
}

export function useReorderSections(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (ordered_section_ids: string[]) =>
      api.put<TextPlanDocument>(`${base(projectId)}/reorder-sections`, { ordered_section_ids }),
    onSuccess: invalidate,
  })
}

export function useReorderTopics(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: ({ section_id, ordered_topic_ids }: { section_id: string; ordered_topic_ids: string[] }) =>
      api.put<TextPlanSection>(`${base(projectId)}/reorder-topics`, { section_id, ordered_topic_ids }),
    onSuccess: invalidate,
  })
}

export function useMoveTopic(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (body: { topic_id: string; target_section_id: string; target_order_index: number }) =>
      api.put<TextPlanTopic>(`${base(projectId)}/move-topic`, body),
    onSuccess: invalidate,
  })
}

export function useApplyTemplate(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: (body: ApplyOutlineTemplateRequest) =>
      api.post<TextPlanDocument>(`${base(projectId)}/apply-outline-template`, body),
    onSuccess: invalidate,
  })
}

export function useDeleteImage(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: ({ topicId, imageId }: { topicId: string; imageId: string }) =>
      api.delete<void>(`${base(projectId)}/topics/${topicId}/images/${imageId}`),
    onSuccess: invalidate,
  })
}

export function useUpdateImage(projectId: string) {
  const invalidate = useInvalidate(projectId)
  return useMutation({
    mutationFn: ({ topicId, imageId, body }: { topicId: string; imageId: string; body: ImageUpdate }) =>
      api.put<TextPlanImage>(`${base(projectId)}/topics/${topicId}/images/${imageId}`, body),
    onSuccess: invalidate,
  })
}

/** Upload a topic image (multipart). Returns the created image record. */
export async function uploadTopicImage(projectId: string, topicId: string, file: File): Promise<TextPlanImage> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}${base(projectId)}/topics/${topicId}/images`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    let detail = `Upload failed (${res.status})`
    try {
      detail = (await res.json())?.detail ?? detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return (await res.json()) as TextPlanImage
}

/** Absolute URL (through the dev proxy) for an image record. */
export function imageSrc(image: TextPlanImage): string {
  return image.url.startsWith('/api') ? image.url : `${API_BASE}${image.url}`
}
