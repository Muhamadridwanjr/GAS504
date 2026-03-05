"""
FastAPI entry point for gas-data-ingestor.
Worker service that converts OHLCV data to Parquet, uploads to MinIO/S3,
and optionally generates text summaries for vector DB.
"""
from __future__ import annotations

import asyncio
import shutil
import tempfile
import uuid
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.security.middleware import InternalKeyMiddleware

from pydantic import BaseModel, Field

from src.config import settings
from src.lib.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

# ── In-memory job tracker ────────────────────────────────────────────────────
jobs: Dict[str, dict] = {}


class IngestRequest(BaseModel):
    source_type: str = Field(default="csv", description="excel, csv, or api")
    source_path: str = Field(default="", description="Path to file (for excel/csv)")
    symbol: str = Field(default="XAUUSD")
    generate_summary: bool = Field(default=True)


class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str = ""
    rows_processed: int = 0


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


async def run_ingestion(job_id: str, request: IngestRequest):
    """Background task that runs the full ingestion pipeline."""
    jobs[job_id] = {"status": "running", "message": "Starting...", "rows_processed": 0}

    try:
        # 1. Read data
        source_path = request.source_path or settings.SOURCE_PATH
        source_type = request.source_type or settings.SOURCE_TYPE

        if source_type in ("excel", "csv"):
            from src.ingestor.excel_reader import ExcelCSVReader
            reader = ExcelCSVReader(source_path)
        else:
            from src.ingestor.api_reader import APIReader
            reader = APIReader()

        from src.ingestor.validator import validate_ohlcv
        from src.converter.parquet_writer import convert_to_parquet
        from src.storage.s3_client import S3Client

        s3 = S3Client()
        total_rows = 0
        all_summaries = []
        tmp_base = tempfile.mkdtemp(prefix="gas_ingest_")

        jobs[job_id]["message"] = "Reading data..."

        for chunk in reader.read(chunk_size=settings.CHUNK_SIZE):
            # 2. Validate
            clean = validate_ohlcv(chunk)
            if clean.empty:
                continue

            # 3. Convert to Parquet
            parquet_files = convert_to_parquet(clean, request.symbol, output_dir=tmp_base)

            # 4. Upload to S3
            s3.upload_partitions(parquet_files, tmp_base)

            total_rows += len(clean)
            jobs[job_id]["rows_processed"] = total_rows
            jobs[job_id]["message"] = f"Processed {total_rows:,} rows..."

            # 5. Generate summaries
            if request.generate_summary:
                from src.summarizer.text_generator import generate_summary
                summaries = generate_summary(clean, request.symbol, settings.SUMMARY_PERIOD)
                all_summaries.extend(summaries)

        # 6. Send summaries to vector DB
        if all_summaries:
            from src.summarizer.embedder import VectorEmbedder
            embedder = VectorEmbedder()
            jobs[job_id]["message"] = "Sending summaries to vector DB..."
            await embedder.send_summaries(all_summaries)

        # Cleanup
        shutil.rmtree(tmp_base, ignore_errors=True)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = f"Done. {total_rows:,} rows ingested."
        logger.info("Job %s completed: %d rows", job_id, total_rows)

    except Exception as e:
        logger.error("Job %s failed: %s", job_id, e)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting %s on port %d [%s]",
        settings.SERVICE_NAME,
        settings.PORT,
        settings.ENVIRONMENT,
    )
    logger.info("%s ready ✓", settings.SERVICE_NAME)
    yield
    logger.info("%s shutdown complete.", settings.SERVICE_NAME)


app = FastAPI(
    title="gas-data-ingestor",
    description=(
        "Worker service for ingesting OHLCV data, converting to Parquet, "
        "uploading to MinIO/S3, and generating text summaries for vector DB."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ingest", status_code=202, tags=["Ingest"])
async def ingest(request: IngestRequest, bg: BackgroundTasks):
    """Trigger a data ingestion job."""
    job_id = str(uuid.uuid4())[:8]
    bg.add_task(run_ingestion, job_id, request)
    return {"job_id": job_id, "status": "accepted"}


@app.get("/ingest/{job_id}", response_model=JobStatus, tags=["Ingest"])
async def get_job_status(job_id: str):
    """Get the status of an ingestion job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    j = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=j["status"],
        message=j.get("message", ""),
        rows_processed=j.get("rows_processed", 0),
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check."""
    return HealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version="1.0.0",
        environment=settings.ENVIRONMENT,
    )
# Internal security — must be last (runs first due to starlette ordering)
app.add_middleware(InternalKeyMiddleware)
