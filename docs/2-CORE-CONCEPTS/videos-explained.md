# Videos Explained - Research as Narrated Visual Overviews

Videos turn your notebook sources into narrated MP4 overviews with AI voiceover and styled slide visuals.

---

## Why Videos Matter

### The Problem

Some research is best consumed as a shareable overview video:

```
Research → Deep understanding
         → Need to BRIEF others quickly
         → Slide decks require a presenter
         → Written reports require reading time
```

Video fills the gap: someone can watch a 5-minute overview and get oriented before reading the full report or attending the presentation.

### The Solution

Generate a narrated video overview from your sources — AI voiceover over styled slides, exportable as MP4.

```
Research pile → Generate video → Watch → Share → Deep dive into sources
                                  5-10 minute overview
```

---

## What Makes It Special

| Capability | Why It Matters |
|---|---|
| **AI narration** | Each slide has TTS voiceover — no recording needed |
| **Styled visuals** | Slides use the same theme system as Presentations (SLATE, OCEAN, FOREST, etc.) |
| **Two-phase generation** | Draft (review slides + narration) → Approve → Render (MP4) |
| **Editable before render** | Edit slide content and narration text before the expensive render step |
| **Streamable MP4** | Standard H.264 video — plays everywhere, shareable, embeddable |
| **Opt-in by design** | Video generation requires `OPEN_NOTEBOOK_ENABLE_VIDEO=true` — off by default to keep Docker image lean |

---

## How Video Generation Works

### Phase A: Draft (Slides + Narration)

```
Sources → LLM generates slide structure
       → LLM generates narration text per slide
       → TTS generates audio per slide narration
       → Saves draft (no video rendering yet)
       → User reviews slides + narration text
```

This phase is fast (LLM calls only) and lets you review before committing to the expensive render step.

### Phase B: Approve & Render

```
User approves draft → System renders:
  1. For each slide: HTML + theme CSS → Playwright screenshot → PNG image
  2. For each slide: narration text → TTS → MP3 audio clip
  3. ffmpeg: PNG image + MP3 audio → MP4 segment per slide
  4. ffmpeg: Concat all segments → Final MP4 video
```

The render phase is compute-intensive but only runs once (after you've reviewed the draft).

---

## Visual Style: Theme System

Videos reuse the same theme system as presentations:

```
THEME: OCEAN
  Background: Deep navy (#0c4a6e)
  Text: Light ice blue (#e0f2fe)
  Accent: Cyan (#22d3ee)
  Accent bar: 6px top edge
  Slide number: Bottom-right, subtle opacity

Slide layout (1920×1080):
┌──────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ ← accent bar
│                                          │
│                                          │
│        Market Overview                   │ ← title (64px)
│    Q3 performance across segments        │ ← subtitle (32px, accent color)
│                                          │
│  ▸ Revenue grew 18% YoY to $45M         │ ← bullets (28px)
│  ▸ Enterprise segment led with 32%       │
│  ▸ International expansion added 5       │
│    new markets                           │
│  ▸ Customer retention improved to 94%    │
│                                          │
│                                          │
│                                    4/10  │ ← slide number
└──────────────────────────────────────────┘
```

Each theme has its own color palette — the LLM assigns themes per slide based on content mood.

---

## The Render Pipeline

### Step 1: HTML → PNG

```
slide_data + theme → HTML string → Playwright (headless Chromium)
                                 → PNG screenshot (1920×1080)
```

The HTML uses inline CSS (no build step needed for server-side rendering). Six theme presets cover common presentation moods.

### Step 2: Narration → Audio

```
narration_text → TTS model (from model registry)
              → MP3 audio clip
```

Uses the same TTS infrastructure as podcasts — any configured TTS provider works (OpenAI, Google, ElevenLabs, local).

### Step 3: Image + Audio → Video Segment

```
slide_4.png + narration_4.mp3
  → ffmpeg: static image for audio duration
          → H.264 video at 30fps, 1920×1080
          → slide_4.mp4 segment
```

### Step 4: Concat → Final Video

```
slide_1.mp4 + slide_2.mp4 + ... + slide_N.mp4
  → ffmpeg concat
  → final_video.mp4
```

---

## Comparison: Video vs. Presentation vs. Podcast

| Aspect | Video | Presentation | Podcast |
|--------|-------|-------------|---------|
| **Output** | MP4 file | PPTX file / browser | MP3 audio |
| **Consumption** | Watch (passive) | Present (active) | Listen (passive) |
| **Visuals** | Styled slides + narration | Editable slides | None (audio only) |
| **Editing** | Before render (text only) | Full slide editor | Transcript editing |
| **Best for** | Briefing, sharing, overview | Meetings, teaching, presenting | Commuting, exercising, passive learn |
| **Generation time** | 5-15 min (draft) + 10-30 min (render) | 2-5 min | 5-20 min |

---

## Key Architecture Decisions

### 1. Two-Phase (Draft → Render)
Video rendering is expensive (Playwright screenshots + ffmpeg encoding). Two-phase means you only pay that cost after approving the content.

**Why?** If the LLM generates a poor slide structure, you catch it at draft review — no time wasted rendering bad slides.

### 2. Server-Side Rendering
The entire video is produced on the backend, not in the browser.

**Why?** Consistent output regardless of client device. No browser-side video encoding. The frontend just streams the finished MP4.

### 3. Opt-In via Environment Flag
`OPEN_NOTEBOOK_ENABLE_VIDEO=true` is required. Off by default.

**Why?** Playwright + Chromium adds ~300MB to the Docker image. Most deployments won't use video generation — don't make everyone pay that cost.

### 4. ffmpeg for Assembly
No Python video library needed — ffmpeg handles image-to-video conversion, concatenation, and codec selection natively.

**Why?** ffmpeg is already available (transitive dependency of `podcast-creator` → `moviepy`). No new binary dependency.

### 5. Inline CSS, No Build Step
Slide HTML uses inline `<style>` blocks, not Tailwind CSS.

**Why?** Tailwind requires a PostCSS build step. Server-side HTML rendering needs static, self-contained styles — inline CSS is the simplest path.

---

## System Requirements (Video Only)

| Component | Requirement | Notes |
|-----------|------------|-------|
| **Chromium** | Installed via Playwright | `playwright install chromium` |
| **ffmpeg** | Already available | Transitive dependency, no action needed |
| **TTS model** | Any configured provider | OpenAI, Google, ElevenLabs, or local TTS |
| **Disk space** | ~500MB per 10-min video | MP4 files can be large; videos stored in `data/videos/` |
| **Memory** | ~2GB during render | Playwright + ffmpeg peak memory |

---

## Cost Considerations

```
10-slide, 8-minute video:

  LLM (slides + narration):  ~5,000 tokens output  (~$0.08 with GPT-4o)
  TTS (8 min narration):     ~$0.12 (Google TTS)
  Render (Playwright + ffmpeg): Free (local)
                            ────────────────────
  Total:                     ~$0.20 per video
```

With Ollama + local TTS: **Free** (but slower rendering).

---

## Privacy & Data

- **Content to LLM/TTS**: Source content and narration sent to configured providers. Use local LLM + local TTS for full privacy.
- **Render processing**: Playwright and ffmpeg run locally — no external service involved in video assembly.
- **Storage**: Video MP4 files stored in `data/videos/` alongside your notebook data.

---

## How Videos Fit Into Your Workflow

```
1. Build notebook (add sources)
   ↓
2. Generate report or presentation (structure findings)
   ↓
3. Generate video (create shareable overview)
   ├─→ Review draft (slides + narration)
   ├─→ Edit narration text
   ├─→ Approve & render
   └─→ Download or stream MP4
   ↓
4. Share with stakeholders (briefing, update, overview)
   ↓
5. Deep dive via report/presentation (for those who want detail)
```

The video is the top-of-funnel: grab attention, provide overview, route to deeper content.

---

## Summary

**Videos turn research into shareable, narrated overviews:**

- Two-phase generation: review before rendering
- AI narration with any configured TTS provider
- Styled slides using the theme system
- Standard MP4 output — plays anywhere
- Opt-in to keep Docker image lean
- All rendering is local (no cloud video service)
