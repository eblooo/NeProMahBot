FROM python:3.9-slim-buster AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/

# Final stage
FROM python:3.9-slim-buster

LABEL maintainer="Sasha Alimov klimdos@gmail.com"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TG_API_TOKEN=""
ENV GPT_API_TOKEN=""

# Set work directory
WORKDIR /app

# Copy only necessary files from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app /app

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Run the application
ENTRYPOINT ["python", "src/app.py"]
