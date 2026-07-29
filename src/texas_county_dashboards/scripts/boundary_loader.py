from pathlib import Path

import geopandas as gpd


class BoundaryLoader:

    def __init__(
        self,
        boundary_path: Path
    ):
       self.boundary_path = boundary_path


    def load_texas_counties(self) -> gpd.GeoDataFrame:
        counties = gpd.read_file(self.boundary_path)

        texas = counties[
            counties["STATEFP"] == '48'
        ].copy

        return texas[
            [
                "GEOID",
                "NAME",
                "geometry"
            ]
        ]