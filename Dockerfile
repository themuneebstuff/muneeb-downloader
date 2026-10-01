FROM python:3.12-slim

# ffmpeg is required (best-quality merge + MP3)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# The platform provides $PORT (Render). Default 7860 for Hugging Face Spaces.
# Longer timeout for big downloads.
ENV PORT=7860
CMD exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2
