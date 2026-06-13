# Business Plan Studio — single web service (FastAPI serves the built React SPA).
#
#   docker build -t bplan .
#   docker run -p 8000:8000 bplan
#
# Render/Railway: point the service at this Dockerfile. The platform's $PORT is
# honoured automatically.

# ---- Stage 1: build the React frontend ----
FROM node:20-bookworm-slim AS frontend
WORKDIR /fe
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python runtime (FastAPI + reports) ----
FROM python:3.12-slim-bookworm AS app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BP_SEED_ON_STARTUP=true

# Native libraries required by WeasyPrint (PDF rendering) + base fonts.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libffi8 \
        shared-mime-info \
        fonts-dejavu-core \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

COPY backend/ /app/backend/
# Built SPA — main.py serves it from <repo>/frontend/dist
COPY --from=frontend /fe/dist /app/frontend/dist

EXPOSE 8000
WORKDIR /app/backend
# Honour the platform-provided $PORT (Render/Railway); default 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
