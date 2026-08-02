'use client'

import { useCallback, useState } from 'react'
import { Loader2, Plus, RefreshCcw } from 'lucide-react'

import { useDeleteReport, useReports } from '@/lib/hooks/use-reports'
import { ReportList } from '@/components/reports/ReportList'
import { GenerateReportDialog } from '@/components/reports/GenerateReportDialog'
import { Button } from '@/components/ui/button'
import { useTranslation } from '@/lib/hooks/use-translation'

export default function ReportsPage() {
  const { t } = useTranslation()
  const [showGenerate, setShowGenerate] = useState(false)
  const { data, isLoading, isError, refetch, isFetching } = useReports()
  const deleteReport = useDeleteReport()

  const reports = data?.reports ?? []

  const handleDelete = useCallback(
    (reportId: string) => deleteReport.mutate(reportId),
    [deleteReport]
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="space-y-1">
          <h2 className="font-display text-xl font-semibold tracking-tight">
            {t('reports.title')}
          </h2>
          <p className="text-sm text-muted-foreground">
            {t('reports.description')}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => setShowGenerate(true)}>
            <Plus className="mr-2 h-4 w-4" />
            {t('reports.generate')}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            {isFetching ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCcw className="mr-2 h-4 w-4" />
            )}
            {t('common.refresh')}
          </Button>
        </div>
      </div>

      {isError ? (
        <div className="rounded-md border border-destructive/30 bg-destructive-tint p-4">
          <p className="text-sm text-destructive">{t('reports.loadError')}</p>
        </div>
      ) : null}

      {isLoading ? (
        <div className="flex items-center gap-3 rounded-lg border border-dashed p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          {t('reports.loading')}
        </div>
      ) : (
        <ReportList
          reports={reports}
          onDelete={handleDelete}
          deleting={deleteReport.isPending}
        />
      )}

      <GenerateReportDialog
        open={showGenerate}
        onOpenChange={setShowGenerate}
      />
    </div>
  )
}
