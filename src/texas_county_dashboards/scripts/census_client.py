"""
Downloads data from the Census API
"""
import requests
import pandas as pd

from texas_county_dashboards.constants.census import (
    ACS_COUNTY_PROFILE,
    ACS_EDUCATION,
    ACS_EMPLOYMENT,
    TEXAS_COUNTIES
)


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
        variables: list[str],
        geography: dict[str, str]
    ) -> pd.DataFrame:
        """
        Download Census data.

        Parameters
            variables (list[str]): Variables to request.
            geography (dict): Geography parameters.
        :return: Pandas DataFrame with requested columns from census api
        """

        params = {
            "get": ",".join(variables),
            **geography
        }

        if self.api_key:
            params["key"] = self.api_key

        response = requests.get(
            self.url,
            params=params,
            timeout=30
        )

        # Raise an exception if 404, 500, or 403 error returned
        response.raise_for_status()

        # Census API returns json
        data = response.json()

        return pd.DataFrame(
            data[1:], # skip first row of column names
            columns=data[0], # first row becomes column names
        )


    def _clean_dataframe(
        self,
        df: pd.DataFrame,
        variables: list[str]
    ) -> pd.DataFrame:
        """
        Helper function for cleaning dataframes after retrieving census api data.

        :param df: dataframe to be cleaned
        :param variables: columns of dataframe
        :return: cleaned dataframe
        """
        # Rename the columns to something more readable
        rename_map = {
            value: key
            for key, value in variables.items()
        }

        df = df.rename(columns=rename_map)

        # Everything from census api is returned as a string
        # Convert numerical coumns to numerical datatypes
        numeric_columns = list(
            variables.keys()
        )

        df[numeric_columns] = (
            df[numeric_columns]
            .apply(pd.to_numeric)
        )

        return df


    def county_profile(self) -> pd.DataFrame:
        """
        Download Census data and return a dataframe.
        Columns:
            state
            county
            NAME
            population
            median_income
            median_age

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
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and chaning number to numerical datatype
        df = self._clean_dataframe(
            df,
            ACS_COUNTY_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *ACS_COUNTY_PROFILE.keys()
        ]

        df = df[columns]

        return df


    def education_profile(self) -> pd.DataFrame:
        """
        Download education Census data and return a dataframe.
        Columns:
            county
            population_24_plus
            bachelors_plus
            bachelors_plus_pct

        Returns
            df: Pandas DataFrame with requested columns from census api
        """
        # Build list of variables to request
        variables = [
            "NAME",
            *ACS_EDUCATION.values(),
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and chaning number to numerical datatype
        df = self._clean_dataframe(
            df,
            ACS_EDUCATION
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *ACS_EDUCATION.keys()
        ]

        df = df[columns]

        return df


    def employment_profile(self) -> pd.DataFrame:
        """
        Download employment Census data and return a dataframe.
        Columns:
            labor force
            unemployed

        Returns
            df: Pandas DataFrame with requested columns from census api
        """
        # Build list of variables to request
        variables = [
            "NAME",
            *ACS_EMPLOYMENT.values()
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and chaning number to numerical datatype
        df = self._clean_dataframe(
            df,
            ACS_EMPLOYMENT
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *ACS_EMPLOYMENT.keys()
        ]

        df = df[columns]

        return df
