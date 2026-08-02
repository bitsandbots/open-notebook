'use client'

import { useState } from 'react'
import { Check, Edit3, X } from 'lucide-react'

import { podcastsApi } from '@/lib/api/podcasts'
import { EpisodeDraft } from '@/lib/types/podcasts'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Textarea } from '@/components/ui/textarea'
import { useTranslation } from '@/lib/hooks/use-translation'
import { toast } from 'sonner'

interface DraftReviewProps {
  draft: EpisodeDraft
  onApprove: () => void
  onCancel: () => void
  approving?: boolean
  cancelling?: boolean
}

interface TranscriptSegment {
  speaker: string
  text: string
}

/**
 * Extract segments from the transcript structure returned by podcast-creator.
 * The transcript is typically { transcript: [{ speaker, text }, ...] }.
 */
function extractSegments(
  transcript: Record<string, unknown> | null
): TranscriptSegment[] {
  if (!transcript) return []
  const inner = transcript['transcript']
  if (Array.isArray(inner)) {
    return inner.filter(
      (s): s is TranscriptSegment =>
        typeof s === 'object' && s !== null && 'speaker' in s && 'text' in s
    )
  }
  return []
}

export function DraftReview({
  draft,
  onApprove,
  onCancel,
  approving = false,
  cancelling = false,
}: DraftReviewProps) {
  const { t } = useTranslation()
  const segments = extractSegments(draft.transcript)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [editText, setEditText] = useState('')
  const [saving, setSaving] = useState(false)

  const startEditing = (index: number, text: string) => {
    setEditingIndex(index)
    setEditText(text)
  }

  const saveEdit = async (index: number) => {
    if (!draft.episode_id) return

    const updated = [...segments]
    updated[index] = { ...updated[index], text: editText }

    setSaving(true)
    try {
      await podcastsApi.updateDraft(draft.episode_id, {
        transcript: { transcript: updated },
      })
      segments[index].text = editText
      setEditingIndex(null)
      toast.success(t('podcasts.draftEditSaved'))
    } catch {
      toast.error(t('podcasts.draftEditFailed'))
    } finally {
      setSaving(false)
    }
  }

  const cancelEditing = () => {
    setEditingIndex(null)
    setEditText('')
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Transcript segments */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">
            {t('podcasts.transcript')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="max-h-[50vh]">
            <div className="space-y-4">
              {segments.map((segment, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-line p-3 transition-colors hover:border-line-strong"
                >
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-ink-faint">
                      {segment.speaker}
                    </span>
                    {editingIndex !== index && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2"
                        onClick={() => startEditing(index, segment.text)}
                      >
                        <Edit3 className="mr-1 h-3 w-3" />
                        {t('common.edit')}
                      </Button>
                    )}
                  </div>

                  {editingIndex === index ? (
                    <div className="space-y-2">
                      <Textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        rows={4}
                        className="font-mono text-sm"
                        disabled={saving}
                      />
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={cancelEditing}
                          disabled={saving}
                        >
                          <X className="mr-1 h-3 w-3" />
                          {t('common.cancel')}
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => saveEdit(index)}
                          disabled={saving}
                        >
                          <Check className="mr-1 h-3 w-3" />
                          {t('common.save')}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm leading-relaxed text-ink-soft">
                      {segment.text}
                    </p>
                  )}
                </div>
              ))}

              {segments.length === 0 && (
                <p className="py-8 text-center text-sm text-ink-faint">
                  {t('podcasts.noTranscriptSegments')}
                </p>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Briefing display */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">
            {t('podcasts.briefing')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-sm text-ink-soft">
            {draft.briefing}
          </p>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3">
        <Button
          variant="outline"
          onClick={onCancel}
          disabled={approving || cancelling}
        >
          <X className="mr-2 h-4 w-4" />
          {t('podcasts.cancelGeneration')}
        </Button>
        <Button onClick={onApprove} disabled={approving || cancelling}>
          <Check className="mr-2 h-4 w-4" />
          {approving
            ? t('podcasts.approving')
            : t('podcasts.approveAndRender')}
        </Button>
      </div>
    </div>
  )
}
