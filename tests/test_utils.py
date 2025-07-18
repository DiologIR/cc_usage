"""
Tests for the utils module.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from par_cc_usage.token_calculator import format_token_count
from par_cc_usage.utils import (
    ensure_directory,
    expand_path,
    format_bytes,
    format_datetime,
    format_time,
    format_time_range,
)


class TestExpandPath:
    """Test path expansion functionality."""

    def test_expand_home_directory(self):
        """Test expanding ~ in paths."""
        path = "~/Documents/test.txt"
        result = expand_path(path)
        
        assert isinstance(result, Path)
        assert "~" not in str(result)
        assert str(result).startswith(str(Path.home()))

    def test_expand_environment_variables(self):
        """Test expanding environment variables in paths."""
        with patch.dict(os.environ, {"TEST_DIR": "/custom/path", "USER": "testuser"}):
            path = "$TEST_DIR/data/$USER/file.txt"
            result = expand_path(path)
            
            assert str(result) == "/custom/path/data/testuser/file.txt"

    def test_expand_complex_path(self):
        """Test expanding path with both ~ and env vars."""
        with patch.dict(os.environ, {"SUBDIR": "projects"}):
            path = "~/$SUBDIR/test"
            result = expand_path(path)
            
            assert isinstance(result, Path)
            assert "~" not in str(result)
            assert "$SUBDIR" not in str(result)
            assert str(result).endswith("projects/test")

    def test_expand_already_absolute_path(self):
        """Test that absolute paths are returned as Path objects."""
        path = "/usr/local/bin/test"
        result = expand_path(path)
        
        assert isinstance(result, Path)
        assert str(result) == path

    def test_expand_relative_path(self):
        """Test that relative paths are converted to Path objects."""
        path = "./data/file.txt"
        result = expand_path(path)
        
        assert isinstance(result, Path)
        # Result should be a Path object representation of the relative path
        assert result == Path(path)

    def test_expand_path_object(self):
        """Test expanding Path object."""
        path = Path("~/test")
        result = expand_path(path)
        
        assert isinstance(result, Path)
        assert "~" not in str(result)


class TestEnsureDirectory:
    """Test directory creation functionality."""

    def test_create_new_directory(self, tmp_path):
        """Test creating a new directory."""
        test_dir = tmp_path / "new_directory"
        assert not test_dir.exists()
        
        ensure_directory(test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_existing_directory(self, tmp_path):
        """Test that existing directory is not recreated."""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()
        
        # Create a file to verify directory isn't recreated
        test_file = test_dir / "test.txt"
        test_file.write_text("content")
        
        ensure_directory(test_dir)
        
        # Directory and contents should still exist
        assert test_dir.exists()
        assert test_file.exists()
        assert test_file.read_text() == "content"

    def test_create_nested_directories(self, tmp_path):
        """Test creating nested directory structure."""
        test_dir = tmp_path / "level1" / "level2" / "level3"
        assert not test_dir.exists()
        
        ensure_directory(test_dir)
        
        assert test_dir.exists()
        assert test_dir.is_dir()


class TestFormatBytes:
    """Test byte formatting functionality."""

    def test_format_bytes_small(self):
        """Test formatting small byte values."""
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(1) == "1.0 B"
        assert format_bytes(999) == "999.0 B"

    def test_format_kilobytes(self):
        """Test formatting kilobyte values."""
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1536) == "1.5 KB"
        assert format_bytes(2048) == "2.0 KB"

    def test_format_megabytes(self):
        """Test formatting megabyte values."""
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1.5) == "1.5 MB"

    def test_format_gigabytes(self):
        """Test formatting gigabyte values."""
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"

    def test_format_terabytes(self):
        """Test formatting terabyte values."""
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_format_petabytes(self):
        """Test formatting petabyte values."""
        # After TB, the loop continues to PB
        assert "PB" in format_bytes(1024 * 1024 * 1024 * 1024 * 1024)


class TestFormatTokenCount:
    """Test token count formatting functionality."""

    def test_format_small_counts(self):
        """Test formatting small token counts."""
        assert format_token_count(0) == "0"
        assert format_token_count(1) == "1"
        assert format_token_count(999) == "999"

    def test_format_thousands(self):
        """Test formatting thousands."""
        assert format_token_count(1000) == "1K"
        assert format_token_count(1500) == "2K"  # .0f rounds to nearest int
        assert format_token_count(9999) == "10K"

    def test_format_millions(self):
        """Test formatting millions."""
        assert format_token_count(1000000) == "1.0M"
        assert format_token_count(1500000) == "1.5M"

    def test_format_billions(self):
        """Test formatting billions - function treats as millions."""
        assert format_token_count(1000000000) == "1000.0M"


class TestFormatTime:
    """Test time formatting functionality."""

    def test_format_12h(self):
        """Test 12-hour format."""
        dt = datetime(2025, 1, 9, 14, 30, 45, tzinfo=timezone.utc)
        assert format_time(dt, time_format="12h") == "02:30 PM"
        
        dt2 = datetime(2025, 1, 9, 0, 0, 0, tzinfo=timezone.utc)
        assert format_time(dt2, time_format="12h") == "12:00 AM"

    def test_format_24h(self):
        """Test 24-hour format."""
        dt = datetime(2025, 1, 9, 14, 30, 45, tzinfo=timezone.utc)
        assert format_time(dt, time_format="24h") == "14:30"
        
        dt2 = datetime(2025, 1, 9, 0, 0, 0, tzinfo=timezone.utc)
        assert format_time(dt2, time_format="24h") == "00:00"

    def test_format_default(self):
        """Test default format (24h)."""
        dt = datetime(2025, 1, 9, 14, 30, 45, tzinfo=timezone.utc)
        assert format_time(dt) == "14:30"


class TestFormatDatetime:
    """Test datetime formatting functionality."""

    def test_format_datetime_12h(self):
        """Test datetime formatting with 12-hour time."""
        dt = datetime(2025, 1, 9, 14, 30, 45, tzinfo=timezone.utc)
        result = format_datetime(dt, time_format="12h")
        
        assert "2025-01-09" in result
        assert "02:30:45 PM" in result

    def test_format_datetime_24h(self):
        """Test datetime formatting with 24-hour time."""
        dt = datetime(2025, 1, 9, 14, 30, 45, tzinfo=timezone.utc)
        result = format_datetime(dt, time_format="24h")
        
        assert "2025-01-09" in result
        assert "14:30:45" in result

    def test_format_datetime_with_timezone(self):
        """Test datetime formatting includes timezone."""
        tz = ZoneInfo("America/Los_Angeles")
        dt = datetime(2025, 1, 9, 14, 30, 45, tzinfo=tz)
        
        result = format_datetime(dt)
        assert "PST" in result or "PDT" in result


class TestFormatTimeRange:
    """Test time range formatting functionality."""

    def test_format_time_range_12h(self):
        """Test formatting time range with 12h format."""
        start = datetime(2025, 1, 9, 9, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 9, 17, 30, 0, tzinfo=timezone.utc)
        
        result = format_time_range(start, end, time_format="12h")
        assert "09:00 AM" in result
        assert "05:30 PM" in result
        assert "UTC" in result

    def test_format_time_range_24h(self):
        """Test formatting time range with 24h format."""
        start = datetime(2025, 1, 9, 9, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 9, 17, 30, 0, tzinfo=timezone.utc)
        
        result = format_time_range(start, end, time_format="24h")
        assert "09:00" in result
        assert "17:30" in result
        assert "UTC" in result