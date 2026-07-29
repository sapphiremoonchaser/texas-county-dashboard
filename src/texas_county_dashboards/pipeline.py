"""
Build the Texas County Analytics dataset.
"""
from streamlit.runtime.caching.cache_utils import Cache
from texas_county_dashboards.scripts.census_client import CensusClient
from texas_county_dashboards.scripts.county_analytics import CountyAnalytics
from texas_county_dashboards.scripts.cache import DataCache


def build_county_dataset():

    census_client = CensusClient()

    analytics = CountyAnalytics(
        census_client=census_client
    )

    county_df = analytics.calculate_metrics()

    cache = Cache()

