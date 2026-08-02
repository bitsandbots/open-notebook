# Creating Presentations - Generate Structured Slide Decks

Turn notebook sources into structured slide decks with speaker notes, visual themes, and PowerPoint export.

---

## Quick-Start: Your First Presentation (5 Minutes)

```
1. Go to your notebook
2. Click "Generate Presentation"
3. Select sources to include
4. Set slide count (5-30)
5. Choose a style (Professional, Casual, Academic, Pitch)
6. Click "Generate"
7. Review slides in the editor
8. Reorder or edit as needed
9. Export to PPTX or present directly
10. Done!
```

---

## Step-by-Step: The Complete Workflow

### Step 1: Prepare Content

```
Before generating:

✓ Sources are processed and ready
✓ You have a clear presentation goal
  (Team update? Client pitch? Conference talk?)
✓ Notes with key points are available
  (Notes become speaker notes — highly recommended)

Good preparation = better first draft.
```

### Step 2: Choose Content and Settings

```
Generate Presentation dialog:

Notebook: "Q3 Market Analysis"
Sources:
  ☑ Market report (source)
  ☑ Competitor data (source)
  ☑ Customer survey (source)
  ☐ Internal memo (not needed)

Settings:
  Slide count: 10
  Style: Professional
  Instructions: "Focus on growth metrics and competitive positioning.
                 Include specific data points from the sources.
                 Make it suitable for a 20-minute executive briefing."
```

### Step 3: Review the Generated Deck

```
Generated presentation appears in the slide editor:

┌─────────────────────────────────────────────────────┐
│ SLIDES                           │  SLIDE PREVIEW   │
│                                  │                  │
│ 1. Title Slide                   │  Market Overview │
│ 2. Executive Summary             │  Q3 performance  │
│ 3. Market Overview      ← active │                  │
│ 4. Growth Metrics                │  ▸ Revenue: +18% │
│ 5. Competitive Analysis          │  ▸ Customers: 2.4x│
│ 6. Customer Insights             │  ▸ ARPU: +$14    │
│ 7. Strategic Opportunities       │                  │
│ 8. Risk Factors                  │                  │
│ 9. Recommendations               │                  │
│ 10. Q&A                          │                  │
│                                  │                  │
│ [+ Add Slide]  [Reorder]         │                  │
└─────────────────────────────────────────────────────┘
```

Each slide shows:
- **Title** — main point
- **Subtitle** — context or timeframe
- **Bullets** — key points from sources
- **Speaker notes** — what to say (hidden from audience in presenter mode)

### Step 4: Edit and Refine

```
Editing a slide:

┌──────────────────────────────────────────────┐
│ Title:     Competitive Analysis              │
│ Subtitle:  Top 5 players and our position    │
│                                              │
│ Bullets:                                     │
│  ▸ Company A: 35% share, enterprise focus    │
│  ▸ Company B: 25% growth, mid-market threat  │
│  ▸ Company C: Niche premium player           │
│  ▸ Our position: #2 with 28% share           │
│  [+ Add bullet]                              │
│                                              │
│ Theme: [OCEAN ▼]  (SLATE/OCEAN/FOREST/...)   │
│                                              │
│ Speaker Notes:                               │
│  "When presenting this slide, start with     │
│   the market structure. Highlight our        │
│   growth vs. Company B's trajectory..."      │
└──────────────────────────────────────────────┘

You can edit:
- Title and subtitle text
- Individual bullet points
- Theme per slide (or use auto-assigned)
- Speaker notes (the most important part — edit these!)
```

### Step 5: Reorder Slides

```
Drag-and-drop to reorder:

Before:                          After:
1. Title                         1. Title
2. Executive Summary             2. Executive Summary
3. Market Overview               3. Growth Metrics      ← moved up
4. Growth Metrics                4. Market Overview     ← moved down
5. Competitive Analysis          5. Competitive Analysis
...

Click "Reorder" to enter drag mode, then drag slides
into your preferred order. Numbers update automatically.
```

### Step 6: Choose Your Export

```
Export options:

PPTX (PowerPoint):
  → Open in PowerPoint, Google Slides, Keynote
  → Fully editable — change fonts, layouts, add images
  → Speaker notes included as PowerPoint notes
  → Best for: Sharing with team, presenting in meeting rooms

Present in Browser:
  → Fullscreen slideshow mode
  → Keyboard navigation (← → arrows)
  → Speaker notes panel (hidden from audience)
  → Best for: Quick presentations, virtual meetings (share window)
```

### Step 7: Present

```
In-browser presenter mode:

What your audience sees (fullscreen):
┌────────────────────────────────────┐
│                                    │
│       Competitive Analysis         │
│       Top 5 players, our position  │
│                                    │
│   ▸ Company A: 35% share           │
│   ▸ Company B: 25% growth          │
│   ▸ Our position: #2 at 28%        │
│                                    │
│                           4 of 10  │
└────────────────────────────────────┘

What you see (speaker notes panel on your screen):
"When presenting this slide, start with the market
structure. Highlight our growth trajectory vs.
Company B. Then transition to strategic opportunities."

Keyboard: ← → to navigate, Esc to exit
```

---

## Theme System

Each slide gets a visual theme from a curated palette:

| Theme | Color Scheme | Best For |
|-------|-------------|----------|
| **SLATE** | Dark navy, light gray, blue accent | Strategy, data, analysis |
| **OCEAN** | Deep blue, ice, cyan accent | Market analysis, research |
| **FOREST** | Dark green, light green, green accent | Growth, sustainability, projections |
| **PLUM** | Deep purple, light purple, pink accent | Vision, innovation, creative |
| **BOREALIS** | Dark indigo, light gray, teal accent | Technology, trends, future |
| **SOLAR** | Dark amber, warm white, orange accent | Urgency, calls-to-action, risks |
| **SLIDE** | Light gray, dark text, blue accent | General purpose, clean default |

The LLM auto-assigns themes based on slide content. You can override any slide's theme in the editor.

---

## Tips for Better Presentations

### Write Good Instructions

```
Good instructions:
"Create a 12-slide pitch deck for our Series A fundraising.
 Focus on market opportunity, traction metrics, and competitive moat.
 Target audience: VCs familiar with B2B SaaS.
 Make data visual — every slide should have a number."

Bad instructions:
"Make a presentation."
```

### Keep Slides Scannable

```
Good slide:
  Title: Revenue Growth Accelerating
  Bullets:
  ▸ Q3 revenue: $45M (+18% YoY)
  ▸ Enterprise: +32%, SMB: +12%
  ▸ International: 5 new markets

Bad slide:
  Title: A Comprehensive Overview of Our Revenue Performance
         Across All Segments Including Historical Context
  Bullets:
  ▸ In the third quarter of fiscal year 2026, we observed a
    significant acceleration in revenue growth across all business
    units, with particularly strong performance in the enterprise
    segment which grew by approximately 32% year-over-year...
```

Slides support scanning, not reading. Keep bullets short.

### Use Speaker Notes Wisely

```
Speaker notes are where the detail lives:

Slide bullet: "Enterprise revenue: +32% YoY"
Speaker note: "The enterprise growth was driven by 3 new Fortune 500
  logos closed in Q3. Mention the Walmart deal specifically — it's
  our largest single contract at $8M ARR. The sales cycle for these
  deals averaged 4 months, down from 6 months in 2025 — our new
  enterprise playbook is working."

The slide shows the headline. You deliver the story.
```

### Choose the Right Slide Count

```
Pitch deck:        10-15 slides
Team update:        5-8 slides
Conference talk:   20-30 slides (rapid pace)
Executive briefing: 8-12 slides
Training session:   15-25 slides (slower pace)

Rule of thumb: 2-3 minutes per slide when presenting.
A 10-slide deck = 20-30 minute presentation.
```

---

## Common Issues

### Slides Have Too Much Text

**Problem**: Bullets are full sentences, not key points.

**Solutions**:
```
- Edit bullets to be scannable phrases
- Move explanatory text to speaker notes
- Regenerate with instruction: "Keep bullets short — 5-8 words max"
```

### Speaker Notes Are Thin

**Problem**: Speaker notes are generic or missing detail.

**Solutions**:
```
- Include notes in your content selection (notes feed speaker notes)
- Edit speaker notes directly — add talking points, context, transitions
- Regenerate with: "Include detailed speaker notes with data context"
```

### Theme Doesn't Match Content

**Problem**: Auto-assigned theme doesn't fit the slide.

**Solutions**:
```
- Click the theme dropdown on any slide to change it
- Manual override takes priority over auto-assignment
- Themes are cosmetic only — no re-generation needed
```

### PPTX Formatting Issues

**Problem**: Exported PPTX doesn't look right in PowerPoint.

**Solutions**:
```
- Open in Google Slides if PowerPoint formatting is off
  (Google Slides handles the PPTX differently)
- Adjust fonts after opening (themes carry colors, not fonts)
- The export is a starting point — expect to do minor formatting
  in PowerPoint (5-10 minutes for a 10-slide deck)
```

---

## Before Generation Checklist

- [ ] Sources are processed and ready
- [ ] You have 3-5 relevant sources selected
- [ ] Slide count is appropriate for your format
- [ ] Style matches your audience
- [ ] Key notes are included (for better speaker notes)
- [ ] Instructions are specific

### After Generation
- [ ] Each slide is scannable (bullets, not paragraphs)
- [ ] Speaker notes contain the detail
- [ ] Slide order flows logically
- [ ] Themes look appropriate (override any that don't fit)
- [ ] Export to PPTX or test presenter mode

---

## Use Cases

### Team Update
```
Presentation: "Weekly Product Update"
Slides: 6-8
Style: Casual
Sources: Meeting notes, ticket summaries, metrics dashboards
Export: PPTX (share in Slack), or present directly in standup
```

### Investor Pitch
```
Presentation: "Series A Pitch Deck"
Slides: 12-15
Style: Pitch
Sources: Market research, financial projections, competitive analysis
Export: PPTX, then customize in PowerPoint with charts and graphics
```

### Conference Talk
```
Presentation: "AI Safety: Current Approaches"
Slides: 25-30
Style: Academic
Sources: 10+ papers, your own notes and analysis
Export: PPTX for the conference AV system
```

### Training Session
```
Presentation: "New Hire Onboarding: Our Process"
Slides: 15-20
Style: Casual
Sources: Process docs, runbooks, team wiki
Export: PPTX for sharing, or present in browser during session
```

---

## Cost Example

```
10-slide presentation with speaker notes (GPT-4o):

  Structure planning:   ~$0.01
  Slide generation:     ~$0.03 (10 slides)
  Theme assignment:     ~$0.005
                       ──────
  Total:               ~$0.045 per presentation

With local LLM (Ollama): Free
```

PPTX export: **Free** (local processing)

---

## Summary

Presentations turn research into presentation-ready slide decks:

1. **Select sources and settings** — content, count, style
2. **Generate** — structured slides with speaker notes in 2-5 minutes
3. **Edit** — refine bullets, enhance speaker notes, reorder slides
4. **Theme** — auto-assigned or manual per-slide
5. **Export or present** — PPTX for sharing, browser for presenting
