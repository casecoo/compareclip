FROM python:3.10-slim

# Install system dependencies (FFmpeg, ImageMagick, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    fonts-roboto \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Modify ImageMagick policy to allow text/font rendering
RUN sed -i 's/<policy domain="coder" rights="none" pattern="LABEL" \/>/<policy domain="coder" rights="read|write" pattern="LABEL" \/>/' /etc/ImageMagick-6/policy.xml || true
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true

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

EXPOSE 8000

CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
