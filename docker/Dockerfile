FROM python:3.13-slim

WORKDIR /app

# Install git (and optionally SSH, if using git+ssh)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git openssh-client \
 && rm -rf /var/lib/apt/lists/*

# COPY secret_key.txt .

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run gunicorn with 1 process and 1 thread
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "1", "app:app"]

