from dotenv import load_dotenv
import os
from pathlib import Path
import geopandas as gpd
import pandas as pd

from texas_county_dashboards.scripts.boundary_loader import BoundaryLoader
from texas_county_dashboards.scripts.county_analytics import CensusClient
from texas_county_dashboards.scripts.county_analytics import CountyAnalytics


def load_county_data() -> gpd.GeoDataFrame:
    """
    Load the county dataset by hitting the api. Also load the boundary data and then
    merge both datasets into a GeoDataFrame.

    :return:
        GeoDataFrame containing the county metrics and geography.
    """
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


def get_county_names(county_gdf):
    """Return sorted county names."""
    return sorted(county_gdf["NAME"].dropna().unique())


def get_selected_county(county_gdf, county_name):
    """Return the row for the selected county."""
    return county_gdf[
        county_gdf["NAME"] == county_name
    ].iloc[0]


def create_county_comparison(
    county_1,
    county_2,
    county_1_name,
    county_2_name,
    metric
) -> pd.DataFrame:
    """Create a dataframe comparing two counties for a given metric"""

    return pd.DataFrame({
        "County": [county_1_name, county_2_name],
        metric:[
            county_1[metric],
            county_2[metric]
        ],
    })

