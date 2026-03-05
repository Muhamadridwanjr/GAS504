#!/bin/bash
cd /home/mridwan3101/goldenaistrategy

# gas-data-ingestor
echo "Creating gas-data-ingestor..."
mkdir -p gas-data-ingestor/src/ingestor
mkdir -p gas-data-ingestor/src/converter
mkdir -p gas-data-ingestor/src/storage
mkdir -p gas-data-ingestor/src/summarizer
mkdir -p gas-data-ingestor/src/lib
mkdir -p gas-data-ingestor/src/workers
mkdir -p gas-data-ingestor/tests
touch gas-data-ingestor/src/__init__.py
touch gas-data-ingestor/src/main.py
touch gas-data-ingestor/src/config.py
touch gas-data-ingestor/src/ingestor/__init__.py
touch gas-data-ingestor/src/ingestor/base.py
touch gas-data-ingestor/src/ingestor/excel_reader.py
touch gas-data-ingestor/src/ingestor/api_reader.py
touch gas-data-ingestor/src/ingestor/validator.py
touch gas-data-ingestor/src/converter/__init__.py
touch gas-data-ingestor/src/converter/parquet_writer.py
touch gas-data-ingestor/src/storage/__init__.py
touch gas-data-ingestor/src/storage/s3_client.py
touch gas-data-ingestor/src/summarizer/__init__.py
touch gas-data-ingestor/src/summarizer/text_generator.py
touch gas-data-ingestor/src/summarizer/embedder.py
touch gas-data-ingestor/src/lib/__init__.py
touch gas-data-ingestor/src/lib/logger.py
touch gas-data-ingestor/src/lib/utils.py
touch gas-data-ingestor/Dockerfile
touch gas-data-ingestor/docker-compose.yml
touch gas-data-ingestor/.env.example
touch gas-data-ingestor/requirements.txt
echo "# gas-data-ingestor" > gas-data-ingestor/README.md

# gas-screener-service
echo "Creating gas-screener-service..."
mkdir -p gas-screener-service/src/api
mkdir -p gas-screener-service/src/core
mkdir -p gas-screener-service/src/clients
mkdir -p gas-screener-service/src/cache
mkdir -p gas-screener-service/src/lib
mkdir -p gas-screener-service/src/workers
mkdir -p gas-screener-service/tests
touch gas-screener-service/src/__init__.py
touch gas-screener-service/src/main.py
touch gas-screener-service/src/config.py
touch gas-screener-service/src/api/__init__.py
touch gas-screener-service/src/api/routes.py
touch gas-screener-service/src/api/models.py
touch gas-screener-service/src/core/__init__.py
touch gas-screener-service/src/core/orchestrator.py
touch gas-screener-service/src/core/parallel_executor.py
touch gas-screener-service/src/core/condition_evaluator.py
touch gas-screener-service/src/core/exceptions.py
touch gas-screener-service/src/clients/__init__.py
touch gas-screener-service/src/clients/indicator_client.py
touch gas-screener-service/src/clients/smc_client.py
touch gas-screener-service/src/clients/feature_client.py
touch gas-screener-service/src/cache/__init__.py
touch gas-screener-service/src/cache/redis_cache.py
touch gas-screener-service/src/lib/__init__.py
touch gas-screener-service/src/lib/logger.py
touch gas-screener-service/src/lib/utils.py
touch gas-screener-service/Dockerfile
touch gas-screener-service/docker-compose.yml
touch gas-screener-service/.env.example
touch gas-screener-service/requirements.txt
echo "# gas-screener-service" > gas-screener-service/README.md

# gas-fundamental-data-service
echo "Creating gas-fundamental-data-service..."
mkdir -p gas-fundamental-data-service/src/api
mkdir -p gas-fundamental-data-service/src/core
mkdir -p gas-fundamental-data-service/src/db/repositories
mkdir -p gas-fundamental-data-service/src/cache
mkdir -p gas-fundamental-data-service/src/ingestion
mkdir -p gas-fundamental-data-service/src/lib
mkdir -p gas-fundamental-data-service/src/workers
mkdir -p gas-fundamental-data-service/tests
touch gas-fundamental-data-service/src/__init__.py
touch gas-fundamental-data-service/src/main.py
touch gas-fundamental-data-service/src/config.py
touch gas-fundamental-data-service/src/api/__init__.py
touch gas-fundamental-data-service/src/api/routes.py
touch gas-fundamental-data-service/src/api/models.py
touch gas-fundamental-data-service/src/core/__init__.py
touch gas-fundamental-data-service/src/core/data_service.py
touch gas-fundamental-data-service/src/core/summary_generator.py
touch gas-fundamental-data-service/src/core/exceptions.py
touch gas-fundamental-data-service/src/db/__init__.py
touch gas-fundamental-data-service/src/db/database.py
touch gas-fundamental-data-service/src/db/models.py
touch gas-fundamental-data-service/src/db/repositories/__init__.py
touch gas-fundamental-data-service/src/db/repositories/fundamental_repo.py
touch gas-fundamental-data-service/src/cache/__init__.py
touch gas-fundamental-data-service/src/cache/redis_cache.py
touch gas-fundamental-data-service/src/ingestion/__init__.py
touch gas-fundamental-data-service/src/ingestion/base.py
touch gas-fundamental-data-service/src/ingestion/fred.py
touch gas-fundamental-data-service/src/ingestion/worldbank.py
touch gas-fundamental-data-service/src/ingestion/scheduler.py
touch gas-fundamental-data-service/src/lib/__init__.py
touch gas-fundamental-data-service/src/lib/logger.py
touch gas-fundamental-data-service/src/lib/utils.py
touch gas-fundamental-data-service/Dockerfile
touch gas-fundamental-data-service/docker-compose.yml
touch gas-fundamental-data-service/.env.example
touch gas-fundamental-data-service/requirements.txt
echo "# gas-fundamental-data-service" > gas-fundamental-data-service/README.md

# gas-calendar-news-service
echo "Creating gas-calendar-news-service..."
mkdir -p gas-calendar-news-service/src/api
mkdir -p gas-calendar-news-service/src/core
mkdir -p gas-calendar-news-service/src/db/repositories
mkdir -p gas-calendar-news-service/src/cache
mkdir -p gas-calendar-news-service/src/ingestion
mkdir -p gas-calendar-news-service/src/embedding
mkdir -p gas-calendar-news-service/src/lib
mkdir -p gas-calendar-news-service/src/workers
mkdir -p gas-calendar-news-service/tests
touch gas-calendar-news-service/src/__init__.py
touch gas-calendar-news-service/src/main.py
touch gas-calendar-news-service/src/config.py
touch gas-calendar-news-service/src/api/__init__.py
touch gas-calendar-news-service/src/api/routes.py
touch gas-calendar-news-service/src/api/models.py
touch gas-calendar-news-service/src/core/__init__.py
touch gas-calendar-news-service/src/core/calendar_service.py
touch gas-calendar-news-service/src/core/news_service.py
touch gas-calendar-news-service/src/core/summary_generator.py
touch gas-calendar-news-service/src/core/exceptions.py
touch gas-calendar-news-service/src/db/__init__.py
touch gas-calendar-news-service/src/db/database.py
touch gas-calendar-news-service/src/db/models.py
touch gas-calendar-news-service/src/db/repositories/__init__.py
touch gas-calendar-news-service/src/db/repositories/event_repo.py
touch gas-calendar-news-service/src/db/repositories/news_repo.py
touch gas-calendar-news-service/src/cache/__init__.py
touch gas-calendar-news-service/src/cache/redis_cache.py
touch gas-calendar-news-service/src/ingestion/__init__.py
touch gas-calendar-news-service/src/ingestion/ecocal_worker.py
touch gas-calendar-news-service/src/ingestion/parser_factory.py
touch gas-calendar-news-service/src/ingestion/scheduler.py
touch gas-calendar-news-service/src/embedding/__init__.py
touch gas-calendar-news-service/src/embedding/embedder.py
touch gas-calendar-news-service/src/embedding/vector_client.py
touch gas-calendar-news-service/src/lib/__init__.py
touch gas-calendar-news-service/src/lib/logger.py
touch gas-calendar-news-service/src/lib/utils.py
touch gas-calendar-news-service/Dockerfile
touch gas-calendar-news-service/docker-compose.yml
touch gas-calendar-news-service/.env.example
touch gas-calendar-news-service/requirements.txt
echo "# gas-calendar-news-service" > gas-calendar-news-service/README.md

# gas-tradingplan-service
echo "Creating gas-tradingplan-service..."
mkdir -p gas-tradingplan-service/src/api
mkdir -p gas-tradingplan-service/src/core
mkdir -p gas-tradingplan-service/src/db/repositories
mkdir -p gas-tradingplan-service/src/cache
mkdir -p gas-tradingplan-service/src/lib
mkdir -p gas-tradingplan-service/src/workers
mkdir -p gas-tradingplan-service/tests
touch gas-tradingplan-service/src/__init__.py
touch gas-tradingplan-service/src/main.py
touch gas-tradingplan-service/src/config.py
touch gas-tradingplan-service/src/api/__init__.py
touch gas-tradingplan-service/src/api/routes.py
touch gas-tradingplan-service/src/api/models.py
touch gas-tradingplan-service/src/core/__init__.py
touch gas-tradingplan-service/src/core/plan_manager.py
touch gas-tradingplan-service/src/core/exceptions.py
touch gas-tradingplan-service/src/db/__init__.py
touch gas-tradingplan-service/src/db/database.py
touch gas-tradingplan-service/src/db/models.py
touch gas-tradingplan-service/src/db/repositories/__init__.py
touch gas-tradingplan-service/src/db/repositories/plan_repo.py
touch gas-tradingplan-service/src/cache/__init__.py
touch gas-tradingplan-service/src/cache/redis_cache.py
touch gas-tradingplan-service/src/lib/__init__.py
touch gas-tradingplan-service/src/lib/logger.py
touch gas-tradingplan-service/src/lib/utils.py
touch gas-tradingplan-service/Dockerfile
touch gas-tradingplan-service/docker-compose.yml
touch gas-tradingplan-service/.env.example
touch gas-tradingplan-service/requirements.txt
echo "# gas-tradingplan-service" > gas-tradingplan-service/README.md

# gas-chart-service
echo "Creating gas-chart-service..."
mkdir -p gas-chart-service/src/api
mkdir -p gas-chart-service/src/core
mkdir -p gas-chart-service/src/clients
mkdir -p gas-chart-service/src/db/repositories
mkdir -p gas-chart-service/src/cache
mkdir -p gas-chart-service/src/lib
mkdir -p gas-chart-service/src/workers
mkdir -p gas-chart-service/tests
touch gas-chart-service/src/__init__.py
touch gas-chart-service/src/main.py
touch gas-chart-service/src/config.py
touch gas-chart-service/src/api/__init__.py
touch gas-chart-service/src/api/routes.py
touch gas-chart-service/src/api/models.py
touch gas-chart-service/src/core/__init__.py
touch gas-chart-service/src/core/orchestrator.py
touch gas-chart-service/src/core/template_manager.py
touch gas-chart-service/src/core/favorites_manager.py
touch gas-chart-service/src/core/exceptions.py
touch gas-chart-service/src/clients/__init__.py
touch gas-chart-service/src/clients/mt5_data_client.py
touch gas-chart-service/src/clients/indicator_client.py
touch gas-chart-service/src/clients/smc_client.py
touch gas-chart-service/src/db/__init__.py
touch gas-chart-service/src/db/database.py
touch gas-chart-service/src/db/models.py
touch gas-chart-service/src/db/repositories/__init__.py
touch gas-chart-service/src/db/repositories/template_repo.py
touch gas-chart-service/src/db/repositories/favorite_repo.py
touch gas-chart-service/src/cache/__init__.py
touch gas-chart-service/src/cache/redis_cache.py
touch gas-chart-service/src/lib/__init__.py
touch gas-chart-service/src/lib/logger.py
touch gas-chart-service/src/lib/utils.py
touch gas-chart-service/Dockerfile
touch gas-chart-service/docker-compose.yml
touch gas-chart-service/.env.example
touch gas-chart-service/requirements.txt
echo "# gas-chart-service" > gas-chart-service/README.md

echo "Done!"
