from src.texas_county_dashboards.scripts.census_metadata import (
    CensusVariables
)

census = CensusVariables()

# Search by keyword
income = census.search("income")

# Search for keyword in specific columns
income_df = income[
    [
        "variable",
        "label",
        "concept"
    ]
]