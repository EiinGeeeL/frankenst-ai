# Variables
IMAGE_NAME = my-graph-app
CONTAINER_NAME = my-graph-app-container
PORT = 8000
HOST = 0.0.0.0

# Build the Docker image
docker-build:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build -t $(IMAGE_NAME) .

# Run the Docker container
docker-run: docker-build
	@echo "Running Docker container: $(CONTAINER_NAME)"
	docker run --rm -it -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)

# Stop the running Docker container
docker-stop:
	@echo "Stopping container: $(CONTAINER_NAME)"
	@docker stop $(CONTAINER_NAME) || echo "Container $(CONTAINER_NAME) is not running."

# Remove unused images and containers
docker-prune:
	@echo "Cleaning up unused images and containers"
	docker system prune -f

# Rebuild the Docker image (clean and build)
docker-rebuild: docker-prune docker-build
	@echo "Docker image rebuilt successfully: $(IMAGE_NAME)"

# Run LangGraph local server
run-app:
	@echo "Starting LangGraph server on port $(PORT)"
	langgraph dev --port $(PORT) --host $(HOST)

# Show available commands
help:
	@echo "Available targets:"
	@echo "  docker-build        - Build the Docker image"
	@echo "  docker-run          - Build and run the Docker container"
	@echo "  docker-stop         - Stop the running container"
	@echo "  docker-prune        - Remove unused images and containers"
	@echo "  docker-rebuild      - Clean and rebuild the Docker image"
	@echo "  run-app             - Start LangGraph local server"
	@echo "  help                - Show this help message"
