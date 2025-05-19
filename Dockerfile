# Use Python 3.10 as base image

FROM python:3.10-slim

# Install system dependencies required for Manim

RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    libgif-dev \
    librsvg2-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# Set working directory

WORKDIR /app

# Copy requirements first to leverage Docker cache

COPY requirements.txt .

# Install Python dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application

COPY . .

# Create necessary directories

RUN mkdir -p media

# Set environment variables

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose the port

EXPOSE 8080

# Command to run the application

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

