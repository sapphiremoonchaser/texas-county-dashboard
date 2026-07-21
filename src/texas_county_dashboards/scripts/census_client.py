"""
Downloads data from the Census API
"""
import requests
import pandas as pd

from texas_county_dashboards.constants.census import TEXAS_COUNTIES

from texas_county_dashboards.variables.county_profile import COUNTY_PROFILE
from texas_county_dashboards.variables.education_profile import EDUCATION_PROFILE
from texas_county_dashboards.variables.employment_profile import EMPLOYMENT_PROFILE
from texas_county_dashboards.variables.demographics_profile import DEMOGRAPHICS_PROFILE
from texas_county_dashboards.variables.economics_profile import ECONOMICS_PROFILE
from texas_county_dashboards.variables.housing_profile import HOUSING_PROFILE


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
        variables: dict[str, str]
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
            *COUNTY_PROFILE.values()
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and chaning number to numerical datatype
        df = self._clean_dataframe(
            df,
            COUNTY_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *COUNTY_PROFILE.keys()
        ]

        print(df.columns.to_list())

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
            *EDUCATION_PROFILE.values(),
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and chaning number to numerical datatype
        df = self._clean_dataframe(
            df,
            EDUCATION_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *EDUCATION_PROFILE.keys()
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
            *EMPLOYMENT_PROFILE.values()
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and chaning number to numerical datatype
        df = self._clean_dataframe(
            df,
            EMPLOYMENT_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *EMPLOYMENT_PROFILE.keys()
        ]

        df = df[columns]

        return df


    def demographics_profile(self) -> pd.DataFrame:
        """
        Download demographics data from census api.

        :return: dataframe with demographics data
        """
        # Build list of variables to request
        variables = [
            "NAME",
            *DEMOGRAPHICS_PROFILE.values()
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and changing numberes to numerical datatypes
        df = self._clean_dataframe(
            df,
            DEMOGRAPHICS_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *DEMOGRAPHICS_PROFILE.keys()
        ]

        df = df[columns]

        return df


    def economics_profile(self) -> pd.DataFrame:
        """
        Download economic health data from census api.

        :return: dataframe with economic data
        """
        # Build list of variables to request
        variables = [
            "NAME",
            *ECONOMICS_PROFILE.values()
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and changing numberes to numerical datatypes
        df = self._clean_dataframe(
            df,
            ECONOMICS_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *ECONOMICS_PROFILE.keys()
        ]

        df = df[columns]

        return df


    def housing_profile(self) -> pd.DataFrame:
        """
        Download housing data from census api.

        :return: dataframe with housing data
        """
        # Build list of variables to request
        variables = [
            "NAME",
            *HOUSING_PROFILE.values()
        ]

        df = self._get(
            variables=variables,
            geography=TEXAS_COUNTIES
        )

        # Clean data by renaming columns and changing numberes to numerical datatypes
        df = self._clean_dataframe(
            df,
            HOUSING_PROFILE
        )

        # Reorder the columns
        columns = [
            "state",
            "county",
            "NAME",
            *HOUSING_PROFILE.keys()
        ]

        df = df[columns]

        return df