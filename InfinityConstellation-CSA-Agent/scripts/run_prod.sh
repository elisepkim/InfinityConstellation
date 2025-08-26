#!/bin/bash
# Run production system with Docker Compose
set -e

echo "[INFO] Starting Infinity Constellation CSA in production mode..."

# Build images
docker-compose -f docker-compose.prod.yml build

# Run services
docker-compose -f docker-compose.prod.yml up -d

echo "[INFO] Deployment complete."
echo "Backend API: http://localhost:8000"
echo "Streamlit UI: http://localhost:8501"