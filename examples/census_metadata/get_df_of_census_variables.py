from src.texas_county_dashboards.scripts.census_metadata import (
    CensusVariables
)

census = CensusVariables()

# Get a dataframe of census variables
variables = census.download()