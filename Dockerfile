# Use Python base image for CPU-only execution
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU wheels first to avoid pulling huge CUDA builds
ARG TORCH_VERSION=2.4.0
ARG TORCHVISION_VERSION=0.19.0
ARG TORCHAUDIO_VERSION=2.4.0
ARG PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    torch==${TORCH_VERSION} \
    torchvision==${TORCHVISION_VERSION} \
    torchaudio==${TORCHAUDIO_VERSION} \
    --extra-index-url ${PYTORCH_INDEX_URL}

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (now that torch deps are satisfied)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV RELOAD=false
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "run.py"]

