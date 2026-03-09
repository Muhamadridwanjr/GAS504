.PHONY: build up down restart status logs clean test help

# Variables
APP_NAME=gas-billing-service

help:
	@echo "Available commands:"
	@echo "  make build    - Build the docker image"
	@echo "  make up       - Start the service in detached mode"
	@echo "  make down     - Stop and remove containers"
	@echo "  make restart  - Restart the service"
	@echo "  make status   - Check container status"
	@echo "  make logs     - View container logs"
	@echo "  make clean    - Remove docker images and volumes"
	@echo "  make test     - Run tests"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

status:
	docker compose ps

logs:
	docker compose logs -f

clean:
	docker compose down --rmi all --volumes --remove-orphans

test:
	docker compose run --rm gas-billing-service pytest tests/
