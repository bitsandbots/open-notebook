import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { reportsApi } from '@/lib/api/reports'
import { QUERY_KEYS } from '@/lib/api/query-client'
import { useToast } from '@/lib/hooks/use-toast'
import { useTranslation } from '@/lib/hooks/use-translation'
import { getApiErrorKey } from '@/lib/utils/error-handler'
import { GenerateReportRequest, UpdateReportRequest } from '@/lib/types/reports'

export function useReports(notebookId?: string | null) {
  return useQuery({
    queryKey: [...QUERY_KEYS.reports, notebookId],
    queryFn: () => reportsApi.listReports(notebookId),
  })
}

export function useReport(reportId: string) {
  return useQuery({
    queryKey: [...QUERY_KEYS.reports, reportId],
    queryFn: () => reportsApi.getReport(reportId),
    enabled: !!reportId,
  })
}

export function useGenerateReport() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const { t } = useTranslation()

  return useMutation({
    mutationFn: (payload: GenerateReportRequest) =>
      reportsApi.generateReport(payload),
    onSuccess: async () => {
      await queryClient.refetchQueries({ queryKey: QUERY_KEYS.reports })
      toast({
        title: t('reports.generationStarted'),
        description: t('reports.generationStartedDesc'),
      })
    },
    onError: (error: unknown) => {
      toast({
        title: t('reports.failedToGenerate'),
        description: getApiErrorKey(error, t('common.error')),
        variant: 'destructive',
      })
    },
  })
}

export function useUpdateReport() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const { t } = useTranslation()

  return useMutation({
    mutationFn: ({
      reportId,
      payload,
    }: {
      reportId: string
      payload: UpdateReportRequest
    }) => reportsApi.updateReport(reportId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.reports })
      toast({
        title: t('reports.saved'),
        description: t('reports.savedDesc'),
      })
    },
    onError: (error: unknown) => {
      toast({
        title: t('reports.failedToSave'),
        description: getApiErrorKey(error, t('common.error')),
        variant: 'destructive',
      })
    },
  })
}

export function useDeleteReport() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const { t } = useTranslation()

  return useMutation({
    mutationFn: (reportId: string) => reportsApi.deleteReport(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.reports })
      toast({
        title: t('reports.deleted'),
        description: t('reports.deletedDesc'),
      })
    },
    onError: (error: unknown) => {
      toast({
        title: t('reports.failedToDelete'),
        description: getApiErrorKey(error, t('common.error')),
        variant: 'destructive',
      })
    },
  })
}
