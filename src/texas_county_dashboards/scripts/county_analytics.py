"""
Analyze Texas county Census data.
Combines and Calculates
"""
import pandas as pd

from texas_county_dashboards.scripts.census_client import CensusClient
from texas_county_dashboards.cache import DataCache

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


    def _calculate_percentage(
        self,
            numerator: str,
            denominator: str,
            output: str
    ) -> None:
        """
        Helper function for calculating percentages.

        :param numerator:
        :param denominator:
        :param output:
        :return:
        """
        self.df[output] = (
            self.df[numerator]
            .div(
                self.df[denominator].replace(0, pd.NA)
            )
            .mul(100)
        )


    def _calculate_demographics(self) -> None:
        """
        Create derived demographic metrics.
            - percent female
            - percent male
            - percent white
            - percent black
            - percent native american
            - percent asian
            - percent native hawaiian
            - percent other race
            - percent two or more races
            - percent hispanic
        """
        # Calculate percent female
        self._calculate_percentage(
            "female_population",
            "population",
            "percent_female"
        )

        # Calculate percent male
        self._calculate_percentage(
            "male_population",
            "population",
            "percent_male"
        )

        # Calculate percent white
        self._calculate_percentage(
            "white_population",
            "population",
            "percent_white"
        )

        # Calculate percent black
        self._calculate_percentage(
            "black_population",
            "population",
            "percent_black"
        )

        # Calculate native american percent
        self._calculate_percentage(
            "american_indian_population",
            "population",
            "percent_native_american"
        )

        # Calculate percent asian
        self._calculate_percentage(
            "asian_population",
            "population",
            "percent_asian"
        )

        # Calculate native hawaiian percent
        self._calculate_percentage(
            "native_hawaiian_population",
            "population",
            "percent_native_hawaiian"
        )

        # Calculate percent other race
        self._calculate_percentage(
            "other_race_population",
            "population",
            "percent_other_race"
        )

        # Calculate percent 2 or more races
        self._calculate_percentage(
            "two_or_more_population",
            "population",
            "percent_two_or_more"
        )

        # Calculate percent hispanic
        self._calculate_percentage(
            "hispanic_population",
            "population",
            "percent_hispanic"
        )


    def _calculate_economics(self) -> None:
        """
        Create derived economic metrics.
            - poverty rate
            - percent with snap
        """
        # Calculate poverty rate
        self._calculate_percentage(
            "population_below_poverty",
            "poverty_universe",
            "poverty_rate"
        )

        # Calculate percentage of people on snap
        self._calculate_percentage(
            "households_with_snap",
            "population",
            "percent_with_snap"
        )


    def _calculate_education(self) -> None:
        """
        Create derived education metrics.
            - percent with bachelors degree or higher
            - percent with less than 9th grade education
        """
        # Calculate percent of people with a bachelor's degree or higher
        self.df["bachelors_plus"] = (
            self.df["bachelors"]
            + self.df["masters"]
            + self.df["professional"]
            + self.df["doctorate"]
        )

        self._calculate_percentage(
            "bachelors_plus",
            "populations_25_plus",
            "perent_bachelors_plus"
        )

        # Calculate percent of people with less than a high school degree
        self._calculate_percentage(
            "less_than_ninth_grade",
            "population_25_plus",
            "percent_less_than_9th_grade"
        )


    def _calculate_employment(self) -> None:
        """
        Create derived employment metrics.
            - unemployment rate
        """
        # Calculate unemployment rate
        self._calculate_percentage(
            "unemployed",
            "labor_force",
            "unemployment_rate"
        )


    def _calculate_housing(self) -> None:
        """
        Create derived housing metrics.
            - percent homes occupied
            - percent of homes rented
            - homeownership rate
            - vacancy rate
        """
        # Percent of homes occupied
        self._calculate_percentage(
            "occupied_housing_units",
            "housing_units",
            "percent_of_homes_occupied"
        )

        # Percent of homes rented
        self._calculate_percentage(
            "renter_occupied_units",
            "occupied_housing_units",
            "percent_of_occupied_homes_rented"
        )

        # Calculate homeownership rate
        self._calculate_percentage(
            "owner_occupied_units",
            "occupied_housing_units",
            "homeownership_rate"
        )

        # Calculate vacancy rate
        self._calculate_percentage(
            "vacant_housing_units",
            "housing_units",
            "vacancy_rate"
        )

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


    def top_n(
        self,
        metric: str,
        n: int = 10,
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Return the top n counties based on the metric passed in.

        :param metric: Metric to be compared.
        :param n: Top n counties.
        :param ascending: ascending behavior, True or False
        :return: dataframe sorted by metric
        """
        return (
            self.df
            .sort_values(metric, ascending=ascending)
            .head(n)
        )


    def save_data(
        self,
        path: str
    ) -> None:
        """
        Save processed county analytics data.
        :param path: path to savve to
        :return:
        """
        self.df.to_parquet(path, index=False)


    def calculate_metrics(self) -> pd.DataFrame:
        """
        Create derived county metrics.
        :return: df including original and derived metrics
        """

        # Make sure the data is loaded
        if self.df is None:
            self.load_data()

        self._calculate_demographics()
        self._calculate_economics()
        self._calculate_education()
        self._calculate_employment()
        self._calculate_housing()

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
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "highest_income_counties",
            n=n
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
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "population",
            n
        )


