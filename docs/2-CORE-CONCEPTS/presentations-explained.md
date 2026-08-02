# Presentations Explained - Research as Slide Decks

Presentations turn your notebook sources into structured slide decks with speaker notes, visual themes, and PPTX export.

---

## Why Presentations Matter

### The Problem

Communicating research often means standing in front of people:

```
Research → Build slides → Write speaker notes → Design visuals → Present
```

Building slides is time-consuming and rarely about the content — most of the effort goes into layout, design, and formatting.

### The Solution

Generate a complete slide deck from your notebook sources in one step, then refine, reorder, and present.

```
Before:
  Research pile → Open PowerPoint → Design template → Write slides → Format → Tweak → Present
  (1-3 hours for a 10-slide deck)

After:
  Research pile → Generate presentation → Review & edit → Export or present
  (5-10 minutes to a usable draft)
```

---

## What Makes It Special

| Capability | Why It Matters |
|---|---|
| **Content-driven** | Slides are built from your sources — not your memory of them |
| **Speaker notes included** | Every slide gets presenter notes so you know what to say |
| **Visual themes** | Each slide gets a theme color from a curated palette based on content mood |
| **Reorder freely** | Drag-and-drop to rearrange slides after generation |
| **PPTX export** | Download as a native PowerPoint file — works in PowerPoint, Google Slides, Keynote |
| **In-browser presenter mode** | Present directly from Open Notebook with speaker notes hidden from audience |

---

## How Presentation Generation Works

### Stage 1: Content Selection

Choose which sources and notes feed the presentation:

```
Notebook → Source A: Market analysis report
         → Source B: Competitor landscape
         → Note: "Strategic recommendations"
         → Note: "Executive summary points"
```

### Stage 2: Structure Planning

The LLM analyzes your content and proposes a logical slide structure:

```
PRESENTATION: "Q3 Market Analysis"

1. Title Slide
   Title + Subtitle

2. Executive Summary
   Key takeaways in bullet points

3. Market Overview
   Market size, growth, trends

4. Competitive Landscape
   Top 5 competitors, positioning

5. Customer Insights
   Survey results, pain points

6. Strategic Opportunities
   Where we can win

7. Risk Analysis
   Key threats and mitigations

8. Financial Projections
   Revenue forecast, assumptions

9. Recommendations
   Actionable next steps

10. Q&A / Closing
```

### Stage 3: Per-Slide Generation

Each slide is generated independently with parallel fan-out:

```
Slide 1: AI generates title + subtitle
Slide 2: AI extracts executive summary from notes
Slide 3: AI structures market data from Source A
Slide 4: AI analyzes competitors from Source B
...
```

Each slide contains:
```
Slide {
  title: "Competitive Landscape"
  subtitle: "Top 5 competitors and their market positions"
  bullets: [
    "Company A: Market leader (35% share), strength in enterprise",
    "Company B: Fastest growing (25% YoY), threat in mid-market",
    "Company C: Niche player, premium positioning",
    "Company D: New entrant, aggressive pricing",
    "Company E: Legacy incumbent, declining share"
  ]
  speaker_notes: "When discussing Company B, highlight their recent Series C
    funding of $50M which could accelerate their growth. Also note that our
    competitive advantage in the enterprise segment remains strong — mention
    the Fortune 500 case study from page 4 of the market report."
  theme: "OCEAN"
}
```

### Stage 4: Theme Assignment

Each slide gets a visual theme from a curated palette:

```
Themes:
  SLATE    — Dark, professional (strategy, data)
  OCEAN    — Cool, analytical (market analysis, research)
  FOREST   — Growth, sustainability (opportunities, projections)
  PLUM     — Creative, distinctive (vision, innovation)
  BOREALIS — Bold, futuristic (technology, trends)
  SOLAR    — Warm, urgent (risks, calls-to-action)
  SLIDE    — Clean, neutral (default, general)
```

The LLM picks themes based on slide content, but you can override any slide's theme in the editor.

### Stage 5: Export or Present

```
Completed presentation:
  ├─→ Review & edit slides in browser
  ├─→ Reorder with drag-and-drop
  ├─→ Export to PPTX (PowerPoint/Google Slides/Keynote)
  └─→ Present directly (browser fullscreen, speaker notes panel)
```

---

## Slide Structure: Why Structured Data

Slides are stored as structured data (title, subtitle, bullet list, speaker notes), not free-form markdown. This is deliberate:

| Approach | Pros | Cons |
|----------|------|------|
| **Markdown slides** | Flexible, familiar | Hard to map to PPTX, inconsistent formatting |
| **Structured data** | Clean PPTX export, predictable formatting, easy to edit per-field | Less flexible for unusual layouts |

The structured approach ensures PPTX export produces clean, professional slides every time — no formatting drift.

---

## Presenter Mode

When presenting from Open Notebook:

```
┌─────────────────────────────────────┐
│            SLIDE VIEW               │  ← Audience sees this
│                                     │
│     Competitive Landscape           │
│     Top 5 competitors...            │
│                                     │
│     • Company A: 35% share          │
│     • Company B: 25% YoY growth     │
│     • Company C: Niche player       │
│                                     │
├─────────────────────────────────────┤
│ SPEAKER NOTES (hidden from audience)│  ← Only you see this
│                                     │
│ When discussing Company B, mention  │
│ their recent Series C funding of    │
│ $50M. Reference the Fortune 500     │
│ case study on page 4 of the report. │
│                                     │
│ Next: Financial Projections →       │
├─────────────────────────────────────┤
│       Slide 4 of 10    ◀  ▶        │
└─────────────────────────────────────┘
```

Keyboard controls: `←` `→` to navigate, `Esc` to exit fullscreen.

---

## Key Architecture Decisions

### 1. Separate Slide Records
Each slide is an independent record in the database, not a JSON blob inside the presentation.

**Why?** Individual slides can be regenerated, reordered, and edited independently. The API can operate on a single slide without reading the entire presentation.

### 2. No Markdown in Slides
Bullets are stored as `list[str]`, not markdown text.

**Why?** Clean, predictable PPTX export. A bullet list in Python maps directly to bullet paragraphs in PowerPoint. No markdown parsing ambiguity.

### 3. Server-Side PPTX Generation
PPTX export uses `python-pptx` on the backend — the browser downloads a ready-to-use file.

**Why?** No browser-side Office format handling. Works on any device — download on mobile, present on desktop.

---

## Cost Considerations

```
10-slide presentation with speaker notes:

  Structure planning:   1 LLM call  (~500 tokens)
  Per-slide:           10 LLM calls (~300 tokens each)
  Theme assignment:     1 LLM call  (~200 tokens)
                       ───────────────────────────
  Total:              ~3,700 tokens output

With GPT-4o:   ~$0.06
With Claude:    ~$0.12
With Ollama:    Free (local)
```

PPTX export is free — `python-pptx` runs locally.

---

## Privacy & Data

- **Content to LLM**: Source content sent to your configured LLM for slide generation. Use local LLMs for sensitive content.
- **Export**: PPTX generation is local — no external service.
- **Storage**: Slides and speaker notes stored in your SurrealDB database.

---

## How Presentations Fit Into Your Workflow

```
1. Build notebook (add sources)
   ↓
2. Chat/Ask (explore content)
   ↓
3. Generate presentation (structure findings as slides)
   ↓
4. Review, edit, reorder (refine the deck)
   ↓
5. Export to PPTX (share with team)
   OR
6. Present directly (in-browser, speaker notes)
```

---

## Summary

**Presentations transform research into communication-ready slide decks:**

- Generate structured slides with speaker notes from any notebook
- Edit, reorder, and customize before presenting
- Export to PowerPoint format for any presentation tool
- Present directly from the browser with hidden speaker notes
- All generation is provider-agnostic — use any configured LLM
