# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY src/ ./src/ 
COPY Procfile ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port (match Flask default or your config)
EXPOSE 5000

# Run the app
CMD ["python", "src/app.py"]
