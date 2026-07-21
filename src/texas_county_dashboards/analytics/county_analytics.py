"""
Analyze Texas county Census data.
Combines and Calculates
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


    def calculate_metrics(self) -> pd.DataFrame:
        """
        Create derived county metrics.
        :return: df including original and derived metrics
        """

        # Make sure the data is loaded
        if self.df is None:
            self.load_data()

        # Calculate percent of people with a bachelor's degree or higher
        self.df["bachelors_plus_pct"] = (
            (
                self.df["bachelors"]
                + self.df["masters"]
                + self.df["professional"]
                + self.df["doctorate"]
            )
            /
            self.df["population_25_plus"]
            * 100
        )

        # Calculate unemployment rate
        self.df["unemployment_rate"] = (
            self.df["unemployed"]
            /
            self.df["labor_force"]
            * 100
        )

        return self.df


    def highest_income_counties(
        self,
        n=10
    ) -> pd.DataFrame:
        """
        Sort counties by highest income.

        :param n: top n counties
        :return: top n counties dataframe
        """
        return (
            self.df
            .sort_values(
                "median_income",
                ascending=False
            )
            .head(n)
        )


    def largest_counties(
        self,
        n=10
    ) -> pd.DataFrame:
        """
        Sort counties by largest population.

        :param n: top n counties
        :return: dataframe with top n largest counties by population
        """
        return (
            self.df
            .sort_values(
                "population",
                ascending=False
            )
            .head(n)
        )