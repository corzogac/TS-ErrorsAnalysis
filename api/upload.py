# ---------------------------------------------------------------------------
# File    : api/upload.py
# Purpose : Streaming file upload handler for large files (Stage 8)
# Version : 1.0
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
"""
Streaming file upload handling for large CSV/data files.

Features:
- Chunked reading to handle large files without memory issues
- CSV parsing with streaming
- Progress tracking
- Data validation during upload
"""

import csv
import io
from typing import List, Dict, Any, AsyncIterator
import aiofiles
from fastapi import UploadFile
import numpy as np


async def stream_csv_file(file: UploadFile, chunk_size: int = 8192) -> AsyncIterator[List[str]]:
    """
    Stream CSV file line by line.

    Args:
        file: Uploaded file object
        chunk_size: Size of chunks to read

    Yields:
        List of values for each row
    """
    buffer = ""

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break

        # Decode chunk
        chunk_str = chunk.decode('utf-8', errors='ignore')
        buffer += chunk_str

        # Process complete lines
        lines = buffer.split('\n')
        buffer = lines[-1]  # Keep incomplete line in buffer

        for line in lines[:-1]:
            if line.strip():
                # Parse CSV line
                reader = csv.reader([line])
                for row in reader:
                    yield row

    # Process remaining buffer
    if buffer.strip():
        reader = csv.reader([buffer])
        for row in reader:
            yield row


async def parse_csv_columns(
    file: UploadFile,
    predicted_col: int = 0,
    target_col: int = 1,
    skip_header: bool = True,
    max_rows: int = None
) -> Dict[str, Any]:
    """
    Parse CSV file with streaming to extract predicted and target columns.

    Args:
        file: Uploaded CSV file
        predicted_col: Column index for predicted values (0-based)
        target_col: Column index for target values (0-based)
        skip_header: Whether to skip first row
        max_rows: Maximum number of rows to read (None = all)

    Returns:
        Dict with parsed data and metadata
    """
    predicted_values = []
    target_values = []
    errors = []
    row_count = 0
    skipped_rows = 0

    # Reset file pointer
    await file.seek(0)

    # Stream and parse
    async for row_idx, row in enumerate_async(stream_csv_file(file)):
        # Skip header if requested
        if skip_header and row_idx == 0:
            continue

        # Check max rows
        if max_rows and row_count >= max_rows:
            break

        try:
            # Extract values
            if len(row) <= max(predicted_col, target_col):
                raise ValueError(f"Row has {len(row)} columns, need at least {max(predicted_col, target_col) + 1}")

            pred_val = float(row[predicted_col])
            target_val = float(row[target_col])

            # Check for valid values
            if np.isfinite(pred_val) and np.isfinite(target_val):
                predicted_values.append(pred_val)
                target_values.append(target_val)
                row_count += 1
            else:
                skipped_rows += 1

        except (ValueError, IndexError) as e:
            skipped_rows += 1
            errors.append({
                'row': row_idx + 1,
                'error': str(e),
                'data': row[:5] if len(row) > 5 else row  # First 5 columns for debugging
            })

            # Stop if too many errors
            if len(errors) > 100:
                break

    return {
        'predicted': predicted_values,
        'target': target_values,
        'metadata': {
            'total_rows': row_count,
            'skipped_rows': skipped_rows,
            'error_count': len(errors),
            'errors': errors[:10]  # Return first 10 errors only
        }
    }


async def enumerate_async(async_iter: AsyncIterator) -> AsyncIterator:
    """Async version of enumerate()."""
    count = 0
    async for item in async_iter:
        yield count, item
        count += 1


async def save_upload_temp(file: UploadFile, max_size_mb: int = 100) -> str:
    """
    Save uploaded file to temp location with size limit.

    Args:
        file: Uploaded file
        max_size_mb: Maximum file size in MB

    Returns:
        Path to saved temp file

    Raises:
        ValueError: If file exceeds size limit
    """
    import tempfile
    import os

    max_size = max_size_mb * 1024 * 1024

    # Create temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
    os.close(temp_fd)

    try:
        # Write file in chunks
        total_size = 0

        async with aiofiles.open(temp_path, 'wb') as f:
            while True:
                chunk = await file.read(8192)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > max_size:
                    os.unlink(temp_path)
                    raise ValueError(f"File exceeds maximum size of {max_size_mb}MB")

                await f.write(chunk)

        return temp_path

    except Exception:
        # Clean up on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def validate_csv_structure(file_path: str, expected_columns: int = 2) -> Dict[str, Any]:
    """
    Validate CSV file structure without loading entire file.

    Args:
        file_path: Path to CSV file
        expected_columns: Expected number of columns

    Returns:
        Validation results
    """
    with open(file_path, 'r') as f:
        reader = csv.reader(f)

        # Check first few rows
        rows_checked = 0
        column_counts = {}

        for row in reader:
            col_count = len(row)
            column_counts[col_count] = column_counts.get(col_count, 0) + 1
            rows_checked += 1

            if rows_checked >= 100:
                break

    # Determine most common column count
    most_common_cols = max(column_counts, key=column_counts.get)

    return {
        'valid': most_common_cols >= expected_columns,
        'column_counts': column_counts,
        'most_common_columns': most_common_cols,
        'rows_checked': rows_checked,
        'consistent': len(column_counts) == 1
    }


class ProgressTracker:
    """Track upload/processing progress."""

    def __init__(self):
        self.total_bytes = 0
        self.processed_bytes = 0
        self.rows_processed = 0

    def update(self, bytes_read: int, rows: int = 0):
        """Update progress."""
        self.processed_bytes += bytes_read
        self.rows_processed += rows

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress."""
        percentage = 0
        if self.total_bytes > 0:
            percentage = (self.processed_bytes / self.total_bytes) * 100

        return {
            'processed_bytes': self.processed_bytes,
            'total_bytes': self.total_bytes,
            'percentage': round(percentage, 2),
            'rows_processed': self.rows_processed
        }
