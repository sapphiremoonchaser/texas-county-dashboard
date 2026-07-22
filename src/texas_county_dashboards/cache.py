"""
This is a class to store data in for caching.
"""
from pathlib import Path
import pandas as pd

PROCESSED_DATA = Path("data/processed")


class DataCache:
    """
    Save and load processed data.
    """

    def __init__(
        self,
        filename="county_metrics.parquet"
    ):
        self.path = PROCESSED_DATA / filename

        PROCESSED_DATA.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(
        self,
        df
    ):
        df.to_parquet(self.path)

    def load(self):
        if not self.path.exists():
            return None

        return pd.read_parquet(self.path)

    def exists(self):
        return self.path.exists()


