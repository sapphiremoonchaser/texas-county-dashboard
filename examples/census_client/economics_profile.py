import os
from dotenv import load_dotenv

from src.texas_county_dashboards.scripts.census_client import CensusClient

# Retrieve the api key
load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")

census_client = CensusClient(
    api_key=api_key
)

economic_profile = census_client.economics_profile()

economic_profile.to_csv(
    "C:/Users/viole/dev/projects/portfolio/texas-county-dashboard/src"
    "/texas_county_dashboards/data/processed/texas_economic_profile.csv",
    index=False
)

x = 1