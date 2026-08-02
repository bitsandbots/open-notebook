# Reports Explained - Research as Structured Documents

Reports turn your notebook sources into structured, exportable documents with citations, versioning, and multi-format output.

---

## Why Reports Matter

### The Problem

Research doesn't end at understanding. You need to **communicate findings**:

```
Research → Understanding
         → Writing the report
         → Formatting the output
         → Distributing to stakeholders
         → Revising as research evolves
```

Each step adds friction. Formatting alone can consume hours.

### The Solution

Generate a complete, citation-backed report from your notebook sources in one step, then refine and export to whatever format your audience needs.

```
Before (Manual):
  Research pile → Write draft → Format → Export → Distribute
  (Hours of manual labor)

After (Open Notebook):
  Research pile → Generate report → Review & edit → Export → Distribute
  (Minutes of AI-assisted work)
```

---

## What Makes It Special

| Capability | Why It Matters |
|---|---|
| **Source-grounded** | Every claim traces back to your sources — no hallucinated facts |
| **Editable content** | Generated text is a starting point, not a final answer. Edit freely |
| **Multi-format export** | PDF, DOCX, HTML, EPUB, LaTeX, ODT, plain text — one report, any format |
| **Version groups** | Revise without losing history. Track changes across report iterations |
| **Section-level revision** | Change one section without regenerating the entire report |
| **Provider-agnostic** | Works with any configured LLM — OpenAI, Anthropic, Ollama, etc. |

---

## How Report Generation Works

### Stage 1: Content Selection

Choose which notebook sources feed the report:

```
Notebook → Source A (full content)
         → Source B (insights only)
         → Source C (full content)
         → Note: "Key findings" (included)
```

### Stage 2: Structure Planning

The LLM analyzes your sources and proposes a report structure:

```
REPORT: "AI Safety Landscape 2026"

1. Executive Summary
   Key findings in 2-3 paragraphs

2. Introduction
   Context and scope of the analysis

3. Core Approaches
   ├─ 3.1 Alignment via Reward Modeling
   ├─ 3.2 Constitutional AI
   └─ 3.3 Debate and Oversight

4. Comparative Analysis
   Strengths and weaknesses of each approach

5. Open Questions
   Unsolved problems and future directions

6. Recommendations
   Actionable conclusions
```

### Stage 3: Section Generation

Each section is generated independently using parallel fan-out:

```
Section 1 → LLM generates executive summary from all sources
Section 2 → LLM writes introduction with context
Section 3.1 → LLM writes from Source A + Source C
Section 3.2 → LLM writes from Source B
Section 3.3 → LLM writes from Source A's debate analysis
Section 4 → LLM synthesizes comparison across all sections
Section 5 → LLM identifies gaps from all sources
Section 6 → LLM generates recommendations
```

Parallel generation means a 6-section report takes roughly the time of one LLM call, not six.

### Stage 4: Synthesis & Flow

The generated sections are combined and the LLM ensures:

- Consistent tone and terminology across sections
- Natural transitions between topics
- No duplicated information
- Proper introduction and conclusion framing

### Stage 5: Export

The final markdown is converted to your chosen format:

```
Markdown → Pandoc → DOCX (editable in Word)
                  → HTML (web-ready)
                  → EPUB (e-book reader)
                  → LaTeX (academic publishing)
                  → ODT (LibreOffice)
                  → Plain text

Markdown → Pandoc → HTML → WeasyPrint → PDF (print-ready)
```

---

## Versioning: Reports as Living Documents

Research evolves. Reports should too.

### Version Groups

When you revise a report, a new version is created in the same group:

```
Report: "AI Safety Analysis v1"
  ├─ report_group_id: "abc-123"
  └─ Generated: June 2026

Report: "AI Safety Analysis v2"
  ├─ report_group_id: "abc-123"  (same group)
  ├─ parent_id: v1
  └─ Revised: July 2026

Report: "AI Safety Analysis v3"
  ├─ report_group_id: "abc-123"  (same group)
  ├─ parent_id: v2
  └─ Revised: August 2026
```

### Section-Level Revision

Updated a source? The LLM identifies which sections changed and regenerates only those — untouched sections are preserved byte-for-byte:

```
Sources updated → LLM diffs sections
                → Sections 2, 3.2 changed → Regenerate only 2 and 3.2
                → Sections 1, 3.1, 3.3, 4-6 unchanged → Keep as-is
```

This avoids the cost of regenerating an entire report for a single section change.

---

## Export Formats: Choose by Audience

| Format | Best For | Editable? |
|--------|----------|-----------|
| **PDF** | Distribution, printing, sharing | No (read-only) |
| **DOCX** | Collaborative editing in Word/Google Docs | Yes |
| **HTML** | Web publishing, embedding | Yes (source) |
| **EPUB** | E-readers, tablets, mobile reading | Limited |
| **LaTeX** | Academic publishing, templated output | Yes (source) |
| **ODT** | LibreOffice/OpenOffice workflows | Yes |
| **Plain Text** | Copy-paste, integration with other tools | Yes |
| **Markdown** | Further AI processing, version control | Yes |

---

## Key Architecture Decisions

### 1. Server-Side Export
All format conversions happen on the backend — no browser dependencies.

**Why?** Consistent output regardless of client device. PDF generation doesn't require a browser with PDF support.

### 2. Markdown as Intermediate
All generated content is stored as markdown, not a proprietary format.

**Why?** Markdown is human-readable, version-control-friendly, and convertible to any output format. You're never locked into one export target.

### 3. Pandoc + WeasyPrint for PDF
PDF is produced via Pandoc (markdown → HTML) then WeasyPrint (HTML → PDF) — no TeX distribution required.

**Why?** XeLaTeX/pdflatex would add ~200MB to the Docker image. WeasyPrint is ~5MB, Python-native, and produces excellent results for document-style output.

### 4. Version Groups, Not Overwrites
New revisions create new records with a shared group ID, not in-place edits.

**Why?** You can always go back. Compare v2 against v1. Track how your understanding evolved with your research.

---

## Cost Considerations

Report generation costs are LLM inference costs only:

```
6-section report, ~3,000 words:
  Structure planning:   1 LLM call  (~1,000 tokens)
  Per-section:         6 LLM calls (~500 tokens each)
  Synthesis:           1 LLM call  (~500 tokens)
                       ─────────────────────────────
  Total:              ~4,500 tokens output

With GPT-4o:   ~$0.07
With Claude:    ~$0.14
With Ollama:    Free (local)
```

Export is free — Pandoc and WeasyPrint are local tools with no API costs.

---

## Privacy & Data Considerations

- **Content to LLM**: Source content is sent to your configured LLM provider for generation. Choose local LLMs (Ollama) for sensitive research.
- **Export processing**: All format conversion happens locally via Pandoc/WeasyPrint — no external service involved.
- **Stored content**: Reports are stored in your SurrealDB database alongside the rest of your notebook data.

---

## How Reports Fit Into Your Workflow

```
1. Build notebook (add sources)
   ↓
2. Chat/Ask (explore content)
   ↓
3. Generate report (structure findings)
   ↓
4. Review & edit (refine content)
   ↓
5. Revise as research evolves (version groups)
   ↓
6. Export (share with audience)
```

Reports complement chat and ask: chat explores, reports communicate.

---

## Summary

**Reports transform research into communication:**

- Generate structured, citation-backed documents from notebook sources
- Edit and refine before exporting
- Export to any format your audience needs
- Version as your research evolves — never lose previous work
- All processing stays local except the LLM generation call
