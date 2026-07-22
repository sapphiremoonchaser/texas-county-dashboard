"""
Analyze Texas county Census data.
Combines and Calculates
"""
import pandas as pd

from texas_county_dashboards.scripts.census_client import CensusClient

MERGE_KEYS = [
    "state",
    "county",
    "NAME",
    "GEOID"
]


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
        self.demographics_profile = None
        self.economics_profile = None
        self.housing_profile = None
        self.df = None


    def _merge_data(self) -> pd.DataFrame:
        """
        Merge the following 6 dataframes:
            county_profile
            education_profile
            employment_profile
            demogrphics_profile
            economics_profile
            housing_profile
        :return: one merged dataframe
        """
        profiles = [
            self.county_profile,
            self.education_profile,
            self.employment_profile,
            self.demographics_profile,
            self.economics_profile,
            self.housing_profile
        ]

        # Copy county profile
        df = profiles[0].copy()

        for profile in profiles[1:]:
            df = df.merge(
                profile,
                on=MERGE_KEYS,
                how="left"
            )

        return df


    def load_data(self) -> pd.DataFrame:
        """
        Load county_profile, education_profile, and employment_profile.
        :return: one dataframe with merged data
        """

        # Load census profiles
        self.county_profile = self.census_client.county_profile()
        self.education_profile = self.census_client.education_profile()
        self.employment_profile = self.census_client.employment_profile()
        self.demographics_profile = self.census_client.demographics_profile()
        self.economics_profile = self.census_client.economics_profile()
        self.housing_profile = self.census_client.housing_profile()

        # Merge all of the data
        self.df = self._merge_data()

        return self.df


    def save_data(
        self,
        path: str
    ):
        """
        Save processed county analytics data.
        :param path: path to savve to
        :return:
        """
        self.df.to_parquet(path, index=False)


    def calculate_metrics(self) -> pd.DataFrame:
        """
        Create derived county metrics.
            - bachelors_plus_pct
            - unemployment_rate
            - poverty_rate
            - homeownership_rate
            - vacancy_rate
        :return: df including original and derived metrics
        """

        # Make sure the data is loaded
        if self.df is None:
            self.load_data()

        # Calculate percent female
        self.df["percent_female"] = (
            self.df["female_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent male
        self.df["percent_male"] = (
            self.df["male_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent white
        self.df["percent_white"] = (
            self.df["white_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent black
        self.df["percent_black"] = (
            self.df["black_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate native american percent
        self.df["percent_native_american"] = (
            self.df["american_indian_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent asian
        self.df["percent_asian"] = (
            self.df["asian_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate native hawaiian percent
        self.df["percent_native_hawaiian"] = (
            self.df["native_hawaiian_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent other race
        self.df["percent_other_race"] = (
            self.df["other_race_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent 2 or more races
        self.df["percent_two_or_more"] = (
            self.df["two_or_more_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate percent hispanic
        self.df["percent_hispanic"] = (
            self.df["hispanic_population"]
            /
            self.df["population"]
            * 100
        )

        # Calculate poverty rate
        self.df["poverty_rate"] = (
                self.df["population_below_poverty"]
                /
                self.df["poverty_universe"]
                * 100
        )

        # Calculate percentage of people on snap
        self.df["percent_with_snap"] = (
                self.df["households_with_snap"]
                /
                self.df["population"]
                * 100
        )

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

        # Calculate percent of people with less than a high school degree
        self.df["percent_less_than_nineth_grade"] = (
            self.df["less_than_9th_grade"]
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

        # Percent of homes occupied
        self.df["percent_of_homes_occupied"] = (
            self.df["occupied_housing_units"]
            /
            self.df["housing_units"]
            * 100
        )

        # Percent of homes rented
        self.df["percent_of_homes_rented"] = (
            self.df['renter_occupied_units']
            /
            self.df["housing_units"]
            * 100
        )

        # Calculate homeownership rate
        self.df["homeownership_rate"] = (
            self.df["owner_occupied_units"]
            /
            self.df["occupied_housing_units"]
            * 100
        )

        # Calculate vacancy rate
        self.df["vacancy_rate"] = (
            self.df["vacant_housing_units"]
            /
            self.df["housing_units"]
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
                "median_household_income",
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


