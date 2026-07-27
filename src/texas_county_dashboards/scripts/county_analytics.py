"""
Provides analytics functionality for Texas county Census data.

This module combines Census datasets from multiple profiles,
creates derived county-level metrics, and provides methods for
ranking and analyzing counties.
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
    """
    Analyze and transform county Census data.

    This class combines Census profile datasets, calculates
    derived demographic, economic, education, employment,
    and housing metrics, and provides analytical methods
    for comparing counties.

    Attributes:
        census_client (CensusClient): Client used to retrieve Census data.
        df: DataFrame containing merged county data and calculated metrics.
    """
    def __init__(
        self,
        census_client: CensusClient
    ):
        # Store the variable so data can be retrieved lazily
        # when analytics are requested
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
        Merge Census profile DataFrame into a single county dataset.

        Each profile is joined using the shared geographic identifier:
        state, county, NAME, and GEOID.

        Returns:
            DataFrame containing all merged county-lebel Census data.
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

        for profile in profiles[1:]: # skip county bc we started with it
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
        Caclulate a percentage metric and store it in the dataframe.

        Division by zero values are replaced with missing values
        to prevent invalid calculations.

        Args:
            numerator (str): Column containing the count being measured
            denominator (str): Column containing the population base.
            output (str): Name of the new percentage column

        Returns:
            None. Adds a new column  to self.df
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
        Calculate demographic percentage metrics.

        Creates percentage values for:
            - Gender distribution
            - Race distribution
            - Hispanic population

        Returns:
            None. Adds calculated columns to self.df.
        """
        self._calculate_percentage(
            "female_population",
            "population",
            "percent_female"
        )

        self._calculate_percentage(
            "male_population",
            "population",
            "percent_male"
        )

        self._calculate_percentage(
            "white_population",
            "population",
            "percent_white"
        )

        self._calculate_percentage(
            "black_population",
            "population",
            "percent_black"
        )

        self._calculate_percentage(
            "american_indian_population",
            "population",
            "percent_native_american"
        )

        self._calculate_percentage(
            "asian_population",
            "population",
            "percent_asian"
        )

        self._calculate_percentage(
            "native_hawaiian_population",
            "population",
            "percent_native_hawaiian"
        )

        self._calculate_percentage(
            "other_race_population",
            "population",
            "percent_other_race"
        )

        self._calculate_percentage(
            "two_or_more_population",
            "population",
            "percent_two_or_more"
        )

        self._calculate_percentage(
            "hispanic_population",
            "population",
            "percent_hispanic"
        )


    def _calculate_economics(self) -> None:
        """
        Calculate metrics around poverty and government assistance.

        Returns:
            None. Adds calculated columns to self.df.
        """
        self._calculate_percentage(
            "population_below_poverty",
            "poverty_universe",
            "poverty_rate"
        )

        self._calculate_percentage(
            "households_with_snap",
            "population",
            "percent_with_snap"
        )


    def _calculate_education(self) -> None:
        """
        Calculate educated and uneducated percentages of population.

        Returns:
            None. Adds calculated metrics to self.df.
        """
        # Calculate total number of people with a bachelors degree or higher
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


