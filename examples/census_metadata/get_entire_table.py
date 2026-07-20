from src.texas_county_dashboards.scripts.census_metadata import (
    CensusVariables
)

census = CensusVariables()

# Get an entire table
age = census.table("B01001")

age_df = age[
    [
        "variable",
        "label"
    ]
]