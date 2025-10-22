# Dockerfile
# Use a slim Python base image for smaller size
FROM python:3.12-slim

# Install system dependencies if needed (like curl or git)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire source code into the container
# This includes main.py, rag_storage.py, batch_converter.py, etc.
COPY . /app

# The final command to run the Python script
# Note: We do NOT start Ollama here; Docker Compose handles that.
CMD ["python", "main.py"]
