# Multi-stage Dockerfile for WebArchiver Pro by Mezzold Studio
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy
WORKDIR /app

# System dependencies for WeasyPrint and Playwright
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium || playwright install chromium

COPY backend/ ./
COPY --from=frontend-builder /frontend/out ./static

EXPOSE 8000
CMD ["python", "run.py"]
