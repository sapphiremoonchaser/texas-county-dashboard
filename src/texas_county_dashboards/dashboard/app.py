import streamlit as st
import pandas as pd
import geopandas as gpd

from texas_county_dashboards.dashboard.visualizations.preparation import (
    load_county_data,
    get_county_names,
    get_selected_county,
    create_county_comparison
)

from texas_county_dashboards.dashboard.visualizations.visualizations import (
    create_county_map,
    create_income_comparison,
    create_poverty_comparison,
    create_unemployment_comparison,
    create_population_comparison_chart,
    create_income_comparison_chart,
    create_poverty_comparison_chart,
    create_metric_ranking_chart,
    create_metric_boxplot
)


st.set_page_config(
    page_title="Texas County Analysis",
    page_icon="⭐",
    layout="wide"
)

# --------------------
# Load data
# --------------------

county_gdf: gpd.GeoDataFrame = load_county_data()

st.title("Texas County Analytics")

st.write("Explore demographic, economic, and population patterns across Texas "
         "counties.")

# --------------------
# Sidebar
# --------------------

st.sidebar.title("Texas")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "County vs. Texas",
        "County Comparison"
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

    # Ranking counties based on selected metric
    st.subheader(f"{map_metric} by County")

    col1, col2 = st.columns(2)

    with col1:
        fig = create_metric_ranking_chart(
            county_gdf=county_gdf,
            metric=map_metric,
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = create_metric_ranking_chart(
            county_gdf=county_gdf,
            metric=map_metric,
            ascending=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Metric Distribution
    st.subheader(f"{map_metric} Distribution")

    fig = create_metric_boxplot(
        county_gdf=county_gdf,
        metric=map_metric,
    )

    st.plotly_chart(fig, use_container_width=True)


if page == "County vs. Texas":
    st.subheader("County Explorer")

    # Create county selector
    county_names = st.selectbox(
        "Select a County",
        options=get_county_names(county_gdf)
    )

    selected_county = get_selected_county(
        county_gdf,
        county_names
    )

    # Ranking Table
    unemployment_rate = (
            selected_county['unemployed'] / selected_county['population']
    )

    # County benchmarks
    texas_population = county_gdf["population"].sum()
    texas_income = county_gdf["median_household_income"].median()
    texas_poverty = county_gdf["poverty_rate"].median()
    texas_unemployment = county_gdf["unemployment_rate"].median()

    # County actual values
    county_income = selected_county["median_household_income"]
    county_poverty = selected_county["poverty_rate"]
    county_unemployment = selected_county["unemployment_rate"]

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Population",
            f"{selected_county['population']:,.0f}",
            delta=(
                selected_county["population"]
                - texas_population
            )
        )

    with col2:
        st.metric(
            "Median Household Income",
            f"${selected_county['median_household_income']:,.0f}",
            delta=(
                    selected_county["median_household_income"]
                    - texas_income
            )
        )

    with col3:
        st.metric(
            "Poverty Rate",
            f"{selected_county['poverty_rate']:.1f}%",
            delta=(
                    selected_county["poverty_rate"]
                    - texas_poverty
            )
        )

    with col4:
        st.metric(
            "Unemployment Rate",
            f"{selected_county['unemployment_rate']:.1f}%",
            delta=(
                    selected_county["unemployment_rate"]
                    - texas_unemployment
            ),
            delta_color="inverse"
        )

    # County benchmarks
    texas_population = county_gdf["population"].sum()
    texas_income = county_gdf["median_household_income"].median()
    texas_poverty = county_gdf["poverty_rate"].median()
    texas_unemployment = county_gdf["unemployment_rate"].median()

    # Ranking the counties
    population_rank = (
        county_gdf["population"]
        .rank(method="min", ascending=False) # Largest population gets rank 1
        .loc[selected_county.name]
    )

    income_rank = (
        county_gdf["median_household_income"]
        .rank(method="min", ascending=False) # Largest income get rank 1
        .loc[selected_county.name]
    )

    poverty_rank = (
        county_gdf["poverty_rate"]
        .rank(method="min", ascending=False) # Largest poverty rate gets rank 1
        .loc[selected_county.name]
    )

    unemployment_rank = (
        county_gdf["unemployment_rate"]
        .rank(method="min", ascending=False) # Largest unemployment rate gets rank 1
        .loc[selected_county.name]
    )

    # Fill in the dataframe with the metrics and rankings
    comparison_df = pd.DataFrame({
        "Metric": [
            "Population",
            "Median Household Income",
            "Poverty Rate",
            "Unemployment Rate"
        ],
        county_names: [
            f"{selected_county['population']:,.0f}",
            f"${selected_county['median_household_income']:,.0f}",
            f"{selected_county['poverty_rate']:.1f}%",
            f"{selected_county['unemployment_rate']:.1f}%"
        ],
        "Texas": [
            f"{texas_population:,.0f}",
            f"${texas_income:,.0f}",
            f"{texas_poverty:.1f}%",
            f"{texas_unemployment:.1f}%"
        ],
        "Rank Among Texas Counties": [
            f"{population_rank:.0f}",
            f"{income_rank:.0f}",
            f"{poverty_rank:.0f}",
            f"{unemployment_rank:.0f}"
        ]
    })

    st.subheader("County vs. Texas")

    st.dataframe(
        comparison_df,
        hide_index=True,
        use_container_width=True
    )
    st.caption(
        "Rank is based on descending values, where 1 represents the highest value among Texas counties."
    )

    # Charts
    st.subheader("Economic Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        if county_names and county_income and texas_income:
            fig = create_income_comparison(
                county_names,
                county_income,
                texas_income
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if county_names and county_income and texas_income:
            fig = create_poverty_comparison(
                county_names,
                county_poverty,
                texas_poverty
            )

            st.plotly_chart(fig, use_container_width=True)

    with col3:
        if county_names and county_income and texas_income:
            fig = create_unemployment_comparison(
                county_names,
                county_unemployment,
                texas_unemployment
            )

            st.plotly_chart(fig, use_container_width=True)


if page == "County Comparison":
    st.title("County Comparison")

    # Select Counties
    county_names = get_county_names(county_gdf)

    col1, col2 = st.columns(2)

    with col1:
        selected_county_1 = st.selectbox(
            "Select County 1",
            county_names,
            index=county_names.index("Bastrop County, Texas"),
            key="comparison_county_1",
        )

        county_1 = county_gdf[
            county_gdf["NAME"] == selected_county_1
        ].iloc[0]

    with col2:
        selected_county_2 = st.selectbox(
            "Select County 2",
            county_names,
            key="comparison_county_2",
        )

        county_2 =county_gdf[
            county_gdf["NAME"] == selected_county_2
        ].iloc[0]

    comparison_df = pd.DataFrame({
        "Metric": [
            "Population",
            "Median Household Income",
            "Poverty Rate",
            "Unemployment Rate",
        ],
        selected_county_1: [
            f"{county_1['population']:,.0f}",
            f"${county_1['median_household_income']:,.0f}",
            f"{county_1['poverty_rate']:.1f}%",
            f"{county_1['unemployment_rate']:.1f}%",
        ],
        selected_county_2: [
            f"{county_2['population']:,.0f}",
            f"${county_2['median_household_income']:,.0f}",
            f"{county_2['poverty_rate']:.1f}%",
            f"{county_2['unemployment_rate']:.1f}%",
        ],
        "Difference": [
            f"{county_1['population'] - county_2['population']:+,.0f}",
            f"${county_1['median_household_income'] - county_2['median_household_income']:+,.0f}",
            f"{county_1['poverty_rate'] - county_2['poverty_rate']:+.1f}%",
            f"{county_1['unemployment_rate'] - county_2['unemployment_rate']:+.1f}%",
        ],
    })

    st.dataframe(
        comparison_df,
        hide_index=True,
        use_container_width=True,
    )

    # Compare economic profile
    st.subheader("Economic Profile")

    # Data for comparison charts
    population_comparison = create_county_comparison(
        county_1,
        county_2,
        selected_county_1,
        selected_county_2,
        "population"
    )

    income_comparison = create_county_comparison(
        county_1,
        county_2,
        selected_county_1,
        selected_county_2,
        "median_household_income"
    )

    poverty_comparison = create_county_comparison(
        county_1,
        county_2,
        selected_county_1,
        selected_county_2,
        "poverty_rate"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(
            create_population_comparison_chart(population_comparison),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            create_income_comparison_chart(income_comparison),
        )

    with col3:
        st.plotly_chart(
            create_poverty_comparison_chart(poverty_comparison)
        )

    # Demographic and population comparison
    st.subheader("Population and Demographics")

    minority_1 = (
        (county_1["population"] - county_1["white_population"])
        / county_1["population"]
    ) * 100

    minority_2 = (
        (county_2["population"] - county_2["white_population"])
        / county_2["population"]
    ) * 100

    demographics_df = pd.DataFrame({
        "Metric": [
            "Population",
            "Median Age",
            "Minority %",
        ],
        selected_county_1: [
            f"{county_1['population']:,.0f}",
            f"{county_1['median_age']:.1f}",
            f"{minority_1:.1f}%",
        ],
        selected_county_2: [
            f"{county_2['population']:,.0f}",
            f"{county_2['median_age']:.1f}",
            f"{minority_2:.1f}%",
        ],
    })

    st.dataframe(
        demographics_df,
        hide_index=True,
        use_container_width=True,
    )

