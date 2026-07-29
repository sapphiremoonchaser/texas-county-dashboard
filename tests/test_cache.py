import pytest
import pandas as pd
from pathlib import Path

from texas_county_dashboards.cache import DataCache


def test_cache_saves_and_loads(tmp_path):

    cache = DataCache()

    cache.path = tmp_path / "test.parquet"

    df = pd.DataFrame(
        {
            "county": ["Travis"],
            "population": [1300000]
        }
    )

    cache.save(df)

    result = cache.load()

    pd.testing.assert_frame_equal(df, result)


def test_load_returns_none_when_file_missing(tmp_path):
    """
    Check that loading a missing cache returns None
    """
    cache = DataCache()
    cache.path = tmp_path / "missing.parquet"

    assert cache.load() is None


def test_exists_returns_false_when_cache_missing(tmp_path):
    """
    Test that the cache returns None before saving.
    """
    cache = DataCache()
    cache.path = tmp_path / "test.parquet"

    assert cache.exists() is False


def test_exists_returns_true_after_saving(tmp_path):
    cache = DataCache()
    cache.path = tmp_path / "test.parquet"

    df = pd.DataFrame(
        {
            "county": ["Travis"],
        }
    )

    cache.save(df)

    assert cache.exists() is True


def test_init_sets_custom_filename():
    cache = DataCache("custom.parquet")

    assert cache.path == Path("data/processed/custom.parquet")


def test_init_uses_default_filename():
    cache = DataCache()

    assert cache.path == Path("data/processed/county_metrics.parquet")


