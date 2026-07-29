import pytest
from requests import HTTPError
from unittest.mock import patch, Mock
import pandas as pd

from texas_county_dashboards.scripts.census_client import CensusClient
from texas_county_dashboards.variables.county import COUNTY_PROFILE
from texas_county_dashboards.variables.education import EDUCATION_PROFILE
from texas_county_dashboards.variables.housing import HOUSING_PROFILE
from texas_county_dashboards.variables.employment import EMPLOYMENT_PROFILE
from texas_county_dashboards.variables.demographics import DEMOGRAPHICS_PROFILE
from texas_county_dashboards.variables.economics import ECONOMICS_PROFILE


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
    """
    Checking for correct columns, datatypes for numerical data, and values
    """
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


def test_add_geoid():
    client = CensusClient()

    # Create mock dataframe
    df = pd.DataFrame({
        "state": ["48"],
        "county": ["453"]
    })

    df = client._add_geoid(df)

    assert df.loc[0, "GEOID"] == "48453"


def test_add_geoid_zero_padding():
    client = CensusClient()

    df = pd.DataFrame({
        "state": [1],
        "county": [7]
    })

    df = client._add_geoid(df)

    assert df.loc[0, "GEOID"] == "01007"


# When requests.get() is called inside census_client.py,
# replace is with a mock object so we don't make an HTTP request everytime
@patch("texas_county_dashboards.scripts.census_client.requests.get")
def test_get_returns_dataframe(mock_get):

    # Create a fake response
    fake_response = Mock()

    # fake json returned
    fake_response.json.return_value = [
        ["NAME", "population", "state", "county"],
        ["Travis County", "1000", "48", "453"]
    ]

    # Fake successful HTTP request
    fake_response.raise_for_status.return_value = None

    # Tells requests.get() what to return
    mock_get.return_value = fake_response

    # Create the client
    client = CensusClient()

    # Call the method
    df = client._get(
        variables=["NAME", "population"],
        geography={"for": "county:*", "in": "state:48"},
    )

    # Check that the correct number of rows are returned
    assert len(df) == 1
    assert df.loc[0, "NAME"] == "Travis County"


@patch("texas_county_dashboards.scripts.census_client.requests.get")
def test_get_sends_correct_parameters(mock_get):

    fake = Mock()

    fake.raise_for_status.return_value = None

    fake.json.return_value = [
        ["NAME"],
    ]

    mock_get.return_value = fake

    client = CensusClient(api_key="ABC123")

    client._get(
        variables=["NAME", "population"],
        geography={"for": "county:*"}
    )

    mock_get.assert_called_once_with(
        client.url,
        params={
            "get": "NAME,population",
            "for": "county:*",
            "key": "ABC123",
        },
        timeout=30,
    )


def test_profile_formats_dataframe(monkeypatch):

    client = CensusClient()

    raw = pd.DataFrame({
        "NAME": ["Travis County"],
        "B01003_001E": ["1000"],
        "state": ["48"],
        "county": ["453"],
    })

    monkeypatch.setattr(client, "_get", lambda **kwargs: raw)

    variables = {
        "population": "B01003_001E"
    }

    df = client._profile(variables)

    assert list(df.columns) == [
        "state",
        "county",
        "GEOID",
        "NAME",
        "population",
    ]

    assert df.loc[0, "population"] == 1000
    assert df.loc[0, "GEOID"] == "48453"


def test_county_profile_calls_profile():
    client = CensusClient()

    with patch.object(client, "_profile") as mock_profile:
        client.county_profile()
        mock_profile.assert_called_once_with(COUNTY_PROFILE)


def test_education_profile_calls_profile():
    client = CensusClient()

    with patch.object(client, "_profile") as mock_profile:
        client.education_profile()
        mock_profile.assert_called_once_with(EDUCATION_PROFILE)


def test_economic_profile_calls_profile():
    client = CensusClient()
    with patch.object(client, "_profile") as mock_profile:
        client.economics_profile()
        mock_profile.assert_called_once_with(ECONOMICS_PROFILE)


def test_housing_profile_calls_profile():
    client = CensusClient()
    with patch.object(client, "_profile") as mock_profile:
        client.housing_profile()
        mock_profile.assert_called_once_with(HOUSING_PROFILE)


def test_employment_profile_calls_profile():
    client = CensusClient()
    with patch.object(client, "_profile") as mock_profile:
        client.employment_profile()
        mock_profile.assert_called_once_with(EMPLOYMENT_PROFILE)


def test_demographic_profile_calls_profile():
    client = CensusClient()
    with patch.object(client, "_profile") as mock_profile:
        client.demographics_profile()
        mock_profile.assert_called_once_with(DEMOGRAPHICS_PROFILE)


@patch("texas_county_dashboards.scripts.census_client.requests.get")
def test_get_raises_http_error(mock_get):

    fake = Mock()

    fake.raise_for_status.side_effect = HTTPError("404")

    mock_get.return_value = fake

    client = CensusClient()

    with pytest.raises(HTTPError):
        client._get(
            variables=["NAME"],
            geography={"for": "county:*"},
        )

