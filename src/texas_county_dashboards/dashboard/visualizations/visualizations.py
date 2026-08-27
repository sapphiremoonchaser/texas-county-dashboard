import geopandas as gpd
import plotly.express as px
from plotly.graph_objs import Figure


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


def create_income_comparison(
    county_name: str,
    county_income: float,
    texas_income: float
) -> Figure:
    """Create a bar chart comparing county income with Texas."""

    fig = px.bar(
        x=["County", "Texas"],
        y=[county_income, texas_income],
        title="Median Household Income",
        labels={
            "x": "",
            "y": "Income"
        },
        text=[
            f"${value:,.0f}"
            for value in [county_income, texas_income]
        ]
    )

    fig.update_yaxes(tickformat="$,.0f")

    return fig


def create_poverty_comparison(
    county_name: str,
    county_poverty: float,
    texas_poverty: float
) -> Figure:
    """Create a bar chart comparing county poverty with Texas."""

    fig = px.bar(
        x=["County", "Texas"],
        y=[county_poverty, texas_poverty],
        title="Poverty Rate",
        labels={
            "x": "",
            "y": "Poverty Rate"
        },
        text=[
            f"{value:.1f}%"
            for value in [county_poverty, texas_poverty]
        ]
    )

    fig.update_yaxes(ticksuffix="%")

    return fig


def create_unemployment_comparison(
    county_name: str,
    county_unemployment: float,
    texas_unemployment: float
) -> Figure:
    """Create a bar chart comparing county unemployment with Texas."""

    fig = px.bar(
        x=["County", "Texas"],
        y=[county_unemployment, texas_unemployment],
        title="Unemployment Rate",
        labels={
            "x": "",
            "y": "Unemployment Rate"
        },
        text=[
            f"{value:.1f}%"
            for value in [county_unemployment, texas_unemployment]
        ]
    )

    fig.update_yaxes(ticksuffix="%")

    return fig


def create_population_comparison_chart(comparison_df):
    fig = px.bar(
        comparison_df,
        x="County",
        y="Population",
        title="Population",
        text="Population",
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
    )

    fig.update_layout(
        yaxis_title="Population",
        xaxis_title=None,
    )

    return fig


def create_income_comparison_chart(comparison_df):
    fig = px.bar(
        comparison_df,
        x="County",
        y="Median Household Income",
        title="Median Household Income",
        text="Median Household Income",
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
    )

    fig.update_layout(
        yaxis_title="Median Household Income",
        xaxis_title=None,
    )

    return fig


def create_poverty_comparison_chart(comparison_df):
    fig = px.bar(
        comparison_df,
        x="County",
        y="Poverty Rate",
        title="Poverty Rate",
        text="Poverty Rate",
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
    )

    fig.update_layout(
        yaxis_title="Poverty Rate",
        xaxis_title=None,
    )

    return fig


def create_metric_ranking_chart(
    county_gdf: gpd.GeoDataFrame,
    metric: str,
    ascending: bool = False,
) -> Figure:
    """Create a bar chart ranking counties by the selected metric."""

    metric_columns = {
        "Median Income": "median_household_income",
        "Poverty Rate": "poverty_rate",
        "Population": "population",
        "Percent White": "percent_white",
    }

    column = metric_columns[metric]

    plot_df = (
        county_gdf[["NAME", column]]
        .dropna()
        .sort_values(column, ascending=ascending)
        .head(10)
    )

    fig = px.bar(
        plot_df,
        x=column,
        y="NAME",
        orientation="h",
        title=(
            f"Bottom 10 Counties by {metric}"
            if ascending
            else f"Top 10 Counties by {metric}"
        ),
    )

    fig.update_layout(
        xaxis_title=metric,
        yaxis_title=None,
    )

    return fig


def create_metric_boxplot(
    county_gdf: gpd.GeoDataFrame,
    metric: str,
) -> Figure:
    """Create a boxplot showing the distribution of the selected metric."""

    metric_columns = {
        "Median Income": "median_household_income",
        "Poverty Rate": "poverty_rate",
        "Population": "population",
        "Percent White": "percent_white",
    }

    column = metric_columns[metric]

    plot_df = county_gdf[["NAME", column]].dropna()

    fig = px.box(
        plot_df,
        x=column,
        points="all",
        hover_name="NAME",
        title=f"Distribution of {metric}",
        labels={
            column: metric,
            "NAME": "County",
        },
    )

    fig.update_layout(
        xaxis_title=metric,
        yaxis_title=None,
    )

    return fig