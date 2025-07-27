#!/bin/bash

# MySQL Access Script for Ginga Tek
# This script provides easy access to MySQL database

echo "🗄️  Ginga Tek MySQL Access"
echo "=========================="

# Check if containers are running
if ! sudo docker compose ps | grep -q "mysql.*Up"; then
    echo "❌ MySQL container is not running. Please start the services first:"
    echo "   ./start-dev.sh"
    exit 1
fi

echo "✅ MySQL container is running"
echo ""

# Show available options
echo "Choose an option:"
echo "1. Connect to MySQL as gingatek user"
echo "2. Connect to MySQL as root user"
echo "3. Show databases"
echo "4. Show tables in ginga_tek database"
echo "5. Show users table"
echo "6. Interactive MySQL shell"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "Connecting as gingatek user..."
        sudo docker compose exec mysql mysql -u gingatek -p ginga_tek
        ;;
    2)
        echo "Connecting as root user..."
        sudo docker compose exec mysql mysql -u root -p
        ;;
    3)
        echo "Showing databases..."
        sudo docker compose exec mysql mysql -u gingatek -pgingatek123 -e "SHOW DATABASES;"
        ;;
    4)
        echo "Showing tables in ginga_tek database..."
        sudo docker compose exec mysql mysql -u gingatek -pgingatek123 -e "USE ginga_tek; SHOW TABLES;"
        ;;
    5)
        echo "Showing users table..."
        sudo docker compose exec mysql mysql -u gingatek -pgingatek123 -e "USE ginga_tek; SELECT username, email, role FROM users;"
        ;;
    6)
        echo "Starting interactive MySQL shell..."
        sudo docker compose exec mysql mysql -u gingatek -p ginga_tek
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac 