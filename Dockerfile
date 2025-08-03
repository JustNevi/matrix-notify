# Stage 1: Base build stage
FROM python:3.12-slim AS builder

WORKDIR /opt/matrix-notify/

# Set environment variables for clean builds
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.prod.txt .
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.prod.txt


# Stage 2: Production stage
FROM python:3.12-slim

# Create app user and working directory
RUN useradd -m -r appuser \
	 && mkdir /opt/matrix-notify/ \
	 # Create directory and files for saving matrix client credentials, keys ets.
	 && mkdir -p /opt/matrix-notify/files/backup/store \
	 && touch /opt/matrix-notify/files/backup/config.json \
	 && echo "{}" > /opt/matrix-notify/files/backup/config.json \
	 # Assign a directory to a user
	 && chown -R appuser /opt/matrix-notify/

WORKDIR /opt/matrix-notify/

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application files
COPY --chown=appuser:appuser src src

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

CMD ["gunicorn", "--chdir=/opt/matrix-notify/src/", "--bind=0.0.0.0:8000", "--workers=3", "main:app"]
