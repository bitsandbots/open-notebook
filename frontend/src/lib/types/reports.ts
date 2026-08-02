export interface Report {
  id: string
  name: string
  content: string
  content_type: string
  notebook_id: string | null
  source_ids: string[]
  status: string
  report_group_id: string | null
  parent_id: string | null
  word_count: number | null
  created: string | null
  updated: string | null
}

export interface ReportListResponse {
  reports: Report[]
}

export interface GenerateReportRequest {
  notebook_id?: string | null
  source_ids?: string[]
  instructions?: string | null
  style?: string
}

export interface GenerateReportResponse {
  job_id: string
  status: string
  message: string
}

export interface UpdateReportRequest {
  name?: string
  content?: string
}

export const EXPORT_FORMATS = [
  { key: 'pdf', label: 'PDF', extension: '.pdf' },
  { key: 'docx', label: 'DOCX', extension: '.docx' },
  { key: 'odt', label: 'ODT', extension: '.odt' },
  { key: 'html', label: 'HTML', extension: '.html' },
  { key: 'epub', label: 'EPUB', extension: '.epub' },
  { key: 'latex', label: 'LaTeX', extension: '.tex' },
  { key: 'plain', label: 'Plain Text', extension: '.txt' },
  { key: 'md', label: 'Markdown', extension: '.md' },
] as const
