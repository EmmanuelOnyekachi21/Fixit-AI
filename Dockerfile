# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql-client \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set environment for collectstatic
ENV SECRET_KEY="temp-build-key-for-collectstatic"
ENV DATABASE_URL="sqlite:///tmp/db.sqlite3"

# Create staticfiles directory
RUN mkdir -p staticfiles

# Collect static files
RUN python manage.py collectstatic --no-input --clear

# Remove temp database
RUN rm -f /tmp/db.sqlite3

# Expose port
EXPOSE 8080

# Run migrations and start server
CMD python manage.py migrate --no-input && \
    daphne -b 0.0.0.0 -p $PORT config.asgi:application
