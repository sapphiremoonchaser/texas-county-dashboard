"""
Analyze Texas county Census data.
"""
import pandas as pd

from texas_county_dashboards.scripts.census_client import CensusClient


class CountyAnalytics:

    def __init__(
        self,
        census_client: CensusClient
    ):
        # Save variables that were passed in
        self.census_client = census_client

        self.county_profile = None
        self.education_profile = None
        self.employment_profile = None
        self.df = None


    def _merge_data(self) -> pd.DataFrame:
        """
        Merge the following 3 dataframes:
            county_profile
            education_profile
            employment_profile
        :return: one merged dataframe
        """
        df = self.county_profile.copy()

        # Merge county profile and education profile
        df = df.merge(
            self.education_profile,
            on=[
                "state",
                "county",
                "NAME"
            ],
            how="left"
        )

        # Merge above df with employment profile
        df = df.merge(
            self.employment_profile,
            on=[
                "state",
                "county",
                "NAME"
            ],
            how="left"
        )

        return df


    def load_data(self) -> pd.DataFrame:
        """
        Load county_profile, education_profile, and employment_profile.
        :return: one dataframe with merged data
        """
        # Load the county profile
        self.county_profile = (
            self.census_client
            .county_profile()
        )

        # Load the education profile
        self.education_profile = (
            self.census_client
            .education_profile()
        )

        # Load the employment profile
        self.employment_profile = (
            self.census_client
            .employment_profile()
        )

        # Merge all of the data
        self.df = self._merge_data()

        return self.df


    # ToDo: calculate_metrics()

    # ToDo: highest_income_counties()

    # ToDo: largest_counties()

    pass