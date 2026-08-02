'use client'

import { useState } from 'react'
import { Loader2 } from 'lucide-react'

import { useGenerateReport } from '@/lib/hooks/use-reports'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useTranslation } from '@/lib/hooks/use-translation'

interface GenerateReportDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  notebookId?: string | null
}

const STYLES = [
  { value: 'professional', label: 'Professional' },
  { value: 'academic', label: 'Academic' },
  { value: 'business', label: 'Business' },
  { value: 'casual', label: 'Casual' },
]

export function GenerateReportDialog({
  open,
  onOpenChange,
  notebookId,
}: GenerateReportDialogProps) {
  const { t } = useTranslation()
  const generateReport = useGenerateReport()
  const [instructions, setInstructions] = useState('')
  const [style, setStyle] = useState('professional')

  const handleSubmit = async () => {
    await generateReport.mutateAsync({
      notebook_id: notebookId ?? null,
      instructions: instructions || null,
      style,
    })
    onOpenChange(false)
    setInstructions('')
    setStyle('professional')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t('reports.generateTitle')}</DialogTitle>
          <DialogDescription>
            {t('reports.generateDesc')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="style">{t('reports.style')}</Label>
            <Select value={style} onValueChange={setStyle}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STYLES.map((s) => (
                  <SelectItem key={s.value} value={s.value}>
                    {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="instructions">
              {t('reports.instructions')}
            </Label>
            <Textarea
              id="instructions"
              placeholder={t('reports.instructionsPlaceholder')}
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows={4}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            {t('common.cancel')}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={generateReport.isPending}
          >
            {generateReport.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : null}
            {generateReport.isPending
              ? t('reports.generating')
              : t('reports.generate')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
