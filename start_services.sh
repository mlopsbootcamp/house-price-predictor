#!/bin/bash

# Navigate to the directory where the script is located
cd "$(dirname "$0")"

echo "Starting Docker services for MLOps-Project..."

# Use Docker Compose to build and start the containers in detached mode
if docker compose version > /dev/null 2>&1; then
    docker compose down
    docker compose up -d --build
elif command -v docker-compose > /dev/null 2>&1; then
    docker-compose down
    docker-compose up -d --build
else
    echo "Error: Docker Compose is not installed or not in the system PATH."
    exit 1
fi

echo "Docker services are now up and running!"
echo "API is available at http://localhost:8000"
echo "Frontend is available at http://localhost:8501"
