.PHONY: run dev build test lint clean help

help:
	@echo "Available commands:"
	@echo "  run      - Run the application with uvicorn"
	@echo "  dev      - Run the application with uvicorn in reload mode"
	@echo "  build    - Build docker images"
	@echo "  up       - Run application using docker-compose"
	@echo "  stop     - Stop the application (kill uvicorn process)"
	@echo "  test     - Run tests with pytest"
	@echo "  lint     - Run ruff for linting"
	@echo "  clean    - Remove temporary files"

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

build:
	docker build -t gas-gateway-api .

up:
	docker-compose up

stop:
	pkill -f uvicorn || true
	@echo "GAS Gateway API stopped."

test:
	PYTHONPATH=. pytest tests/

lint:
	ruff check .
	black --check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
