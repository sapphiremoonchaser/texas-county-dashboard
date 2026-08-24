"""
Cache data to avoid repeatedly hitting the api.
"""
from pathlib import Path
import pandas as pd


class DataCache:

    def __init__(
        self,
        filename="data/processed/county_metrics.parquet"
    ):
        self.filename = Path(filename)


    def save(
        self,
        df: pd.DataFrame
    ):
        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        df.to_parquet(self.filename)


    def load(self):
        return pd.read_parquet(self.filename)
