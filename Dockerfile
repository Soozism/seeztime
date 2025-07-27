FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies including MySQL client
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p /app/data

# Make wait script executable
RUN chmod +x scripts/wait-for-mysql.py

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=mysql://gingatek:gingatek123@mysql:3306/ginga_tek
ENV MYSQL_HOST=mysql
ENV MYSQL_PORT=3306
ENV MYSQL_USER=gingatek
ENV MYSQL_PASSWORD=gingatek123
ENV MYSQL_DATABASE=ginga_tek

# Expose port
EXPOSE 8000

# Wait for MySQL and start application
CMD ["sh", "-c", "python scripts/wait-for-mysql.py && python scripts/create_admin.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
