# Ginga Tek - Docker Development Setup

This guide explains how to run the Ginga Tek Task Management API using Docker with MySQL database.

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB of available RAM
- Ports 8000 and 3306 available

## Quick Start

### Option 1: Using the startup script (Recommended)

```bash
# Make the script executable (if not already done)
chmod +x start-dev.sh

# Start the development environment
./start-dev.sh
```

### Option 2: Manual Docker commands

```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## Services

The Docker setup includes the following services:

### 1. Ginga Tek API (Port 8000)
- **URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### 2. MySQL Database (Internal Only)
- **Host**: mysql (internal container name)
- **Port**: 3306 (internal only)
- **Database**: ginga_tek
- **Username**: gingatek
- **Password**: gingatek123
- **Root Password**: root123

## Default Admin User

After the first startup, a default admin user is created:

- **Username**: admin
- **Password**: admin123
- **Email**: admin@gingatek.com
- **Role**: ADMIN

⚠️ **Important**: Change the default password after first login!

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ginga-tek-api
docker-compose logs -f mysql
```

### Stop services
```bash
docker-compose down
```

### Restart services
```bash
docker-compose restart
```

### Access MySQL database
```bash
# Connect to MySQL container
docker compose exec mysql mysql -u gingatek -p ginga_tek

# Or as root
docker compose exec mysql mysql -u root -p

# Or access from API container
docker compose exec ginga-tek-api mysql -h mysql -u gingatek -p ginga_tek
```

### Run database migrations
```bash
# Access the API container
docker-compose exec ginga-tek-api bash

# Run migrations
alembic upgrade head
```

### Create a new migration
```bash
# Access the API container
docker-compose exec ginga-tek-api bash

# Create a new migration
alembic revision --autogenerate -m "Description of changes"
```

## Environment Variables

The following environment variables are configured:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `mysql://gingatek:gingatek123@mysql:3306/ginga_tek` | Database connection string |
| `SECRET_KEY` | `your-secret-key-change-this` | JWT secret key |
| `DEBUG` | `True` | Debug mode |
| `MYSQL_HOST` | `mysql` | MySQL hostname |
| `MYSQL_PORT` | `3306` | MySQL port |
| `MYSQL_USER` | `gingatek` | MySQL username |
| `MYSQL_PASSWORD` | `gingatek123` | MySQL password |
| `MYSQL_DATABASE` | `ginga_tek` | MySQL database name |

## Database Configuration

### MySQL Settings
- **Version**: MySQL 8.0
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci
- **Authentication**: mysql_native_password

### Connection Pool Settings
- **Pool Size**: 10
- **Max Overflow**: 20
- **Pool Recycle**: 300 seconds
- **Pool Pre-ping**: Enabled

## Troubleshooting

### Service won't start
1. Check if Docker is running
2. Check if ports 8000 and 3306 are available
3. View logs: `docker-compose logs`

### Database connection issues
1. Wait for MySQL to be ready (the startup script handles this)
2. Check MySQL logs: `docker-compose logs mysql`
3. Verify database exists: `docker-compose exec mysql mysql -u gingatek -p -e "SHOW DATABASES;"`

### API not responding
1. Check API logs: `docker-compose logs ginga-tek-api`
2. Verify the API container is running: `docker-compose ps`
3. Check if the wait script completed successfully

### Reset everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
./start-dev.sh
```

## Development Workflow

1. **Start the environment**: `./start-dev.sh`
2. **Make code changes** in your local files
3. **Rebuild the API container**: `docker-compose build ginga-tek-api`
4. **Restart the API**: `docker-compose restart ginga-tek-api`
5. **Test your changes** at http://localhost:8000/docs

## Production Considerations

For production deployment:

1. Change all default passwords
2. Use strong SECRET_KEY
3. Set DEBUG=False
4. Configure proper CORS settings
5. Use external MySQL database
6. Set up proper logging
7. Configure SSL/TLS
8. Use Docker secrets for sensitive data

## File Structure

```
ginga_tek/
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # API container definition
├── start-dev.sh               # Development startup script
├── scripts/
│   ├── init-mysql.sql         # MySQL initialization
│   └── wait-for-mysql.py      # MySQL readiness check
├── app/                       # Application code
└── .dockerignore              # Docker build exclusions
``` 