import streamlit as st
from pathlib import Path

from texas_county_dashboards.scripts.boundary_loader import BoundaryLoader
from texas_county_dashboards.dashboard.visualizations.preparation import load_county_data
from texas_county_dashboards.dashboard.visualizations.visualizations import (
    create_county_map,
    create_top_income_chart,
    create_top_poverty_chart,
    create_income_boxplot
)


county_gdf = load_county_data()

st.set_page_config(
    page_title="Texas County Analytics",
    layout="wide"
)

st.title("Texas County Analytics")

st.write("Explore demographic, economic, and population patterns across Texas "
         "counties.")

# -------------------------
# KPI Cards
# -------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Counties",
        len(county_gdf)
    )

with col2:
    st.metric(
        "Average Median Income",
        f"${county_gdf['median_household_income'].mean():,.0f}"
    )

with col3:
    st.metric(
        "Average Poverty Rate",
        f"{county_gdf['poverty_rate'].mean():,.0f}%"
    )

with col4:
    st.metric(
        "Average Population",
        f"{county_gdf['population'].mean():,.0f}"
    )

# -------------------------
# County Map
# -------------------------
st.subheader("Texas County Map")

map_metric = st.selectbox(
    "Select metric",
    [
        "Median Income",
        "Poverty Rate",
        "Population",
        "Percent White"
    ]
)

fig = create_county_map(
    county_gdf=county_gdf,
    metric=map_metric
)
st.plotly_chart(fig, use_container_width=True)


# -------------------------
# County-Level Patterns
# -------------------------
st.subheader("County-Level Patterns")

col1, col2 = st.columns(2)

with col1:
    st.write("Median Income by County")

    fig = create_top_income_chart(county_gdf)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("Poverty Rate by County")

    fig = create_top_poverty_chart(county_gdf)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Median Household Income Distribution
# -------------------------
st.subheader("Median Houshold Income Distribution")

fig = create_income_boxplot(county_gdf)
st.plotly_chart(fig, use_container_width=True)