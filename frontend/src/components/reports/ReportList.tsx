'use client'

import { formatDistanceToNow } from 'date-fns'
import { getDateLocale } from '@/lib/utils/date-locale'
import { FileText, Trash2 } from 'lucide-react'
import Link from 'next/link'

import { Report } from '@/lib/types/reports'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { useTranslation } from '@/lib/hooks/use-translation'

interface ReportListProps {
  reports: Report[]
  onDelete: (reportId: string) => void
  deleting?: boolean
}

function StatusBadge({ status }: { status: string }) {
  const { t } = useTranslation()
  const meta: Record<string, { label: string; className: string }> = {
    draft: {
      label: t('reports.statusDraft'),
      className: 'bg-teal-tint text-teal border-teal/30',
    },
    generating: {
      label: t('reports.statusGenerating'),
      className: 'bg-warn-tint text-warn border-warn/30',
    },
    failed: {
      label: t('reports.statusFailed'),
      className: 'bg-destructive-tint text-destructive border-destructive/30',
    },
  }

  const m = meta[status] ?? {
    label: status,
    className: 'bg-muted text-muted-foreground border-transparent',
  }

  return (
    <Badge
      variant="outline"
      className={`uppercase tracking-wide text-xs ${m.className}`}
    >
      {m.label}
    </Badge>
  )
}

export function ReportList({ reports, onDelete, deleting }: ReportListProps) {
  const { t, language } = useTranslation()

  if (reports.length === 0) {
    return (
      <div className="rounded-md border border-dashed p-10 text-center">
        <p className="text-sm text-muted-foreground">
          {t('reports.noReports')}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {reports.map((report) => {
        const distance = report.created
          ? formatDistanceToNow(new Date(report.created), {
              addSuffix: true,
              locale: getDateLocale(language),
            })
          : null

        return (
          <Card key={report.id}>
            <CardContent className="flex items-center justify-between p-4">
              <div className="min-w-0 flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                  <Link
                    href={`/reports/${report.id}`}
                    className="truncate text-base font-semibold text-foreground hover:text-fern"
                  >
                    {report.name}
                  </Link>
                  <StatusBadge status={report.status} />
                </div>
                <p className="text-xs text-muted-foreground">
                  {report.word_count != null
                    ? t('reports.wordCount', { count: report.word_count })
                    : null}
                  {report.word_count != null && distance ? ' • ' : ''}
                  {distance ?? ''}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/reports/${report.id}`}>
                    {t('common.edit')}
                  </Link>
                </Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-destructive">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        {t('reports.deleteTitle')}
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        {t('reports.deleteDesc', { name: report.name })}
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>{t('common.cancel')}</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={() => onDelete(report.id)}
                        disabled={deleting}
                      >
                        {deleting ? t('common.deleting') : t('common.delete')}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
