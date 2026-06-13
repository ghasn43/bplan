/* Types mirroring backend/app/models/text_plan.py + schemas/text_plan.py */

export type TopicStatus = 'not_started' | 'draft' | 'in_review' | 'completed'
export type ImageAlignment = 'left' | 'center' | 'right' | 'full_width'

export interface TextPlanImage {
  id: string
  file_name: string
  original_file_name: string
  url: string
  mime_type: string
  file_size: number
  width: number | null
  height: number | null
  caption: string
  alt_text: string
  alignment: ImageAlignment
  display_width_percentage: number
  order_index: number
}

export interface TextPlanTopic {
  id: string
  section_id: string | null
  title: string
  content_html: string
  content_json?: Record<string, unknown> | null
  plain_text: string
  order_index: number
  topic_type: string
  include_in_report: boolean
  status: TopicStatus
  priority: string
  word_count: number
  reading_time_minutes: number
  guidance_text: string
  images: TextPlanImage[]
  updated_at: string
}

export interface TextPlanSection {
  id: string
  title: string
  subtitle: string
  description: string
  section_type: string
  order_index: number
  collapsed: boolean
  include_in_report: boolean
  page_break_before: boolean
  status: TopicStatus
  guidance_text: string
  topics: TextPlanTopic[]
  updated_at: string
}

export interface TextPlanDocument {
  id: string
  title: string
  template_id: string | null
  business_type: string | null
  sections: TextPlanSection[]
  updated_at: string
}

export interface TextPlanCompletion {
  project_id: string
  completion_percent: number
  section_count: number
  topic_count: number
  completed_topics: number
  draft_topics: number
  empty_topics: number
  word_count: number
  image_count: number
  sections_in_report: number
  topics_in_report: number
  missing_key_sections: string[]
  warnings: string[]
}

export interface TemplateTopicInfo {
  title: string
  topic_type: string
  guidance_text: string
}

export interface TemplateSectionInfo {
  title: string
  section_type: string
  description: string
  guidance_text: string
  topics: TemplateTopicInfo[]
}

export interface OutlineTemplateInfo {
  id: string
  name: string
  description: string
  business_types: string[]
  section_count: number
  topic_count: number
  sections: TemplateSectionInfo[]
}

export interface OutlineSuggestionResponse {
  detected_business_type: string
  recommended_template_id: string
  explanation: string
  report_style: string | null
  templates: OutlineTemplateInfo[]
}

export interface ApplyOutlineTemplateRequest {
  template_id: string
  mode: 'replace' | 'append'
  selected_section_titles?: string[] | null
  selected_topic_titles?: string[] | null
  with_sample_content?: boolean
}

export interface SectionCreate {
  title?: string
  section_type?: string
  description?: string
  guidance_text?: string
  include_in_report?: boolean
}

export interface SectionUpdate {
  title?: string
  subtitle?: string
  description?: string
  section_type?: string
  guidance_text?: string
  collapsed?: boolean
  include_in_report?: boolean
  page_break_before?: boolean
  status?: TopicStatus
}

export interface TopicCreate {
  section_id: string
  title?: string
  content_html?: string
  topic_type?: string
  guidance_text?: string
  include_in_report?: boolean
}

export interface TopicUpdate {
  title?: string
  content_html?: string
  content_json?: Record<string, unknown> | null
  topic_type?: string
  guidance_text?: string
  include_in_report?: boolean
  status?: TopicStatus
  priority?: string
}

export interface ImageUpdate {
  caption?: string
  alt_text?: string
  alignment?: ImageAlignment
  display_width_percentage?: number
  order_index?: number
}
