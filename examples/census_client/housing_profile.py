import os
from dotenv import load_dotenv

from src.texas_county_dashboards.scripts.census_client import CensusClient

# Retrieve the api key
load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")

census_client = CensusClient(
    api_key=api_key
)

housing_profile = census_client.housing_profile()

housing_profile.to_csv(
    "C:/Users/viole/dev/projects/portfolio/texas-county-dashboard/src"
    "/texas_county_dashboards/data/processed/texas_housing_profile.csv",
    index=False
)

x = 1