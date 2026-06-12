import { Badge } from '@/components/ui/Badge'
import type { ReportFormat } from '@/types/reports'

export function ReportFormatBadge({ format }: { format: ReportFormat }) {
  const map: Record<ReportFormat, { tone: 'blue' | 'red' | 'amber'; label: string }> = {
    docx: { tone: 'blue', label: 'WORD' },
    pdf: { tone: 'red', label: 'PDF' },
    html: { tone: 'amber', label: 'HTML' },
  }
  const { tone, label } = map[format] ?? map.docx
  return <Badge tone={tone}>{label}</Badge>
}
