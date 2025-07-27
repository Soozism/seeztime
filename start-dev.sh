#!/bin/bash

# Ginga Tek Development Startup Script
# This script starts the application with MySQL database for development

echo "🚀 Starting Ginga Tek Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down

# Build and start the services
echo "🔨 Building and starting services..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if services are running
echo "🔍 Checking service status..."
docker compose ps

# Run health check
echo ""
echo "🏥 Running health checks..."
python3 scripts/health-check.py

echo ""
echo "✅ Ginga Tek Development Environment is ready!"
echo ""
echo "📊 Services:"
echo "   🌐 API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🗄️  MySQL: Internal only (access via container)"
echo ""
echo "🔑 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   Email: admin@gingatek.com"
echo ""
echo "📝 Useful Commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop services: docker compose down"
echo "   Restart services: docker compose restart"
echo "   Access MySQL: docker compose exec mysql mysql -u gingatek -p ginga_tek"
echo "   Health check: python3 scripts/health-check.py"
echo ""
echo "⚠️  Remember to change the default admin password after first login!" 