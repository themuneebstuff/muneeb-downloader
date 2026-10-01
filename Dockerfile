FROM python:3.12-slim

# ffmpeg zaroori hai (best quality merge + MP3 ke liye)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Render $PORT deta hai; lambe downloads ke liye timeout barhaya
CMD exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2
