#!/bin/bash

# Exit on error
set -e

# Define variables
IMAGE_NAME="archelon-genesis"
IMAGE_TAG="latest"
CONTAINER_NAME="archelon-genesis"
HOST_PORT=8000
CONTAINER_PORT=8000

# Check if container already exists
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME already exists. Stopping and removing..."
    docker stop $CONTAINER_NAME || true
    docker rm $CONTAINER_NAME || true
fi

# Run the container
echo "Starting container: $CONTAINER_NAME"
docker run -d \
    --name $CONTAINER_NAME \
    -p $HOST_PORT:$CONTAINER_PORT \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/log_files:/app/log_files" \
    $IMAGE_NAME:$IMAGE_TAG

echo "Container started successfully!"
echo "API is available at: http://localhost:$HOST_PORT"
echo "API documentation: http://localhost:$HOST_PORT/docs"
