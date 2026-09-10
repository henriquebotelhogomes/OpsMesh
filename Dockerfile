# ==========================================
# Stage 1: Frontend Build (React + Vite)
# ==========================================
FROM node:24-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Python Dependencies with uv
# ==========================================
FROM python:3.12-slim AS backend-builder
WORKDIR /app

# Install uv for blazing-fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -e .

# ==========================================
# Stage 3: Final Production Runtime (Scale-to-Zero)
# ==========================================
FROM python:3.12-slim AS runtime
WORKDIR /app

# Security: Non-root user
RUN addgroup --system --gid 1001 opsgroup && \
    adduser --system --uid 1001 --gid 1001 opsuser

# Copy python packages and binaries
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy source code and docs
COPY src/ /app/src/
COPY docs/runbooks/ /app/docs/runbooks/
COPY pyproject.toml /app/

# Copy compiled frontend SPA
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Install project editable link
RUN pip install --no-deps -e .

USER opsuser

ENV PORT=8000
ENV API_HOST=0.0.0.0
ENV APP_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "opsmesh.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
