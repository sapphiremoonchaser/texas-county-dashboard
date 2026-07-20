"""
Downloads data from the Census API
"""
import requests
import pandas as pd
from dash import clientside_callback
from dateutil.tz.win import valuestodict
from numpy.ma.extras import column_stack

from texas_county_dashboards.constants.census import ACS_COUNTY_PROFILE


class CensusClient:
    """Download Census API data"""

    BASE_URL = "https://api.census.gov/data"

    def __init__(
        self,
        year: int = 2024,  # Set the census year
        dataset: str = "acs/acs5",  # Set the census catalog
        api_key: str | None = None,
    ):
        # Save the variables that were passed in
        self.year = year
        self.dataset = dataset
        self.api_key = api_key

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

        if self.api_key:
            params["key"] = self.api_key

        print(self.url)
        print(params)

        response = requests.get(
            self.url,
            params=params,
            timeout=30
        )

        print("Requested URL:")
        print(response.request.url)

        print("\nFinal URL:")
        print(response.url)

        print("\nRedirect History:")
        for r in response.history:
            print(r.status_code, r.url)

        print("\nResponse:")
        print(response.text[:500])

        # Raise an exception if 404, 500, or 403 error returned
        response.raise_for_status()

        # Census API returns json
        data = response.json()

        return pd.DataFrame(
            data[1:], # skip first row of column names
            columns=data[0], # first row becomes column names
        )


    def county_profile(self):
        """
        Download Census data and return a dataframe.

        Returns
            df: Pandas DataFrame with requested columns from census api
        """
        # Build list of variables to request
        variables = [
            "NAME",
            *ACS_COUNTY_PROFILE.values(),
        ]

        df = self._get(
            variables=variables,
            geography={
                "for": "county:*", # All counties
                "in": "state:48" # In Texas
            },
        )

        # Rename the columns
        rename_map = {
            value: key
            for key, value in ACS_COUNTY_PROFILE.items()
        }

        df = df.rename(columns=rename_map)

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *ACS_COUNTY_PROFILE.keys()
        ]

        df = df[columns]

        return df

