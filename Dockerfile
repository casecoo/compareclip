FROM python:3.10-slim

# Install system dependencies (FFmpeg, ImageMagick, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    fonts-roboto \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Modify ImageMagick policy to allow text/font rendering and @/tmp file access for MoviePy
RUN sed -i 's/rights="none"/rights="read|write"/g' /etc/ImageMagick-6/policy.xml || true
RUN sed -i 's/rights="none"/rights="read|write"/g' /etc/ImageMagick-7/policy.xml || true
RUN sed -i 's/pattern="@\*"/pattern="*"/g' /etc/ImageMagick-6/policy.xml || true
RUN sed -i 's/pattern="@\*"/pattern="*"/g' /etc/ImageMagick-7/policy.xml || true

WORKDIR /app

# Copy requirement definitions
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application files and audio asset
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV IMAGEMAGICK_BINARY=/usr/bin/convert
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1

EXPOSE 8000

CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
