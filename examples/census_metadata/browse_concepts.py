from src.texas_county_dashboards.scripts.census_metadata import (
    CensusVariables
)

census = CensusVariables()

# Browse concepts
concepts = census.concepts()

print(concepts[:25])