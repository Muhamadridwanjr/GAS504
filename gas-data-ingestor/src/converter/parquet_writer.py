"""
Parquet conversion and partitioning logic.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.lib.logger import get_logger

logger = get_logger(__name__)


def convert_to_parquet(
    df: pd.DataFrame,
    symbol: str,
    output_dir: str | None = None,
) -> list[Path]:
    """
    Convert a DataFrame to Parquet files partitioned by year/month.

    Returns list of paths to the created temporary Parquet files.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="gas_parquet_")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    created_files: list[Path] = []

    # Group by year and month for partitioning
    if "year" not in df.columns or "month" not in df.columns:
        logger.warning("No year/month columns — writing single file")
        file_path = output_path / f"{symbol}_data.parquet"
        table = pa.Table.from_pandas(df)
        pq.write_table(table, str(file_path), compression="zstd")
        created_files.append(file_path)
        return created_files

    for (year, month), group in df.groupby(["year", "month"]):
        part_dir = output_path / f"symbol={symbol}" / f"year={year}" / f"month={month:02d}"
        part_dir.mkdir(parents=True, exist_ok=True)
        file_path = part_dir / "data.parquet"

        table = pa.Table.from_pandas(group)
        pq.write_table(table, str(file_path), compression="zstd")
        created_files.append(file_path)
        logger.debug("Wrote %s (%d rows)", file_path, len(group))

    logger.info("Created %d parquet partitions for %s", len(created_files), symbol)
    return created_files
