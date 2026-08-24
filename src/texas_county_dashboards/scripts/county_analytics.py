"""
Provides analytics functionality for Texas county Census data.

This module combines Census datasets from multiple profiles,
creates derived county-level metrics, and provides methods for
ranking and analyzing counties.
"""
from pathlib import Path

import pandas as pd

from texas_county_dashboards.scripts.census_client import CensusClient
from texas_county_dashboards.scripts.boundary_loader import BoundaryLoader

MERGE_KEYS = [
    "state",
    "county",
    "NAME",
    "GEOID"
]

BOUNDARY_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "raw"
    /"tl_2024_us_county.zip"
)


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


    def _validate_dataframe(self) -> None:
        """
        Validate required columns exist before calculation.
        """

        required_columns = [
            "population",
            "median_household_income",
            "housing_units"
        ]

        missing = (
            set(required_columns) - set(self.df.columns)
        )

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )


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


    def _calculate_ratio(
        self,
        numerator: str,
        denominator: str,
        output: str
    ) -> None:
        """
        Calculate a ratio metric and store it in a DataFrame.

        Division by zero values are replaced with missing values
        to prevent invalid calculations.

        Args:
            numerator: Numerator column
            denominator: Denominator column
            output: Name of output column

        Returns:
            None. Adds a column to self.df.
        """

        self.df[output] = (
            self.df[numerator]
            .div(self.df[denominator].replace(0, pd.NA))
        )


    def _calculate_rank(
        self,
        column: str,
        output: str,
        ascending: bool = False
    ) -> None:
        """
        Rank counties by a metric.

        Args:
            column: Column to rank.
            output: Output rank column.
            ascending: Whether lower values receive better ranks.

        Returns:
            None. Adds a column to self.df.
        """

        self.df[output] = (
            self.df[column]
            .rank(
                ascending=ascending,
                method="dense"
            )
            .astype(int)
        )


    def _calculate_percentile(
        self,
        column: str,
        output: str
    ) -> None:
        """
        Calculate what percentile the county is in for a particular metric.

        Args:
            column: Column to calculate percentile for.
            output: Name of output column.

        Returns:
            None. Adds a column to self.df.
        """

        self.df[output] = (
            self.df[column]
            .rank(pct=True)
            * 100
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

        self._calculate_rank(
            "poverty_rate",
            "poverty_rank",
            ascending=True
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
            "population_25_plus",
            "percent_bachelors_plus"
        )

        self._calculate_percentage(
            "less_than_9th_grade",
            "population_25_plus",
            "percent_less_than_9th_grade"
        )

        self._calculate_rank(
            "percent_bachelors_plus",
            "education_rank",
            ascending=True
        )

        # self._calculate_percentage(
        #     "high_school_graduate",
        #     "population_25_plus",
        #     "percent_high_school"
        # )


    def _calculate_employment(self) -> None:
        """
        Calculate the unemployment rate.
        """
        self._calculate_percentage(
            "unemployed",
            "labor_force",
            "unemployment_rate"
        )

        self._calculate_rank(
            "unemployment_rate",
            "unemployment_rank",
            ascending=True
        )


    def _calculate_housing(self) -> None:
        """
        Calculate housing percentage metrics.

        Creates percentage values for:
            - home occupancy
            - home ownership

        Returns:
            None. Adds calculated columns to self.df.
        """
        self._calculate_percentage(
            "occupied_housing_units",
            "housing_units",
            "percent_of_homes_occupied"
        )

        self._calculate_percentage(
            "renter_occupied_units",
            "occupied_housing_units",
            "percent_of_occupied_homes_rented"
        )

        self._calculate_percentage(
            "owner_occupied_units",
            "occupied_housing_units",
            "homeownership_rate"
        )

        self._calculate_percentage(
            "vacant_housing_units",
            "housing_units",
            "vacancy_rate"
        )


    def _round_metrics(self) -> None:
        """
        Round calculated metrics.
        """

        percentage_columns = [
            col for col in self.df.columns
            if col.startswith("percent")
            or col.endswith("rate")
        ]

        self.df[percentage_columns] = (
            self.df[percentage_columns]
            .round(2)
        )


    def _organize_columns(self) -> None:
        """
        Arrange dataframe columns into logical groups.
        """

        id_columns = [
            "NAME",
            "GEOID",
            "state",
            "county"
        ]

        metric_columns = sorted(
            c for c in self.df.columns
            if c not in id_columns
        )

        self.df = self.df[
            id_columns + metric_columns
        ]


    def run(self) -> pd.DataFrame:
        """
        Execute the full analytics pipeline.

        Returns:
            DataFrame containing county metrics
        """

        self.load_data()
        self.calculate_metrics()

        return self.df


    def load_data(self) -> pd.DataFrame:
        """
        Retrieve Census datasets and merge them into one dataframe.

        The loaded datasets include demographic, economic,
        education, employment, housing, and county profile data.

        Returns:
            DataFrame containing merged county Census data.
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

        # Load the county boundaries
        boundary_loader = BoundaryLoader(
            boundary_path=BOUNDARY_FILE)

        boundaries = boundary_loader.load_texas_counties()

        self.df = self.df.merge(
            boundaries,
            on="GEOID",
            how="left"
        )

        return self.df


    def top_n(
        self,
        metric: str,
        n: int = 10,
        ascending: bool = False
    ) -> pd.DataFrame:
        """
        Return the top n counties based on the metric passed in.

        Args:
            metric: Metric to be compared.
            n: Top n counties.
            ascending: ascending behavior, True or False
        Returns:
            DataFrame sorted by metric
        """
        return (
            self.df
            .sort_values(
                metric,
                ascending=ascending
            )
            .head(n)
        )


    def save_data(
        self,
        path: str
    ) -> None:
        """
        Save processed analytics to a parquet file.

        Args:
            path: File location where the dataframe will be saved.

        Returns:
            None. Saves the dataframe as a parquet file.
        """
        self.df.to_parquet(path, index=False)


    def calculate_metrics(self) -> pd.DataFrame:
        """
        Calculate all derived county analytics metrics.

        Loads Census data if it has not already been loaded,
        the calculates metrics for demographics, economics,
        education, employment, and housing.

        Returns:
            DataFrame containing raw Census data and calculated metrics.
        """

        # Make sure the data is loaded
        if self.df is None:
            self.load_data()

        self._validate_dataframe()

        self._calculate_demographics()
        self._calculate_economics()
        self._calculate_education()
        self._calculate_employment()
        self._calculate_housing()

        self._calculate_rank(
            "median_household_income",
            "median_income_rank",
            ascending=True
        )

        self._calculate_rank(
            "population",
            "population_rank",
            ascending=True
        )

        self._calculate_rank(
            "median_household_income",
            "income_percentile",
            ascending=True
        )

        self._round_metrics()

        return self.df


    def get_county(
        self,
        county_name: str
    ) -> pd.DataFrame:
        """
        Returns metrics for a single county.

        Args:
            county_name: name of the county being returned

        Returns:
            DataFrame containing metrics for a single county
        """

        return self.df[
            self.df["NAME"] == county_name
        ]


    def highest_income_counties(
        self,
        n=10
    ) -> pd.DataFrame:
        """
        Sort counties by highest income.

        Args:
            n: top n counties
        Returns:
            DataFrame with the top n counties by highest income.
        """
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "median_household_income",
            n=n
        )


    def largest_counties(
        self,
        n=10
    ) -> pd.DataFrame:
        """
        Sort counties by largest population.

        Args:
            n: top n counties
        Returns:
            DataFrame with top n largest counties by population
        """
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "population",
            n
        )


    def highest_poverty_counties(
        self,
        n=10
    ) -> pd.DataFrame:
        """
        Sort counties based on highest poverty rate.

        Args:
            n: top n counties

        Returns:
            DataFrame with top n highest poverty rates by county.
        """
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "povery_rate",
            n
        )


    def highest_education_counties(
        self,
        n=10
    ):
        """
        Sort counties based on highest education rate.

        Args:
            n: top n counties

        Returns:
            DataFrame with top n highest education rates by county.
        """
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "percent_bachelors_plus",
            n
        )


    def highest_unemployment_counties(
        self,
        n=10
    ):
        """
        Sort counties based on highest unemployment rate.

        Args:
            n: top n counties

        Returns:
            DataFrame with top n highest unemployment rates by county.
        """
        if self.df is None:
            self.calculate_metrics()

        return self.top_n(
            "unemployment_rate",
            n
        )


