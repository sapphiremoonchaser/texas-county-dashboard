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
        self.emplete_profile = None
        self.df = None


    # ToDo: load_data()


    # ToDo: _merge_data


    # ToDo: calculate_metrics()

    # ToDo: highest_income_counties()

    # ToDo: largest_counties()

    pass