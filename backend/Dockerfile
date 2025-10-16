FROM python:3.11-slim

WORKDIR /app

# Install system dependencies efficiently (needed for some ML packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies with memory optimizations
RUN pip install --no-cache-dir \
    --disable-pip-version-check \
    --prefer-binary \
    -r requirements.txt

RUN python -m spacy download sv_core_news_sm

# Copy the rest of the application
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Use gunicorn for production (better than dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "1", "--timeout", "120", "src.app:create_app()"]