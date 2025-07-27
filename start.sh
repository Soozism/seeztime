#!/bin/bash

# Ginga Tek - Task Management API Startup Script

echo "🚀 Starting Ginga Tek Task Management API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Create admin user
echo "👤 Creating admin user..."
python scripts/create_admin_simple.py

# Start the application
echo "🌟 Starting the API server..."
echo "📊 Dashboard will be available at: http://localhost:8000/docs"
echo "🔍 API documentation at: http://localhost:8000/redoc"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
echo "⚠️  Please change the password after first login!"
echo ""

python main.py
