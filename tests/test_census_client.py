import pandas as pd

from texas_county_dashboards.scripts.census_client import CensusClient


def test_init_defaults():
    """
    Test initial values
    """

    client = CensusClient()

    assert client.year == 2024
    assert client.dataset == "acs/acs5"
    assert client.api_key is None
    assert client.url == "https://api.census.gov/data/2024/acs/acs5"


def test_clean_dataframe():
    client = CensusClient()

    # Create df with mock data
    df = pd.DataFrame({
        "B01003_001E": ["1000"],
        "B19013_001E": ["55000"],
        "NAME": ["Travis County"],
    })

    # Create variables map
    variables = {
        "population": "B01003_001E",
        "income": "B19013_001E",
    }

    # Clean the mock df
    cleaned = client._clean_dataframe(df, variables)

    # Check the columns
    assert list(cleaned.columns) == [
        "population",
        "income",
        "NAME"
    ]

    # Check datatype for numerical columns
    assert cleaned["population"].dtype.kind in "iu"
    assert cleaned["income"].dtype.kind in "iu"

    # Check values
    assert cleaned.loc[0, "population"] == 1000


