import os
from dotenv import load_dotenv

from src.texas_county_dashboards.scripts.census_client import CensusClient

# Retrieve the api key
load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")

census_client = CensusClient(
    api_key=api_key
)

county_profile = census_client.county_profile()

x = 1