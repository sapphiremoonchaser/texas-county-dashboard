import pandas as pd
import pytest

from texas_county_dashboards.scripts.county_analytics import CountyAnalytics


class FakeCensusClient:
    """
    Create a fake census client so we don't have to hit the api for testing.
    """
    def county_profile(self):
        return pd.DataFrame({
            "state": ["48"],
            "county": ["001"],
            "NAME": ["Anderson County"],
            "GEOID": ["48001"],
            "population": [1000],
            "median_household_income": [50000],
            "housing_units": [500]
        })

    def education_profile(self):
        return pd.DataFrame({
            "state": ["48"],
            "county": ["001"],
            "NAME": ["Anderson County"],
            "GEOID": ["48001"],
            "bachelors": [100],
            "masters": [50],
            "professional": [10],
            "doctorate": [5],
            "population_25_plus": [500],
            "less_than_9th_grade": [50]
        })

    def employment_profile(self):
        return pd.DataFrame({
            "state": ["48"],
            "county": ["001"],
            "NAME": ["Anderson County"],
            "GEOID": ["48001"],
            "unemployed": [50],
            "labor_force": [500]
        })

    def demographics_profile(self):
        return pd.DataFrame({
            "state": ["48"],
            "county": ["001"],
            "NAME": ["Anderson County"],
            "GEOID": ["48001"],
            "female_population": [500],
            "male_population": [500],
            "white_population": [700],
            "black_population": [200],
            "asian_population": [50],
            "hispanic_population": [100],
            "american_indian_population": [10],
            "native_hawaiian_population": [5],
            "other_race_population": [20],
            "two_or_more_population": [15]
        })

    def economics_profile(self):
        return pd.DataFrame({
            "state": ["48"],
            "county": ["001"],
            "NAME": ["Anderson County"],
            "GEOID": ["48001"],
            "population_below_poverty": [100],
            "poverty_universe": [1000],
            "households_with_snap": [200]
        })

    def housing_profile(self):
        return pd.DataFrame({
            "state": ["48"],
            "county": ["001"],
            "NAME": ["Anderson County"],
            "GEOID": ["48001"],
            "occupied_housing_units": [450],
            "renter_occupied_units": [200],
            "owner_occupied_units": [250],
            "vacant_housing_units": [50]
        })


def test_county_analytics_initialization():
    """
    Checks the constructor.
    :return:
    """
    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    assert analytics.df is None
    assert analytics.county_profile is None


def test_merge_data():

    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    analytics.county_profile = analytics.census_client.county_profile()
    analytics.education_profile = analytics.census_client.education_profile()
    analytics.employment_profile = analytics.census_client.employment_profile()
    analytics.demographics_profile = analytics.census_client.demographics_profile()
    analytics.economics_profile = analytics.census_client.economics_profile()
    analytics.housing_profile = analytics.census_client.housing_profile()

    df = analytics._merge_data()

    assert len(df) == 1
    assert "population" in df.columns
    assert "bachelors" in df.columns
    assert "occupied_housing_units" in df.columns


def test_load_data_merges_profiles():
    """
    Verifies the following:
        - all profiles loaded
        - merge keys work
        - columns survive
    :return:
    """
    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    df = analytics.load_data()

    assert len(df) == 1

    assert "population" in df.columns
    assert "bachelors" in df.columns
    assert "unemployed" in df.columns


def test_calculate_percentage_handles_zero():

    analytics = CountyAnalytics(
        FakeCensusClient
    )

    analytics.df = pd.DataFrame({
        "numerator": [10],
        "denominator": [0]
    })

    analytics._calculate_percentage(
        "numerator",
        "denominator",
        "result"
    )

    assert pd.isna(
        analytics.df["result"].iloc[0]
    )


def test_calculate_percentage():
    """
    Tests percentage calculation.
    :return:
    """

    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    analytics.df = pd.DataFrame({
        "female_population": [500],
        "population": [1000]
    })

    analytics._calculate_percentage(
        "female_population",
        "population",
        "percent_female"
    )

    assert analytics.df["percent_female"].iloc[0] == 50


def test_calculated_metrics():
    """
    Test calculated metrics
    :return:
    """

    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    df = analytics.calculate_metrics()

    assert "percent_female" in df.columns
    assert "unemployment_rate" in df.columns
    assert "homeownership_rate" in df.columns


def test_calculated_demographics_metrics():
    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    df = analytics.calculate_metrics()

    assert df["percent_female"].iloc[0] == 50
    assert df["percent_male"].iloc[0] == 50
    assert df["percent_white"].iloc[0] == 70
    assert df["percent_black"].iloc[0] == 20
    assert df["percent_asian"].iloc[0] == 5
    assert df["percent_native_hawaiian"].iloc[0] == 0.5
    assert df["percent_other_race"].iloc[0] == 2
    assert df["percent_two_or_more"].iloc[0] == 1.5
    assert df["percent_hispanic"].iloc[0] == 10


def test_calculated_economic_metrics():

    analytics = CountyAnalytics(
        FakeCensusClient
    )

    df = analytics.calculate_metrics()

    assert df["poverty_rate"].iloc[0] == 10
    assert df["percent_with_snap"].iloc[0] == 20


def test_calculated_education_metrics():
    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    df = analytics.calculate_metrics()

    assert df["bachelors_plus"].iloc[0] == 165
    assert df["percent_bachelors_plus"].iloc[0] == 33
    assert df["percent_less_than_9th_grade"].iloc[0] == 10


def test_calculated_employment_metrics():
    analytics = CountyAnalytics(
        FakeCensusClient
    )

    df = analytics.calculate_metrics()

    assert df["unemployment_rate"].iloc[0] == 10


def test_calculated_housing_metrics():
    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    df = analytics.calculate_metrics()

    assert df["percent_of_homes_occupied"].iloc[0] == 90
    assert df["percent_of_occupied_homes_rented"].iloc[0] == pytest.approx(44.44, abs=0.01)
    assert df["homeownership_rate"].iloc[0] == pytest.approx(55.56, abs=0.01)
    assert df["vacancy_rate"].iloc[0] == 10


def test_highest_income_counties():

    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    analytics.df = pd.DataFrame({
        "NAME": [
            "A",
            "B",
            "C"
        ],
        "median_household_income": [
            50000,
            80000,
            30000
        ]
    })

    result = analytics.highest_income_counties(2)

    assert list(result["NAME"]) == [
        "B",
        "A"
    ]


def test_largest_counties():

    analytics = CountyAnalytics(
        FakeCensusClient()
    )

    analytics.df = pd.DataFrame({
        "NAME": [
            "Small",
            "Large"
        ],
        "population": [
            100,
            1000
        ]
    })

    result = analytics.largest_counties(1)

    assert result.iloc[0]["NAME"] == "Large"
