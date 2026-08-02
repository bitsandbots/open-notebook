'use client'

import { useState } from 'react'
import { Download } from 'lucide-react'

import { reportsApi } from '@/lib/api/reports'
import { EXPORT_FORMATS } from '@/lib/types/reports'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useTranslation } from '@/lib/hooks/use-translation'
import { toast } from 'sonner'

interface ExportMenuProps {
  reportId: string
  reportName: string
}

export function ExportMenu({ reportId, reportName }: ExportMenuProps) {
  const { t } = useTranslation()
  const [exporting, setExporting] = useState<string | null>(null)

  const handleExport = async (format: string, extension: string) => {
    setExporting(format)
    try {
      const blob = await reportsApi.exportReport(reportId, format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportName}${extension}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      toast.error(t('reports.exportFailed'))
    } finally {
      setExporting(null)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="mr-2 h-4 w-4" />
          {t('reports.export')}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {EXPORT_FORMATS.map(({ key, label, extension }) => (
          <DropdownMenuItem
            key={key}
            onClick={() => handleExport(key, extension)}
            disabled={exporting === key}
          >
            {exporting === key
              ? t('reports.exporting')
              : `${label} (${extension})`}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
