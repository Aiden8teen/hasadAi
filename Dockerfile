# ==============================================================================
# Hassad AI (حصاد) — Production Container for Free Cloud / Hugging Face Spaces
# ==============================================================================
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Install required system libraries for OpenCV and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application codebase and models
COPY backend/ ./backend/
COPY models/ ./models/
COPY web/ ./web/
COPY run.sh ./run.sh

RUN chmod +x ./run.sh

# Default port for Hugging Face Spaces & container hosts
EXPOSE 7860

# Launch Hassad AI (binds to 0.0.0.0 on the dynamic $PORT)
CMD ["bash", "-c", "./run.sh ${PORT:-7860}"]
