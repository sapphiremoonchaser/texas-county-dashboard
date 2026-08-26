import streamlit as st
from pathlib import Path

from texas_county_dashboards.scripts.boundary_loader import BoundaryLoader
from texas_county_dashboards.dashboard.visualizations.preparation import load_county_data
from texas_county_dashboards.dashboard.visualizations.visualizations import (
    create_county_map
)


df = load_county_data()

boundary_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "tl_2024_us_county.zip"
)

boundary_loader = BoundaryLoader(boundary_path)

boundary_gdf = boundary_loader.load_counties()

county_gdf = boundary_gdf.merge(
    df,
    on="GEOID",
    how="left"
)

st.write(type(boundary_gdf))
st.write(type(county_gdf))

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
        len(df)
    )

with col2:
    st.metric(
        "Average Median Income",
        f"${df['median_household_income'].mean():,.0f}"
    )

with col3:
    st.metric(
        "Average Poverty Rate",
        f"{df['poverty_rate'].mean():,.0f}%"
    )

with col4:
    st.metric(
        "Average Population",
        f"{df['population'].mean():,.0f}"
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
    county_gdf=df,
    metric=map_metric
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------
# County-Level Patterns
# -------------------------
st.subheader("County-Level Patterns")

col1, col2 = st.columns(2)

with col1:
    st.write("Median Income by County")
    # Chart goes here

with col2:
    st.write("Poverty Rate by County")
    # Chart goes here

# -------------------------
# County Highlights
# -------------------------
st.subheader("County Highlights")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Highest Median Income", "...")

with col2:
    st.metric("Lowest Poverty Rate", "...")

with col3:
    st.metric("Largest Population", "...")