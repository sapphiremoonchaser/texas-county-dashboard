import pytest
import pandas as pd

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