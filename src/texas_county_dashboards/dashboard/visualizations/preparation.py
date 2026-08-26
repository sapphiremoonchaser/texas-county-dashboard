from dotenv import load_dotenv
import os
from pathlib import Path

from texas_county_dashboards.scripts.boundary_loader import BoundaryLoader
from texas_county_dashboards.scripts.county_analytics import CensusClient
from texas_county_dashboards.scripts.county_analytics import CountyAnalytics


def load_county_data():
    load_dotenv()

    api_key = os.getenv("CENSUS_API_KEY")

    census_client = CensusClient(api_key=api_key)

    analytics = CountyAnalytics(census_client=census_client)

    boundary_path = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "raw"
            / "tl_2024_us_county.zip"
    )

    boundary_loader = BoundaryLoader(boundary_path)

    boundary_gdf = boundary_loader.load_counties()

    county_data = analytics.run()

    county_data = county_data.drop(
        columns=["geometry"],
        errors="ignore"
    )

    county_gdf = boundary_gdf.merge(
        county_data,
        on="GEOID",
        how="left"
    )

    return county_gdf

