FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio/DSP processing and compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if available
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Set Python path to ensure imports work correctly
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
