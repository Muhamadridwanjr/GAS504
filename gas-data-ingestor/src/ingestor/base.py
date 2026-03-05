"""
Base class for data source readers.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

import pandas as pd


class BaseSource(ABC):
    """Abstract base class for data source readers."""

    @abstractmethod
    def read(self, chunk_size: int = 100000) -> Iterator[pd.DataFrame]:
        """
        Read data in chunks and yield DataFrames.

        Args:
            chunk_size: Number of rows per chunk.

        Yields:
            pd.DataFrame: A chunk of data.
        """
        ...

    @abstractmethod
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate that the DataFrame has the required columns."""
        ...
