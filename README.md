# Video Comparison Generator ("VS" Style)

A lightweight, zero-cost automated tool for generating viral vertical split-screen "VS" comparison videos (e.g., *Superman vs. Batman*) with beat-synced transitions and dynamic category tags.

---

## Problem & Motivation

### Why Was This Project Built?
Vertical "VS" comparison videos (such as character power scaling or product matchups) are extremely popular across social media platforms like TikTok, YouTube Shorts, and Instagram Reels. However, creating these videos manually in traditional video editors (Premiere Pro, CapCut, After Effects) is tedious and highly repetitive:
* Manually splitting top and bottom video clips into vertical aspect ratios.
* Aligning frame-by-frame text overlays for ~9 categories (e.g., *IQ, Strength, Speed, Durability*).
* Precise frame synchronization of score reveals with background audio beat drops.

### What Problem Does It Solve?
**Video Comparison Generator** automates the entire video creation workflow into a single programmatic request. By taking two short vertical video clips (~20 seconds max), player names, and 9 custom category labels, the system automatically clips, composites, beat-syncs, and renders a ready-to-publish vertical MP4 video—reducing hours of repetitive manual editing down to seconds.

---

## Architecture & Technology Choices

The project adheres to a strict **zero-cost operational philosophy**, zero persistent database overhead, and a lean synchronous pass-through pipeline.

```
┌─────────────────────────┐               ┌──────────────────────────────────────────┐
│   Vercel (Frontend)     │  HTTP POST    │         Render.com (Backend API)         │
│  (Static/React SPA)     │ ------------> │ (Python 3.10 + FastAPI + Docker)         │
│                         │ Multipart Form│                                          │
│  - File Validation      │               │  - MoviePy + FFmpeg + ImageMagick        │
│  - Cold-start UX        │ <------------ │  - Beat sync & visual compositing        │
│  - Direct Blob Download │   MP4 Blob    │  - Immediate temp file cleanup           │
└─────────────────────────┘               └──────────────────────────────────────────┘
```

### Why These Technologies Were Chosen

| Component | Technology | Rationale & Architectural Decisions |
|---|---|---|
| **Backend API** | **FastAPI (Python)** | Chosen for high-performance asynchronous file handling, low overhead, automatic OpenAPI documentation, and native support for post-response `BackgroundTasks`. |
| **Backend Hosting** | **Render.com (Free Tier)** | Containerized deployment hosted on Render's free Web Service tier. Selected specifically because it offers a free container runtime without requiring credit card verification. |
| **Video Engine** | **MoviePy + FFmpeg + ImageMagick** | Handles programmatic video clipping, vertical compositing, custom text overlay rendering, and audio beat alignment. Packaged directly in Docker to bypass unreliable buildpacks. |
| **Frontend** | **Static/React (Vercel)** | Hosted on Vercel for zero-cost, global CDN distribution. Handles client-side input validation (file size & length limits) before sending payloads to the API. |
| **Execution Model** | **Synchronous Pass-Through** | Processing is fully synchronous (`Request → Render → Stream MP4 response → Auto-cleanup`). Bypasses background queue workers and complex job polling for short (~20s) videos. |

### Architectural Trade-offs & Simplifications

* **No Persistent Database:** The application is 100% stateless—there are no user accounts, render histories, or database dependencies to maintain.
* **No External Object Storage:** Input video clips are short (~20s max), allowing video streams to pass directly through temporary container memory/disk and return straight to the client as a binary blob response. This eliminates cloud storage costs and data privacy overhead.
* **No Background Queue Infrastructure:** Because video processing is bounded to short clips, synchronous request-response handling fits cleanly within standard HTTP timeouts without requiring separate background queue workers or complex job state polling.

---

## Standards & Best Practices

* **Conventional Commits:** Git commits follow standardized messaging guidelines (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`) for clean version control history and seamless changelog generation.
* **Containerized Infrastructure (Dockerized Backend):** Built using a multi-stage `python:3.10-slim` base image with system dependencies (`ffmpeg`, `imagemagick`, `fonts-roboto`) pre-installed and ImageMagick policies configured for font rendering.
* **Low-Resource Optimization (512MB RAM Cap):** Thread concurrency is strictly locked (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`) to guarantee stable rendering within Render's free 512MB RAM ceiling without memory leaks or OOM crashes.
* **Stateless Resource Cleanup:** Uses FastAPI's `BackgroundTasks` to perform immediate post-response temporary directory deletion (`shutil.rmtree`) and garbage collection (`gc.collect()`), ensuring zero disk accumulation.
* **UX Resilience & Cold Start Management:** The frontend incorporates proactive UI feedback (loading spinners + cold-start warning text) to keep users informed during Render's ~30-60s container wake-up time.
* **Modular Architecture:** Clear code organization separating API router logic ([`backend/app/main.py`](file:///c:/Users/erman/Desktop/apps/scripts/video_project/backend/app/main.py)), core video engine ([`backend/app/core/video_processor.py`](file:///c:/Users/erman/Desktop/apps/scripts/video_project/backend/app/core/video_processor.py)), and asset configuration ([`backend/app/core/config.py`](file:///c:/Users/erman/Desktop/apps/scripts/video_project/backend/app/core/config.py)).

---

## Getting Started

### Prerequisites
* [Docker](https://www.docker.com/) installed locally **OR** Python 3.10+ with FFmpeg and ImageMagick.

### Running with Docker (Recommended)

```bash
# Build the Docker image
docker build -t video-comparison-generator .

# Run the container
docker run -p 8000:8000 video-comparison-generator
```
Once started, access the interactive API docs at `http://localhost:8000/docs`.

### Running Locally (Without Docker)

1. **Install System Dependencies:**
   Ensure `ffmpeg` and `imagemagick` are installed on your system PATH.

2. **Install Python Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start the FastAPI Server:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

### Running the Frontend

Open `frontend/index.html` directly in your browser, or serve it using any static server:
```bash
npx serve frontend
```

---

## API Reference

### `POST /api/v1/compare`

Generates a vertical comparison video from two input clips.

* **Content-Type:** `multipart/form-data`
* **Form Parameters:**
  * `video1` *(file, required)*: First video clip (top half).
  * `video2` *(file, required)*: Second video clip (bottom half).
  * `player1_name` *(string, default: "PLAYER 1")*: Name of Player 1.
  * `player2_name` *(string, default: "PLAYER 2")*: Name of Player 2.
  * `categories` *(string / JSON array, default: 9 standard categories)*: 9 comma-separated or JSON array tags (e.g., `IQ, BATTLE IQ, SPEED, DURABILITY, STRENGTH, POWER, AGILITY, COMBAT, ENDURANCE`).

* **Response:** Binary `video/mp4` file stream for direct browser download.

---

## License

MIT License.
