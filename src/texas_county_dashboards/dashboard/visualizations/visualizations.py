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
        "Median Income": "median_income",
        "Poverty Rate": "poverty_rate",
        "Population": "population",
        "Percent White": "percent_white"
    }

    column = metric_columns[metric]

    fig = px.choropleth(
        county_gdf,
        geojson=county_gdf.geometry,
        locations=county_gdf.index,
        color=column,
        hover_name="county_name",
        color_continuous_scale="Viridis"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig

