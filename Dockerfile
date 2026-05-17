# ─── Stage 1: Frontend build ────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --ignore-scripts
COPY frontend/ .
RUN npm run build

# ─── Stage 2: Runtime ───────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# src/ contiene todos los paquetes Python — necesario para los imports de dominio
ENV PYTHONPATH=/app/src

# Los archivos SQLite viven en un volumen persistente montado en /app/data
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
