# Installing Open Notebook Deliverable Studio

This guide covers installing the deliverable studio features: enhanced podcasts, reports, presentations, and videos. These features ship as part of the next Open Notebook release.

---

## Before You Install

### Check Your Current Version

```bash
# Docker:
docker compose exec open_notebook cat /app/pyproject.toml | grep version

# Source:
grep version pyproject.toml
```

Requirements: Open Notebook **v1.15.0** or later (the deliverable studio release).

### Backup Your Data

Always back up before upgrading:

```bash
# Docker:
docker compose down
tar -czf open-notebook-backup-$(date +%Y%m%d).tar.gz notebook_data/ surreal_data/
docker compose up -d

# Source:
tar -czf open-notebook-backup-$(date +%Y%m%d).tar.gz data/
```

---

## Option A: Docker Compose (Recommended)

### Step 1: Pull the Latest Image

```bash
docker compose pull
```

Or if you need the development build (pre-release):

```bash
# In docker-compose.yml, change:
# image: lfnovo/open_notebook:v1-latest
# To:
# image: lfnovo/open_notebook:v1-dev
docker compose pull
```

### Step 2: Update Environment Variables

Add to your `docker-compose.yml` under the `open_notebook` service `environment:` section:

```yaml
services:
  open_notebook:
    environment:
      # Required — already present:
      - OPEN_NOTEBOOK_ENCRYPTION_KEY=your-secret-key
      - SURREAL_URL=ws://surrealdb:8000/rpc
      - SURREAL_USER=root
      - SURREAL_PASSWORD=your-password
      - SURREAL_NAMESPACE=open_notebook
      - SURREAL_DATABASE=open_notebook

      # New — for video generation (optional, off by default):
      - OPEN_NOTEBOOK_ENABLE_VIDEO=true
      # Keep worker concurrency low when video is enabled:
      - OPEN_NOTEBOOK_WORKER_MAX_TASKS=2
```

| Variable | Required? | Purpose |
|----------|-----------|---------|
| `OPEN_NOTEBOOK_ENABLE_VIDEO` | No | Set to `true` to enable video generation. Off by default (~300MB smaller image). |
| `OPEN_NOTEBOOK_WORKER_MAX_TASKS` | No | Reduce to 2-3 if enabling video — prevents multiple video renders from consuming all resources. |

All other deliverable features (reports, presentations, enhanced podcasts) require **no new environment variables** — they work out of the box with your existing configuration.

### Step 3: Recreate the Container

```bash
docker compose up -d
```

On first startup with `OPEN_NOTEBOOK_ENABLE_VIDEO=true`, the container installs Playwright + Chromium (~300MB download, cached on your data volume). This only happens once. Check progress:

```bash
docker compose logs open_notebook | grep -i "playwright\|chromium"
```

### Step 4: Verify Installation

```bash
# Check the container is healthy:
docker compose ps

# Check API health:
curl http://localhost:5055/health
```

Open the UI at `http://localhost:8502`. You should see:
- **Podcasts** — Generate dialog now has Draft/Review phases
- **Reports** — New "Generate Report" option in notebook dropdown
- **Presentations** — New "Generate Presentation" option
- **Videos** — New "Generate Video" option (only if `OPEN_NOTEBOOK_ENABLE_VIDEO=true`)

### Step 5: Migrate Credentials (First Time Only)

If you previously used environment variables for AI provider keys:

1. Go to **Settings → API Keys**
2. Click **Migrate to Database** to import existing env var credentials
3. Remove the deprecated env vars from `docker-compose.yml`

If you already use the Settings UI credential system: no action needed.

---

## Option B: From Source (Development)

### Step 1: Pull Latest Code

```bash
cd open-notebook
git pull origin main
```

### Step 2: Install New Python Dependencies

```bash
uv sync
```

This installs the new packages:
- `pypandoc` + `pypandoc_binary` — report export (PDF, DOCX, HTML, etc.)
- `weasyprint` — PDF generation
- `python-pptx` — PowerPoint export for presentations

### Step 3: Install Video Dependencies (Optional)

Only if you want video generation:

```bash
# Set the environment variable:
export OPEN_NOTEBOOK_ENABLE_VIDEO=true

# Install Playwright + Chromium:
uv run playwright install chromium
```

### Step 4: Rebuild the Frontend

```bash
cd frontend
npm ci
npm run build
cd ..
```

### Step 5: Update Environment Variables

In your `.env` file:

```bash
# Required (already present):
OPEN_NOTEBOOK_ENCRYPTION_KEY=your-secret-key
SURREAL_URL=ws://localhost:8000/rpc
SURREAL_USER=root
SURREAL_PASSWORD=root
SURREAL_NAMESPACE=open_notebook
SURREAL_DATABASE=open_notebook

# New — for video generation (optional):
OPEN_NOTEBOOK_ENABLE_VIDEO=true
OPEN_NOTEBOOK_WORKER_MAX_TASKS=2
```

### Step 6: Restart All Services

```bash
# Stop everything if running:
make stop-all

# Start in order (each depends on the one below):
make database        # 1. SurrealDB
make api             # 2. FastAPI — schema migrations run automatically
make worker-start    # 3. Background job worker
make frontend        # 4. Next.js frontend on port 3000
```

Or all at once:
```bash
make start-all
```

### Step 7: Verify

```bash
# Check API health:
curl http://localhost:5055/health

# Verify migration ran (check logs):
# You should see: "All migrations up to date" or "Migration 24-26 applied"

# Check worker is processing:
make status
```

Open the UI at `http://localhost:3000`.

---

## Feature-Specific Setup

### Reports (No Additional Setup)

Reports work out of the box. The only requirements are:
- A configured LLM model (any provider — OpenAI, Anthropic, Ollama, etc.)
- At least one notebook with processed sources

Export to PDF/DOCX/HTML/EPUB/LaTeX/ODT/plain text requires no configuration — `pypandoc_binary` is self-contained.

### Presentations (No Additional Setup)

Presentations work out of the box with any configured LLM. PPTX export uses `python-pptx` — no configuration needed.

### Enhanced Podcasts (No Additional Setup)

The new two-phase generation (draft → render) and voice preview are automatic. If voice preview doesn't work, verify your TTS model is properly configured in **Settings → Models**.

### Videos

Requires explicit opt-in. After enabling:

1. Verify Chromium is installed:
   ```bash
   # Docker:
   docker compose exec open_notebook playwright install --dry-run chromium

   # Source:
   uv run playwright install --dry-run chromium
   ```

2. Check disk space for video output directory:
   ```bash
   # Created automatically — verify it exists:
   ls -la data/videos/
   ```

3. If the "Generate Video" option doesn't appear in the UI:
   ```bash
   # Check the env var is set inside the container:
   docker compose exec open_notebook env | grep ENABLE_VIDEO
   # Should return: OPEN_NOTEBOOK_ENABLE_VIDEO=true
   ```

---

## Rollback

If you need to revert to the previous version:

```bash
# Docker — specify the previous version tag:
# In docker-compose.yml, change:
# image: lfnovo/open_notebook:v1-latest
# To:
# image: lfnovo/open_notebook:v1.14.0
docker compose down && docker compose up -d

# Source:
git checkout v1.14.0
uv sync
cd frontend && npm ci && npm run build && cd ..
make stop-all && make start-all
```

Then restore from your backup if needed:
```bash
docker compose down
rm -rf notebook_data/ surreal_data/
tar -xzf open-notebook-backup-YYYYMMDD.tar.gz
docker compose up -d
```

---

## Expected New Data Files

After installing and using the deliverable studio, your data directories will contain:

```
notebook_data/  (or data/ for source installs)
├── uploads/           (existing)
├── podcasts/          (existing — podcast MP3 files)
│   └── episodes/
├── sqlite-db/         (existing — chat checkpoints)
│   └── checkpoints.sqlite
├── tiktoken-cache/    (existing)
├── videos/            (new — video MP4 files)
│   └── *.mp4
└── .cache/            (existing — opt-in runtime installs)

surreal_data/  (Docker only)
└── mydatabase.db      (existing — SurrealDB RocksDB, now includes
                        report, presentation, slide, video tables)
```

---

## Troubleshooting

### "Report export failed — pandoc not found"

```bash
# Verify pypandoc_binary is installed:
docker compose exec open_notebook python -c "import pypandoc; print(pypandoc.get_pandoc_version())"

# Source:
uv run python -c "import pypandoc; print(pypandoc.get_pandoc_version())"
```

### "PDF export produces empty file"

```bash
# Verify weasyprint system deps are installed:
docker compose exec open_notebook python -c "import weasyprint; print('OK')"

# If missing (rare in Docker — the image should include them):
# The Dockerfile needs: apt-get install -y libpango-1.0-0 libcairo2
```

### "Video render stuck on 'rendering' for 30+ minutes"

```bash
# Check worker logs:
docker compose logs open_notebook | grep "video"

# Common causes:
# 1. Chromium not installed: playwright install chromium
# 2. Disk full: df -h
# 3. Memory exhausted: Reduce slide count and retry
```

### "Migration failed on startup"

Schema migrations (24: reports, 25: presentations+slides, 26: videos) run automatically on API startup. If they fail:

```bash
# Check migration logs:
docker compose logs open_notebook | grep -i migrat

# Manual migration (source only — Docker runs automatically):
uv run python -c "from open_notebook.database.async_migrate import run_migrations; import asyncio; asyncio.run(run_migrations())"
```

### "Feature X doesn't appear in the UI"

The deliverable studio features appear only when:
- A notebook has processed sources
- A configured LLM model exists (Settings → Models)
- For videos specifically: `OPEN_NOTEBOOK_ENABLE_VIDEO=true`

Check all three before troubleshooting further.

---

## What Changed from v1.14

| Feature | v1.14 | v1.15 (Deliverable Studio) |
|---------|-------|---------------------------|
| **Podcasts** | Single-phase generation | Two-phase (draft → review → render), voice preview, brief proposal |
| **Reports** | Not available | Generate, edit, version, export to 7 formats |
| **Presentations** | Not available | Generate, edit slides, speaker notes, PPTX export, presenter mode |
| **Videos** | Not available | Generate narrated MP4 overviews (opt-in), two-phase draft/render |
| **New env vars** | n/a | `OPEN_NOTEBOOK_ENABLE_VIDEO` |
| **New dependencies** | n/a | `pypandoc`, `pypandoc_binary`, `weasyprint`, `python-pptx`, `playwright` (conditional) |
| **Database** | 23 migrations | 26 migrations (new tables: report, presentation, slide, video) |
