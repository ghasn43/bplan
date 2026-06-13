# Deploying Business Plan Studio

The app ships as a **single web service**: FastAPI serves the built React SPA and
the `/api` backend from the same origin. One container, one URL.

- Frontend: React + Vite (built to `frontend/dist`)
- Backend: FastAPI + JSON storage, Word/PDF report generation
- Container: `Dockerfile` (multi-stage — builds the SPA, then a Python runtime
  with the WeasyPrint native libs needed for PDF reports)

There is **no separate backend URL** and **no Streamlit**. Whatever URL the host
gives you is the whole app.

---

## Option A — Render (Blueprint)

1. Push to GitHub (already done): `ghasn43/bplan`, branch `main`.
2. Render → **New → Blueprint** → pick this repo. It reads `render.yaml`
   (Docker web service, health check `/health`).
3. **Apply / Deploy**. First build takes a few minutes.
4. Open the service URL, e.g. `https://bplan-xxxx.onrender.com` — that's the full app.
   - Health: `GET /health` → `{"status":"ok"}`
   - API docs: `/docs`

### Render (manual Web Service)
New → **Web Service** → connect repo → **Runtime: Docker**,
**Dockerfile path: `./Dockerfile`** (leave build/start commands empty).

---

## Option B — Railway

New → **Deploy from GitHub repo** → select the repo. Railway detects the
`Dockerfile` and builds it. Generate a domain in the service settings.

---

## Option C — Run the container anywhere

```bash
docker build -t bplan .
docker run -p 8000:8000 bplan
# open http://localhost:8000
```

The platform's `$PORT` is honoured automatically; locally it defaults to `8000`.

---

## Configuration (env vars)

| Variable             | Default            | Purpose                                            |
|----------------------|--------------------|----------------------------------------------------|
| `PORT`               | `8000`             | Set by the host; the container binds it.           |
| `BP_SEED_ON_STARTUP` | `true`             | Seed a demo project on first boot.                 |
| `BP_DATA_DIR`        | `backend/data`     | JSON store location. Point at a mounted disk to persist. |
| `BP_CORS_ORIGINS`    | localhost dev URLs | Not needed in production (same-origin).             |

### Persisting data
The JSON store, uploaded images, and generated reports live on the container
filesystem, which is **ephemeral** on most hosts (resets on redeploy; the demo
re-seeds on boot). For durable data on Render, attach a disk and set
`BP_DATA_DIR=/data` (see the commented block in `render.yaml`; requires a paid plan).

---

## Local development (unchanged)

Two processes:

```bash
# backend
cd backend && py -m uvicorn app.main:app --reload     # http://127.0.0.1:8000

# frontend (separate terminal)
cd frontend && npm run dev                            # http://localhost:5173
```

In dev, Vite proxies `/api` to the backend. The SPA-serving block in
`backend/app/main.py` is a no-op when `frontend/dist` is absent, so it doesn't
interfere with the Vite dev server.

## Notes
- First request after idle on free tiers can take ~30–60s (cold start).
- PDF reports need the WeasyPrint system libraries — already installed in the
  Dockerfile. If WeasyPrint is ever unavailable, the PDF route falls back to a
  styled, print-ready HTML file (Word generation is unaffected).
