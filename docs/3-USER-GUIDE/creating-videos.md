# Creating Videos - Generate Narrated Overviews

Turn notebook sources into narrated MP4 videos with AI voiceover and styled slide visuals.

> **Prerequisite**: Video generation requires `OPEN_NOTEBOOK_ENABLE_VIDEO=true` in your environment. See [Video Setup](../5-CONFIGURATION/video-setup.md).

---

## Quick-Start: Your First Video (10 Minutes)

```
1. Go to your notebook
2. Click "Generate Video"
3. Select sources to include
4. Set slide count and style
5. Click "Generate Draft"
6. Review slides and narration text
7. Edit narration if needed
8. Click "Approve & Render"
9. Wait 10-30 minutes (render runs in background)
10. Download or stream MP4 when ready
```

---

## Step-by-Step: The Complete Workflow

### Step 1: Prepare Content

```
Before generating:

✓ Sources are processed and ready
✓ You have a clear message (what's the 5-minute story?)
✓ TTS model is configured (Settings → Models)
✓ Video is enabled (OPEN_NOTEBOOK_ENABLE_VIDEO=true)

Good preparation saves time in draft review.
```

### Step 2: Generate Draft

```
Generate Video dialog:

Notebook: "Product Launch Analysis"
Sources:
  ☑ Market research report
  ☑ Customer beta feedback
  ☑ Competitor launch comparisons

Settings:
  Slide count: 8
  Style: Professional
  Narration voice: Default TTS model
  Instructions: "Focus on the launch opportunity and competitive advantage.
                 Keep it optimistic but grounded in data."

Click "Generate Draft"

→ System generates slides + narration text + TTS audio
→ Status changes to "Draft Ready" when complete
→ You can now review before the expensive render step
```

### Step 3: Review the Draft

```
Draft review screen:

┌──────────────────────────────────────────────────────┐
│ SLIDES                          │ SLIDE PREVIEW      │
│                                 │                    │
│ 1. Title                        │                    │
│ 2. Market Opportunity    ← here │                    │
│ 3. Customer Need                │                    │
│ 4. Our Solution                 │                    │
│ 5. Competitive Advantage        │                    │
│ 6. Go-to-Market Strategy        │                    │
│ 7. Projections                  │                    │
│ 8. Next Steps                   │                    │
│                                 │                    │
│ NARRATION (slide 2):            │                    │
│ "The market for this product    │                    │
│  represents a $12B opportunity  │                    │
│  growing at 22% annually..."    │                    │
│ [Edit narration]                │                    │
│                                 │                    │
│ [Play narration audio preview]  │                    │
│ [Regenerate slide]              │                    │
│ [Approve & Render]              │                    │
└──────────────────────────────────────────────────────┘

Review every slide:
- Does the message flow logically?
- Are the bullet points scannable?
- Is the narration natural and engaging?
- Are data points accurate to the sources?

Edit narration text directly — this is your only chance
before the expensive render step.
```

### Step 4: Edit Narration

```
Editing narration text:

Good narration:
"The market opportunity is significant. We're looking at a
$12 billion addressable market growing at 22% annually. But
here's what makes this interesting — our beta customers are
reporting 40% time savings compared to their current workflows."

Bad narration (reads like a report):
"The total addressable market for this product category is
estimated at $12 billion with a compound annual growth rate
of 22 percent according to the Q3 market analysis report..."

Tips:
- Write like you speak, not like you write
- Short sentences (15-20 words)
- Use contractions ("we're" not "we are")
- Vary sentence length for rhythm
- Include transitions between slides
```

### Step 5: Approve and Render

```
Click "Approve & Render"

What happens:
1. System creates visual slides (HTML → PNG screenshots)
2. Narration text → TTS → MP3 audio clips
3. Each slide image + audio → MP4 video segment
4. All segments → concatenated → Final MP4

Progress indicators:
  [=====>    ] Rendering slides (3/8)
  [========> ] Combining audio (done)
  [=========>] Encoding video (75%)

Total render time: 10-30 minutes (processed in background)
You can close the browser — render continues on the server.
```

### Step 6: Download or Stream

```
When complete:

Preview:
  [▶ Play] — Stream MP4 directly in browser

Download:
  [⬇ Download MP4] — Save to computer

The video is standard H.264 MP4 at 1920×1080 (30fps).
  File size: ~50-150MB for a typical 5-10 minute video.
  Plays on: Any device, any browser, any video player.
```

---

## Understanding the Two-Phase Design

### Why Draft → Render?

Video rendering is expensive:
```
Generate draft:   30-90 seconds  (LLM calls only)
Render video:     10-30 minutes  (Playwright + ffmpeg)
```

If you spotted a mistake after rendering, you'd waste 10-30 minutes. The draft phase costs almost nothing — review there first.

### What You Can Change at Draft

```
Before render, you can edit:
✓ Slide titles and bullets
✓ Narration text per slide
✓ Slide order
✓ Regenerate individual slides

After render, you must:
- Fix the issue
- Re-render the entire video (10-30 min)
```

**Strategy**: Spend 2 minutes reviewing the draft. Save 20 minutes of re-rendering.

---

## Choosing Narration Style

```
Professional narrator:
  Instructions: "Authoritative but warm. Like a TED talk narrator."
  Best for: Business briefings, executive summaries

Conversational guide:
  Instructions: "Friendly, approachable. Like explaining to a colleague."
  Best for: Internal updates, training videos

Academic presenter:
  Instructions: "Formal, precise. Like a conference presentation."
  Best for: Research overviews, educational content

Enthusiastic storyteller:
  Instructions: "Energetic, engaging. Like a product launch keynote."
  Best for: Pitch videos, marketing overviews
```

The narration style comes from your instructions — the LLM adapts the tone.

---

## Tips for Better Videos

### Keep It Short

```
5 minutes:  Great for overviews and briefings
8 minutes:  Good for deeper dives with data
10+ minutes:  Only if the topic demands it

Audience attention drops sharply after 8 minutes.
If you need more time, consider making it a podcast instead
(people listen longer than they watch).
```

### Match Visual Pace to Narration

```
Short bullet, short narration = 15-20 seconds per slide
  → 8 slides = ~2.5 minute video

Longer bullet, detailed narration = 30-45 seconds per slide
  → 8 slides = ~6 minute video

Aim for 20-30 seconds per slide as a starting point.
```

### Test Narration by Reading Aloud

```
Before approving the draft:
1. Read the narration out loud
2. Does it sound natural?
3. Are there tongue-twisters or awkward phrases?
4. Do slide transitions feel smooth?

Reading aloud catches problems that silent reading misses.
```

---

## Common Issues

### Video Generation Is Slow

**Problem**: Rendering takes longer than expected.

**Explanation**:
```
Playwright screenshot per slide:  ~5-10 seconds
TTS per slide:                     ~10-20 seconds
ffmpeg encode per slide:           ~30-60 seconds
ffmpeg concat:                     ~1-2 minutes

8-slide video: ~10-20 minutes total
This is normal — video rendering is compute-intensive.
```

### Narration Sounds Robotic

**Problem**: TTS voice lacks natural cadence.

**Solutions**:
```
- Switch TTS provider (ElevenLabs > Google > OpenAI for quality)
- Shorten sentences (long sentences sound more robotic)
- Add natural pauses: "Let me put that another way. [pause]"
- Use contractions and conversational language
```

### Slide Images Look Wrong

**Problem**: Visual slides don't match expectations.

**Solutions**:
```
- Change the theme (different colors may help)
- Keep bullet points short (long text overflows at 1080p)
- Regenerate individual slides with more specific content
- Note: Visuals are generated from the slide content —
  if the content is good, the visuals will represent it well
```

### Render Failed

**Problem**: "Video render failed"

**Solutions**:
```
1. Check disk space (videos need ~500MB free during render)
2. Verify Playwright is installed: playwright install chromium
3. Check worker logs for ffmpeg errors
4. Reduce slide count and retry
5. Ensure TTS model is configured and working
```

---

## Cost Breakdown

```
8-slide, 6-minute video:

  LLM (slides + narration):  ~$0.06 (GPT-4o)
  TTS (6 min):                ~$0.09 (Google TTS)
  Render (local):             Free
                             ─────
  Total:                     ~$0.15 per video

With Anthropic Claude + ElevenLabs: ~$0.75 per video
With Ollama + local TTS:             Free (but slower)
```

---

## Video vs. Podcast vs. Presentation: When to Use What

```
Use VIDEO when:
  - Your audience won't read a report
  - You need a shareable, self-contained overview
  - The visual structure helps understanding
  - You want something for social media or email

Use PODCAST when:
  - Your audience is commuting or exercising
  - The content is dialogue-driven (debate, interview)
  - Visuals aren't needed
  - You need longer-form content (15-60 min)

Use PRESENTATION when:
  - You'll present it live
  - The audience needs to see details on slides
  - You want editable slides for collaboration
  - You need speaker notes for delivery
```

---

## Before Generation Checklist

- [ ] `OPEN_NOTEBOOK_ENABLE_VIDEO=true` is set
- [ ] Sources are processed and ready
- [ ] TTS model is configured
- [ ] Slide count is appropriate (5-10 for overviews)
- [ ] Narration style is specified in instructions
- [ ] Disk has >1GB free space

### Draft Review Checklist
- [ ] Message flows logically across slides
- [ ] Narration sounds natural when read aloud
- [ ] Data points are accurate to sources
- [ ] Slide transitions make sense
- [ ] Each slide adds value (no filler slides)

### After Render
- [ ] Watch the full video
- [ ] Audio sync is correct (narration matches slides)
- [ ] Download for sharing
- [ ] Delete draft if satisfied (or keep for future revisions)

---

## Use Cases

### Executive Briefing
```
Video: "Q3 Performance Overview"
Slides: 8, Duration: 6 minutes
Style: Professional
Content: Revenue data, market analysis, strategic outlook
Use: Send to board members before the quarterly review meeting
Benefit: Everyone arrives informed — meeting is discussion, not presentation
```

### Product Launch Teaser
```
Video: "Introducing Project Aurora"
Slides: 6, Duration: 3 minutes
Style: Pitch
Content: Problem, solution, early traction, launch timeline
Use: Share with sales team and early-access customers
Benefit: Consistent message, no one-off briefings needed
```

### Research Summary
```
Video: "Key Findings: AI Alignment Survey"
Slides: 10, Duration: 8 minutes
Style: Academic
Content: Methodology, results, implications, next steps
Use: Accompany the full paper — share on social media
Benefit: Reaches people who won't read the full 30-page paper
```

### Onboarding Overview
```
Video: "Welcome to the Team: What We're Building"
Slides: 7, Duration: 5 minutes
Style: Casual
Content: Product vision, team structure, current priorities
Use: Send to new hires before their first day
Benefit: Consistent onboarding, saves manager time
```

---

## Summary

Videos turn research into self-contained, narrated overviews:

1. **Generate draft** — slides + narration in under 2 minutes
2. **Review and edit** — fix issues before the expensive render
3. **Approve and render** — system produces the MP4 in background
4. **Download or stream** — shareable, standard video format

The two-phase design means you only render when the content is right. Review costs almost nothing — use it.
