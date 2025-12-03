FROM python:3.13-slim

# Create workspace
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI (Uvicorn)
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]