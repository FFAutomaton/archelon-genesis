#!/bin/bash

# Exit on error
set -e

# Define variables
IMAGE_NAME="archelon-genesis"
IMAGE_TAG="latest"

# Build the Docker image
echo "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
docker build -t $IMAGE_NAME:$IMAGE_TAG .

echo "Docker image built successfully!"
echo "To run the container, use:"
echo "docker run -p 8000:8000 $IMAGE_NAME:$IMAGE_TAG"
