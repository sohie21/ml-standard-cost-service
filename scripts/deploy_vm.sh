#!/usr/bin/env bash
set -e

docker compose up -d --build

echo "Service started."
echo "Check containers:"
echo "docker ps"
echo "Check health:"
echo "curl http://localhost:8000/health"
