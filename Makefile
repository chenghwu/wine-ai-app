# Virtual environment directory
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Set project metadata variables
PROJECT_ID = gen-lang-client-0149363960
REGION = us-west1
REPO = wine-ai-app
IMAGE_NAME = wine-api
TAG = latest
FULL_IMAGE = $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO)/$(IMAGE_NAME)

# Default goal
.DEFAULT_GOAL := help

# Create virtual environment
$(VENV_DIR)/bin/activate: requirements.txt
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)

install: $(VENV_DIR)/bin/activate
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

run:
	@echo "Starting FastAPI app..."
	$(VENV_DIR)/bin/uvicorn app.main:app --reload

init-db:
	@echo "Initializing database schema..."
	$(PYTHON) -m app.db.init_db
	
test:
	@echo "Running tests..."
	$(VENV_DIR)/bin/pytest -s

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR) 
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -f .coverage coverage.xml
	rm -rf htmlcov
	rm -rf frontend/.next frontend/.turbo
	find . -name ".DS_Store" -delete

# Will full reset of frontend dependencies, cost time to reinstall
clean-node:
	rm -rf frontend/node_modules

docker-build:
	@echo "Building Docker image..."
	docker build -t wine-ai-app .

docker-run:
	@echo "Running Wine AI App in Docker..."
	docker run -d -p 8080:8080 --env-file .env wine-api:slim

docker-compose-up:
	docker-compose up --build -d

# Build image for Google Cloud Run (linux/amd64)
docker-build-cloudrun:
	docker build --platform=linux/amd64 -t $(FULL_IMAGE):$(TAG) .

# Push image to Artifact Registry
docker-push-cloudrun:
	docker push $(FULL_IMAGE):$(TAG)

# Build & Push (combined)
docker-deploy-cloudrun: docker-build-cloudrun docker-push-cloudrun

# Google cloud build
gcloud-build:
	gcloud builds submit --tag $(FULL_IMAGE)

docker-start:
	@echo "Starting all Docker services without rebuilding..."
	docker-compose up -d

docker-stop:
	@echo "Stopping all Docker services..."
	docker-compose down

docker-clean:
	@echo "Removing Docker containers and images..."
	docker system prune -af

help:
	@echo ""
	@echo "Wine Intelligence Analysis Project Commands:"
	@echo "---------------------------"
	@echo "make install		# Create venv and install all dependencies (incl. Playwright)"
	@echo "make run			# Run FastAPI app with uvicorn"
	@echo "make init-db		# Initialize DB"
	@echo "make test		# Run tests"
	@echo "make clean		# Remove virtualenv and __pycache__"
	@echo "make clean-node	# Remove frontend dependencies"
	@echo "make docker-build		# Build image"
	@echo "make docker-run			# Run container with .env"
	@echo "make docker-compose-up	# Use full service stack"
	@echo "make docker-start		# Start all docker services"
	@echo "make docker-stop			# Stop all docker services"
	@echo "make docker-clean		# Remove all docker resources"
	@echo ""
