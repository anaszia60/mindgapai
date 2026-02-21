FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend folder and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ .

# Create uploads directory inside /app
RUN mkdir -p uploads && chmod 777 uploads

# Command to run the application
# Hugging Face Spaces expects the app to run on port 7860
CMD ["python", "app.py"]
