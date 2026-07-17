FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the default port
EXPOSE 8000

# Run with uvicorn
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
