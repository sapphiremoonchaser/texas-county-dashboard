from dotenv import load_dotenv
import os

from texas_county_dashboards.scripts.county_analytics import CensusClient
from texas_county_dashboards.scripts.county_analytics import CountyAnalytics


def load_county_data():
    load_dotenv()

    api_key = os.getenv("CENSUE_API_KEY")

    census_client = CensusClient(api_key=api_key)

    analytics = CountyAnalytics(census_client=census_client)

    return analytics.run()

