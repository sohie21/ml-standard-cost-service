#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y docker.io docker-compose-plugin git curl

sudo systemctl enable docker
sudo systemctl start docker

sudo usermod -aG docker "$USER"

echo "Docker installed."
echo "Log out and log in again, or run: newgrp docker"
