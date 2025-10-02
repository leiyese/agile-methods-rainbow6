# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install pgvector Python client
RUN pip install --no-cache-dir pgvector

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/interim /app/data/processed /app/uploads

# Expose port (match Flask default or your config)
EXPOSE 5000

# Copy the rest of the application
COPY . .

# Run the app
CMD ["flask", "run", "--host=0.0.0.0"]
