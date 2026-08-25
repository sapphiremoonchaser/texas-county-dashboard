import streamlit as st
import os

from dotenv import load_dotenv

from texas_county_dashboards.scripts.county_analytics import CountyAnalytics
from texas_county_dashboards.scripts.census_client import CensusClient


st.set_page_config(
    page_title="Texas County Analytics",
    layout="wide"
)

st.title("Texas County Analytics")

st.write("Explore demographic, economic, and population patterns across Texas "
         "counties.")

load_dotenv()

api_key = os.getenv("CENSUS_API_KEY")

census_client = CensusClient(
    api_key=api_key
)

analytics = CountyAnalytics(census_client)

df = analytics.run()

# # KPI cards
# col1, col2, col3, col4 = st.columns(4)
#
# with col1:
#     st.metric(
#         "Total Counties",
#         len(df)
#     )
#
# with col2:
#     st.metric(
#         "Average Median Income",
#         f"${df['median_household_income'].mean():.1%}"
#     )