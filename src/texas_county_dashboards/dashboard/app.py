import streamlit as st

from texas_county_dashboards.dashboard.visualizations.preparation import load_county_data
from texas_county_dashboards.dashboard.visualizations.visualizations import (
    create_county_map,
    create_top_income_chart,
    create_top_poverty_chart,
    create_income_boxplot
)


st.set_page_config(
    page_title="Lana Del Rey Lyric Analysis",
    page_icon="⭐",
    layout="wide"
)

# --------------------
# Load data
# --------------------

county_gdf = load_county_data()

st.set_page_config(
    page_title="Texas County Analytics",
    layout="wide"
)

st.title("Texas County Analytics")

st.write("Explore demographic, economic, and population patterns across Texas "
         "counties.")

# --------------------
# Sidebar
# --------------------

st.sidebar.title("Texas County Analytics")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "County Explorer",
        "County Comparison",
        "Demographics Explorer"
    ]
)

# -------------------------
# Page Content
# -------------------------

if page == "Overview":
    st.subheader("Overview")

    # KPI Cards
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

   # County Map
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


    # Horizontal Bar Graphs
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

    # Median Household Income Distribution
    st.subheader("Median Houshold Income Distribution")

    fig = create_income_boxplot(county_gdf)
    st.plotly_chart(fig, use_container_width=True)


if page == "County Explorer":
    st.subheader("County Explorer")

    # Create county selector
    county_name = st.selectbox(
        "Select a County",
        options=sorted(county_gdf["NAME"].dropna().unique())
    )

    selected_county = county_gdf[
        county_gdf["NAME"] == county_name
    ].iloc[0]

    # KPI Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Population",
            f"{selected_county['population']:,.0f}"
        )

    with col2:
        st.metric(
            "Average Median Income",
            f"${selected_county['median_household_income'].mean():,.0f}"
        )

    with col3:
        st.metric(
            "Average Poverty Rate",
            f"{selected_county['poverty_rate'].mean():,.0f}%"
        )

    # Percentile Rankings
    st.subheader("Ranking Against Other Counties")

    population_percentile = (
        county_gdf["population"] <= selected_county["population"]
    ).mean() * 100

    income_percentile = (
        county_gdf['median_household_income'] <= selected_county["median_household_income"]
    ).mean() * 100

    poverty_rate = selected_county["poverty_rate"]

    poverty_rate_percentile = (
       county_gdf["poverty_rate"] <= poverty_rate
    ).mean() * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Population Percentile",
            f"{population_percentile:,.0f}th"
        )

    with col2:
        st.metric(
            "Income Percentile",
            f"{income_percentile:,.0f}th"
        )

    with col3:
        st.metric(
            "Poverty Rate Percentile",
            f"{poverty_rate_percentile:.0f}th"
        )



if page == "County Comparison":
    pass

if page == "Demographics Explorer":
    pass
