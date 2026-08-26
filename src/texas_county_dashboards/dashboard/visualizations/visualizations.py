import pandas as pd
import geopandas as gpd
import plotly.express as px
from plotly.graph_objs import Figure
from prompt_toolkit.layout import margins


def create_county_map(
    county_gdf: gpd.GeoDataFrame,
    metric: str
) -> Figure:
    """Create a choropleth map of Texas counties."""

    metric_columns = {
        "Median Income": "median_household_income",
        "Poverty Rate": "poverty_rate",
        "Population": "population",
        "Percent White": "percent_white"
    }

    column = metric_columns[metric]

    geojson = county_gdf.__geo_interface__

    fig = px.choropleth(
        county_gdf,
        geojson=geojson,
        locations='GEOID',
        featureidkey='properties.GEOID',
        color=column,
        hover_name="NAME",
        color_continuous_scale="Inferno"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


def create_top_income_chart(
    county_gdf: gpd.GeoDataFrame
) -> Figure:
    top_income = (
        county_gdf[[
            "NAME",
            "median_household_income",
        ]]
        .dropna()
        .nlargest(10, "median_household_income")
        .sort_values("median_household_income")
    )

    max_income = top_income["median_household_income"].max()

    fig = px.bar(
        top_income,
        x="median_household_income",
        y="NAME",
        orientation="h",
        title="Top 10 Counties by Median Income",
        labels={
            "median_household_income": "Median Household Income",
            "NAME": "County"
        },
        text="median_household_income"
    )

    fig.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )

    fig.update_xaxes(
        range=[0, max_income * 1.15]
    )

    return fig


def create_top_poverty_chart(
    county_gdf
) -> Figure:
    top_poverty = (
        county_gdf[["NAME", "poverty_rate"]]
        .dropna()
        .nlargest(10, "poverty_rate")
        .sort_values("poverty_rate")
    )

    max_poverty = top_poverty["poverty_rate"].max()

    fig = px.bar(
        top_poverty,
        x="poverty_rate",
        y="NAME",
        orientation="h",
        title="Top 10 Counties by Poverty Rate",
        labels={
            "poverty_rate": "Poverty Rate",
            "NAME": "County"
        },
        text="poverty_rate"
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_xaxes(
        range=[0, max_poverty * 1.15]
    )

    return fig


def create_income_boxplot(
    county_gdf: gpd.GeoDataFrame
) -> Figure:
    """Create a boxplot showing the distribution of median household income."""
    income_data = county_gdf["median_household_income"].dropna()

    fig = px.box(
        county_gdf,
        x="median_household_income",
        points="all",
        title="Distribution of Median Household Income",
        labels={
            "median_household_income": "Median Household Income"
        },
        hover_name="NAME"
    )

    fig.update_traces(
        hovertemplate=(
            "%{hovertext}<br>"
            "$%{x:,.0f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        yaxis_tickprefix="$",
        yaxis_tickformat=","
    )

    return fig
