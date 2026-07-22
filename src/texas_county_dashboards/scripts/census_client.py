"""
Downloads data from the Census API
"""
import requests
import pandas as pd

from texas_county_dashboards.constants.census import TEXAS_COUNTIES

from texas_county_dashboards.variables.county import COUNTY_PROFILE
from texas_county_dashboards.variables.education import EDUCATION_PROFILE
from texas_county_dashboards.variables.employment import EMPLOYMENT_PROFILE
from texas_county_dashboards.variables.demographics import DEMOGRAPHICS_PROFILE
from texas_county_dashboards.variables.economics import ECONOMICS_PROFILE
from texas_county_dashboards.variables.housing import HOUSING_PROFILE
from texas_county_dashboards.cache import DataCache


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

        # Check for cahced data
        self.cache = DataCache()


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


    def _profile(
        self,
        variables: dict[str, str]
    ) -> pd.DataFrame:
        """
        Download and clean a Census profile.

        Parameters:
            variables (dict): Dictionary mapping friendly names to census variables.

        Returns:
            Cleaned dataframe.
        """

        # Add NAME so we keep the count name
        census_variables = [
            "NAME",
            *variables.values()
        ]

        df = self._get(
            variables=census_variables,
            geography=TEXAS_COUNTIES
        )

        # Rename columns and convert numeric columns
        df = self._clean_dataframe(
            df,
            variables
        )

        df = self._add_geoid(df)

        # Standard profile columns
        columns = [
            "state",
            "county",
            "GEOID",
            "NAME",
            *variables.keys()
        ]

        return df[columns]


    def _add_geoid(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create 5-digit county FIPS codes.
        :param df:
        :return:
        """

        df["GEOID"] = (
            df["state"]
            .astype(str)
            .str.zfill(2)
            +
            df["county"]
            .astype(str)
            .str.zfill(3)
        )

        return df


    def county_profile(self) -> pd.DataFrame:
        """
        Download Census data and return a dataframe.

        Returns
            df: Pandas DataFrame with requested columns from census api
        """

        return self._profile(COUNTY_PROFILE)


    def education_profile(self) -> pd.DataFrame:
        """
        Download education Census data and return a dataframe.

        Returns
            df: Pandas DataFrame with requested columns from census api
        """

        return self._profile(EDUCATION_PROFILE)


    def employment_profile(self) -> pd.DataFrame:
        """
        Download employment Census data and return a dataframe.

        Returns
            df: Pandas DataFrame with requested columns from census api
        """

        return self._profile(EMPLOYMENT_PROFILE)


    def demographics_profile(self) -> pd.DataFrame:
        """
        Download demographics data from census api.

        :return: dataframe with demographics data
        """

        return self._profile(DEMOGRAPHICS_PROFILE)


    def economics_profile(self) -> pd.DataFrame:
        """
        Download economic health data from census api.

        :return: dataframe with economic data
        """

        return self._profile(ECONOMICS_PROFILE)


    def housing_profile(self) -> pd.DataFrame:
        """
        Download housing data from census api.

        :return: dataframe with housing data
        """

        return self._profile(HOUSING_PROFILE)

