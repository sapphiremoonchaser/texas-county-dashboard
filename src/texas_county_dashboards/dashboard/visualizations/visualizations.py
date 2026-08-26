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
):
    top_income = (
        county_gdf[[
            "county_name",
            "median_household_income",
        ]]
        .dropna()
        .nlargest(10, "median_household_income")
        .sort_values("median_household_income")
    )

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

    return fig
