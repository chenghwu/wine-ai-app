# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into /install directory
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --target=/install -r requirements.txt && \
    rm -rf /root/.cache/pip /tmp/*

# Install Playwright browser dependencies
RUN python -m playwright install --with-deps chromium

# Set PYTHONPATH so the next command can find packages in /install
ENV PYTHONPATH=/install

# Preload SentenceTransformer model into /root/.cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ---------- Stage 2: Final ----------
FROM python:3.11-slim AS final

WORKDIR /app

# Copy your application source code
COPY . /app

# Copy dependencies from builder stage
COPY --from=builder /install /usr/local/lib/python3.11/site-packages/

# Copy preloaded model cache from builder
COPY --from=builder /root/.cache /root/.cache

# Copy Playwright browser binaries from builder
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages/
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Expose FastAPI port and run the server
ENV PORT=8080
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]