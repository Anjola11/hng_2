# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8080

# Run FastAPI with Uvicorn
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8080"]