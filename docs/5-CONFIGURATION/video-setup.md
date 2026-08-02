# Video Generation Setup

Video generation is **opt-in** to keep the Docker image lean. This guide covers enabling and configuring it.

---

## Quick Setup (Docker)

```bash
# 1. Add to your docker-compose.yml environment:
services:
  open_notebook:
    environment:
      - OPEN_NOTEBOOK_ENABLE_VIDEO=true

# 2. Recreate the container:
docker compose down && docker compose up -d
```

The first startup with video enabled installs Playwright and Chromium (~300MB download, cached on the `/app/data` volume). Subsequent startups are fast.

---

## Quick Setup (Local Development)

```bash
# 1. Set the environment variable:
export OPEN_NOTEBOOK_ENABLE_VIDEO=true

# 2. Install Playwright browsers:
playwright install chromium

# 3. Restart the API and worker:
make api
make worker-start
```

---

## What Gets Installed

| Component | Purpose | Size |
|-----------|---------|------|
| `playwright` | Python package for browser automation | ~5MB |
| Chromium (headless) | Renders slide HTML → PNG screenshots | ~300MB |
| `ffmpeg` | Audio/video assembly | Already present (transitive via `podcast-creator` → `moviepy`) |

The Chromium download is cached — you only pay the download time once.

---

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 2GB | 4GB+ |
| **Disk (for Chromium)** | ~350MB | 500MB |
| **Disk (per video)** | ~50-150MB | 500MB working space |
| **CPU** | 2 cores | 4+ cores |

Video rendering is CPU-intensive (Playwright screenshots + ffmpeg encoding). Longer videos = proportionally longer render times.

---

## Verifying Installation

After enabling video and restarting:

1. Open Open Notebook in your browser
2. Navigate to any notebook
3. You should see a "Generate Video" button/option
4. If the option is missing, check: `docker compose logs open_notebook | grep -i video`

---

## How Video Render Works

```
1. LLM generates slide structure + narration text
2. TTS generates MP3 audio per slide narration
3. Playwright (headless Chromium) screenshots each slide as PNG
4. ffmpeg combines: PNG image + MP3 audio → MP4 segment
5. ffmpeg concatenates all segments → Final MP4
```

All rendering is local — no cloud video service involved. The only external calls are LLM (slide structure) and TTS (narration audio), which use your configured providers.

---

## Performance Tuning

### Limit Concurrent Video Renders

Video rendering is resource-intensive. By default, only one video renders at a time:

```bash
# If you need to adjust worker concurrency (affects all background tasks):
OPEN_NOTEBOOK_WORKER_MAX_TASKS=3
```

With video enabled, keep `WORKER_MAX_TASKS` low (1-3) to avoid multiple simultaneous video renders consuming all CPU/RAM.

### Reduce Render Resolution

Videos render at 1920×1080 (1080p) by default. For faster rendering or smaller files, you can set a lower resolution (future config option).

---

## Troubleshooting

### "Video option not showing in UI"

**Cause**: `OPEN_NOTEBOOK_ENABLE_VIDEO` not set or not picked up.

**Fix**:
```bash
# Verify the variable is set in the container:
docker compose exec open_notebook env | grep ENABLE_VIDEO

# Should output: OPEN_NOTEBOOK_ENABLE_VIDEO=true
```

### "Playwright not found"

**Cause**: Chromium browser not installed.

**Fix**:
```bash
# In Docker: Restart the container — Playwright installs on first boot when the flag is set.
# Check logs for: "Installing Playwright browsers..."
docker compose logs open_notebook | grep -i playwright

# Local dev:
playwright install chromium
```

### "ffmpeg: command not found"

**Cause**: ffmpeg binary missing (unlikely — it's a transitive dependency).

**Fix**:
```bash
# Verify ffmpeg is available:
docker compose exec open_notebook which ffmpeg
# Should output: /usr/bin/ffmpeg

# If missing (rare):
# Add to Dockerfile:
# RUN apt-get update && apt-get install -y ffmpeg
```

### "Video render failed with no error"

**Common causes**:
1. **Disk full** — Videos need ~500MB working space. Check: `df -h`
2. **TTS timeout** — Narration audio generation exceeded `ESPERANTO_TTS_TIMEOUT`. Increase it.
3. **Memory exhausted** — Chromium + ffmpeg can spike RAM. Reduce slide count or upgrade server.
4. **Permission issue** — Can't write to `data/videos/`. Check directory permissions.

### "Video quality is poor"

**Solutions**:
- Shorten narration (shorter audio = fewer rendering artifacts)
- Reduce slide count (fewer slides = better encoding quality per slide)
- Check TTS provider (robotic TTS narration hurts perceived quality more than visual quality)

---

## Uninstalling / Disabling

To remove video support:

```bash
# 1. Remove the environment variable from docker-compose.yml
# 2. Recreate the container:
docker compose down && docker compose up -d

# 3. (Optional) Remove the cached Chromium download:
# The download is stored in the data volume — rm -rf data/playwright/
```

The Docker image returns to its lean state. Existing videos remain in `data/videos/` — they're just not accessible via the UI.

---

## Cost Implications

Video generation costs are **LLM + TTS only**. Rendering is local and free:

```
8-slide, 6-minute video (GPT-4o + Google TTS):
  LLM:    ~$0.06
  TTS:    ~$0.09
  Render: Free
  Total:  ~$0.15

With local LLM + local TTS:
  LLM:    Free
  TTS:    Free
  Render: Free
  Total:  Free (but slower)
```

---

## Next Steps

- **User guide**: [Creating Videos](../3-USER-GUIDE/creating-videos.md)
- **Core concepts**: [Videos Explained](../2-CORE-CONCEPTS/videos-explained.md)
- **TTS setup**: [Local TTS](local-tts.md) or [AI Providers](ai-providers.md)
- **Worker config**: [Advanced](advanced.md) — concurrency and performance
