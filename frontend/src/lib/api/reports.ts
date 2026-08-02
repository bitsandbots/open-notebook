import apiClient from './client'
import {
  Report,
  ReportListResponse,
  GenerateReportRequest,
  GenerateReportResponse,
  UpdateReportRequest,
} from '@/lib/types/reports'

export const reportsApi = {
  listReports: async (notebookId?: string | null) => {
    const params = notebookId ? { notebook_id: notebookId } : {}
    const response = await apiClient.get<ReportListResponse>('/reports', { params })
    return response.data
  },

  getReport: async (reportId: string) => {
    const response = await apiClient.get<Report>(`/reports/${reportId}`)
    return response.data
  },

  updateReport: async (reportId: string, payload: UpdateReportRequest) => {
    const response = await apiClient.patch<Report>(
      `/reports/${reportId}`,
      payload
    )
    return response.data
  },

  deleteReport: async (reportId: string) => {
    await apiClient.delete(`/reports/${reportId}`)
  },

  generateReport: async (payload: GenerateReportRequest) => {
    const response = await apiClient.post<GenerateReportResponse>(
      '/reports/generate',
      payload
    )
    return response.data
  },

  exportReport: async (reportId: string, format: string) => {
    const response = await apiClient.get<Blob>(
      `/reports/${reportId}/export`,
      {
        params: { format },
        responseType: 'blob',
      }
    )
    return response.data
  },
}
