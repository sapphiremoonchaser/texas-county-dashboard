import pandas as pd
import pytest
from pathlib import Path

from texas_county_dashboards.scripts.boundary_loader import BoundaryLoader

test_boundary_file = (
    Path(__file__).parent.parent
    / "src"
    / "texas_county_dashboards"
    / "data"
    / "raw"
    /"tl_2024_us_county.zip"
)

def test_boundary_loader():
    loader = BoundaryLoader(test_boundary_file)

    gdf = loader.load_counties()

    assert len(gdf) == 254
    assert "geometry" in gdf.columns
    assert gdf["GEOID"].is_unique
    assert gdf.geometry.notna().all()
