# ==============================================================================
# Hassad AI (حصاد) — Production Container for Render / Cloud / Hugging Face
# ==============================================================================
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000

# Install required lightweight system libraries for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install cloud-optimized requirements (< 100 MB RAM)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application codebase and models
COPY backend/ ./backend/
COPY models/ ./models/
COPY web/ ./web/
COPY run.sh ./run.sh

RUN chmod +x ./run.sh

# Support Render default port 10000, Hugging Face 7860, and general 8080
EXPOSE 10000
EXPOSE 7860
EXPOSE 8080

# Launch Hassad AI on the dynamic $PORT (Render sets PORT=10000)
CMD ["bash", "-c", "./run.sh ${PORT:-10000}"]
