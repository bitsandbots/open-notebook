# Creating Reports - Generate Structured Documents

Turn notebook sources into structured, exportable documents with AI-generated content, citations, and multi-format export.

---

## Quick-Start: Your First Report (3 Minutes)

```
1. Go to your notebook
2. Click "Generate Report"
3. Select sources to include
4. Add instructions (optional — topic, audience, length)
5. Click "Generate"
6. Wait 30-90 seconds
7. Review the generated report
8. Export to your preferred format
9. Done!
```

That's the minimum. Let's make it better.

---

## Step-by-Step: The Complete Workflow

### Step 1: Prepare Your Notebook

```
Before generating, make sure:

✓ Sources are added and processed
  (Green "Ready" status)

✓ You have at least 2-3 sources
  (Single-source reports are possible but thin)

✓ You know your report's purpose
  (Executive summary? Detailed analysis? Recommendations?)

✓ Notes with key insights are available
  (Optional but helpful — notes feed the report structure)

Typical preparation: 5 minutes
```

### Step 2: Choose Content

```
Click "Generate Report"

Select which sources to include:
☑ Source A: Market analysis report
☑ Source B: Customer survey results
☑ Source C: Competitor landscape
☐ Source D: Legacy data (not relevant)
✓ Note: "Strategic recommendations"

Content tips:
- 3-6 sources produces a focused, thorough report
- Include notes with your own insights — they guide the structure
- Exclude sources that don't relate to your report's topic

Recommended: 3-5 sources per report
```

### Step 3: Configure Generation

```
Report Configuration:
├─ Report name: "Q3 Market Analysis"
├─ Instructions: "Focus on competitive positioning and growth opportunities.
│                  Audience is the executive team. Keep it concise — 2-3 pages.
│                  Include specific revenue numbers where available."
└─ Style: Business (options: Academic, Business, Casual, Technical)

Instructions guide the LLM but don't constrain it completely.
Be specific about audience, length, and focus areas.
```

### Step 4: Review and Edit

```
Generated report appears in the editor:

┌─────────────────────────────────────────────┐
│ Q3 Market Analysis                          │
│                                             │
│ ## Executive Summary                        │
│                                             │
│ The Q3 market analysis reveals three key    │
│ findings: revenue growth of 18% YoY...      │
│                                             │
│ ## Market Overview                          │
│                                             │
│ The total addressable market expanded from  │
│ $12B to $15B in Q3...                       │
│ [Edit] [Regenerate section]                 │
│                                             │
│ ## Competitive Landscape                    │
│ ...                                         │
└─────────────────────────────────────────────┘

Actions:
- Edit any section inline (markdown editor)
- "Regenerate section" to redo a single section with new instructions
- "Add section" to insert a new topic
- "Re-order sections" to restructure
```

### Step 5: Section-Level Revision

If you update one source and want to refresh the report:

```
1. Edit the report, find the affected section
2. Click "Regenerate section"
3. Provide new instructions: "Update with Q4 data from the new source"
4. Only that section is regenerated
5. All other sections remain unchanged

This avoids the cost and unpredictability of regenerating
the entire report for a single update.
```

### Step 6: Version Your Report

```
When your research evolves:

1. Click "Create New Version"
2. The current report is saved as v1
3. A new draft (v2) is created in the same version group
4. Edit v2 with updated sources or new instructions
5. All versions are accessible from the report page

Version history:
  v3 — Q4 update, includes new competitor data (December 2026)
  v2 — Revised after board feedback (November 2026)
  v1 — Initial draft (October 2026)
```

### Step 7: Export

```
Click "Export" → Choose format:

PDF     — For distribution, printing, sharing (read-only)
DOCX    — For collaborative editing in Word/Google Docs
HTML    — For web publishing, embedding
EPUB    — For e-readers, tablets
LaTeX   — For academic publishing, templated workflows
ODT     — For LibreOffice/OpenOffice
Plain   — For integration with other tools

Download starts automatically — no additional processing needed.
```

---

## Which Export Format for Which Audience?

```
Executive summary for busy stakeholders  → PDF
Draft for team collaboration             → DOCX
Blog post or web content                 → HTML
Long-form reading on devices             → EPUB
Academic journal submission              → LaTeX
Further AI processing / notes            → Plain text / Markdown
```

---

## Tips for Better Reports

### Write Good Instructions

```
Good instructions:
"Focus on the competitive threats from new entrants in the Asian market.
 Include specific market share data from Sources A and B.
 Target audience is the VP of Strategy — keep it strategic, not tactical.
 3-4 pages max."

Bad instructions:
"Make a report about the market."
```

The more specific your instructions, the better the LLM can target the content.

### Choose the Right Sources

```
Better: 3 sources on the same topic
  Source A: Market report
  Source B: Customer interviews
  Source C: Analyst coverage

Worse: 10 sources on unrelated topics
  Source A: Market report
  Source B: Technical paper on ML
  Source C: Historical data from 2019
  Source D: Personal notes
  ... (report becomes unfocused)
```

### Review Before Exporting

```
Always:
- Read the executive summary — does it capture the key message?
- Check data points — are numbers accurate to the sources?
- Review structure — does the flow make sense?
- Edit tone — does it match your audience?

The generated report is a strong draft, not a finished product.
Budget 5-10 minutes for review before sharing.
```

---

## Common Issues and Solutions

### Report Is Too Long/Short

**Problem**: Generated report doesn't match desired length.

**Solutions**:
```
Too long:
  - Reduce source count (fewer sources = shorter report)
  - Specify in instructions: "Keep to 2 pages maximum"
  - Use Summarize transformation on sources first

Too short:
  - Include more sources
  - Specify in instructions: "Write a comprehensive 5-page report"
  - Check that sources have enough content (thin sources → thin report)
```

### Sections Are Repetitive

**Problem**: Different sections contain the same information.

**Solutions**:
```
- Regenerate the overlapping sections with focused instructions
- In instructions, specify which source feeds which section
- Edit manually to remove duplication (it's markdown — easy to fix)
```

### Data Points Are Wrong

**Problem**: Generated report contains inaccurate numbers.

**Solutions**:
```
- Verify against sources (use Chat to ask "What was the revenue in Source A?")
- Edit the data point manually
- Regenerate the section with: "Use exact numbers from the sources, do not estimate"
```

### Generation Failed

**Problem**: "Report generation failed"

**Solutions**:
```
1. Check LLM provider connection (Settings → API Keys → Test Connection)
2. Reduce source count (too much content may exceed context window)
3. Check source processing status (some sources may be unprocessed)
4. Try with a different LLM model (some handle long context better)
```

---

## Cost Breakdown Example

```
Generate a 6-section report (~3,000 words) with GPT-4o:

  Structure planning:    ~$0.01
  Section generation:    ~$0.04 (6 sections × ~$0.007 each)
  Synthesis & polish:    ~$0.01
                        ──────
  Total:                ~$0.06 per report

With Anthropic Claude:  ~$0.12 per report
With Ollama (local):    Free
```

Export to any format: **Free** (Pandoc + WeasyPrint run locally)

Revisions (regenerating 1-2 sections): proportionally cheaper — you only pay for changed sections.

---

## Before Generation Checklist

- [ ] Sources are processed and ready
- [ ] You've selected 3-5 relevant sources
- [ ] Instructions are specific (audience, focus, length)
- [ ] Style matches your audience (Academic/Business/Casual/Technical)
- [ ] LLM provider is configured and tested

### After Generation
- [ ] Executive summary captures key message
- [ ] Data points are verified against sources
- [ ] Structure flows logically
- [ ] Tone matches audience expectations
- [ ] Export to desired format
- [ ] Create version if this is an update

---

## Use Cases

### Executive Briefing
```
Report: "Q3 Market Analysis"
Sources: Market reports, competitor data, customer surveys
Audience: Executive team
Format: PDF, 3-4 pages
Style: Business — concise, data-driven, action-oriented
Export: PDF for board deck, DOCX for collaborative review
```

### Academic Literature Review
```
Report: "Survey of Alignment Approaches"
Sources: 10+ papers from your notebook
Audience: Research community
Format: PDF or LaTeX, 10-15 pages
Style: Academic — formal, citation-heavy, comprehensive
Export: LaTeX for journal submission
```

### Internal Knowledge Transfer
```
Report: "Onboarding Guide: Our Tech Stack"
Sources: Architecture docs, meeting notes, design decisions
Audience: New team members
Format: HTML (internal wiki) or PDF
Style: Casual — accessible, explanatory, no jargon without definition
Export: HTML for wiki, DOCX for collaborative updates
```

### Client Deliverable
```
Report: "Engagement Findings & Recommendations"
Sources: Client data, interview transcripts, analysis notes
Audience: Client stakeholders
Format: PDF
Style: Business — professional, clear recommendations, supporting evidence
Export: PDF (final), DOCX (client may want to edit)
```

---

## Summary

Reports turn notebook research into structured, exportable documents:

1. **Select sources** — what content feeds the report
2. **Set instructions** — audience, focus, length, style
3. **Generate** — 30-90 seconds for a full report
4. **Review & edit** — refine the draft
5. **Version** — track changes as research evolves
6. **Export** — any format, any audience
