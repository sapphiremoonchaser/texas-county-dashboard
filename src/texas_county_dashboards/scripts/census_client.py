"""
Downloads data from the Census API
"""
import requests
import pandas as pd
from notebooks.data_exploration.census_api_exploration.census_api_exploration import \
    response, df


class CensusClient:
    """Download Census API data"""

    BASE_URL = "https://api.census.gov/data"

    def __init__(
        self,
        year: int = 2024,  # Set the census year
        dataset: str = "acs/acs5",  # Set the census catalog
    ):
        # Save the variables that were passed in
        self.year = year
        self.dataset = dataset

        # Create the url
        self.url = (
            f"{self.BASE_URL}/{self.year}/{self.dataset}"
        )


    def _get(
        self,
        variables,
        geography
    ):
        """
        Download Census data.

        Parameters
            variables (list[str]): Variables to request.
            geography (dict): Geography parameters.
        """

        params = {
            "get": ",".join(variables),
            **geography
        }

        response = requests.get(
            self.url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return pd.DataFrame(
            data[1:],
            columns=data[0],
        )


    def county_profile(self):
        variables = [
            "NAME",
            *ACS_COUNTY_PROFILE.values(),
        ]

        df = self._get(
            variables=variables,
            geography={
                "for": "county",
                "in": "state:48"
            },
        )