FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable to avoid buffering in logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency files first to leverage Docker cache
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port uvicorn will run on (matches the app.main settings)
EXPOSE 6502

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6502"]
