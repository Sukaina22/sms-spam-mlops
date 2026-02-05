# app/Dockerfile

# --- Base image ---
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create working dir inside container
WORKDIR /app

# Install build tools (needed for some Python deps like numpy, scikit-learn)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# --- Install dependencies ---
# Copy requirements from project root into image
COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# --- Copy source code ---
# Copy backend + ml code into image
COPY ../app /app/app
COPY ../ml /app/ml

# (Optional) if you need model files, mlruns, etc., you can copy them too:
# COPY ../models /app/models
# COPY ../mlruns /app/mlruns

# --- Runtime configuration ---
# Default DB path inside container (can be overridden by env var)
ENV DB_PATH=/data/sms_history.db

# Create directory for DB volume
RUN mkdir -p /data

# Expose FastAPI port
EXPOSE 8000

# --- Start the API ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
