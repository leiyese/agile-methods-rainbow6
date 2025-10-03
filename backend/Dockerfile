FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Run as a module - this enables relative imports
CMD ["python", "-m", "src.app"]