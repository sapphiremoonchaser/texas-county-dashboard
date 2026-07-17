from os.path import exists
from pathlib import Path
import pandas as pd
import requests
from numpy.ma.core import masked
from setuptools.command.egg_info import overwrite_arg

from notebooks.data_exploration.census_api_exploration import response


class CensusVariables:
    """Download and search Census variable metadata."""

    def __init__(
        self,
        year: int = 2024, # Set the census year
        dataset: str = "acs/acs5", # Set the census catalog
        cache_dir: str = "data/metadata" # Where to store it
    ):
        # Save the variables that were passed in
        self.year = year
        self.dataset = dataset
        self.cache_dir = Path(cache_dir)

        # Create the folder
        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True # If the folder already exists don't throw an error
        )

        # Set the url
        self.url = (
            f"https://api.census.gov/data/{year}/{dataset}/variables.json"
        )

        # Take out / from filename and replace with _
        # Create the csv file
        self.cache_file = (
            self.cache_dir /
            f"{dataset.replaca('/', '_')}_{year}_variables.csv"
        )

        # Create the dataframe
        self.df =None


    def download(
            self,
            overwrite=False
    ):
        """Download variable metadata from the Census API"""
        # If the csv cache file exists and the user did not request an overwrite
        # Create the dataframe from the csv file
        if self.cache_file.exists() and not overwrite:
            self.df = pd.read_csv(self.cache_file)
            return self.df

        # Go to this url and download it
        response = requests.get(
            self.url,
            timeout=30
        )

        # Check for errors
        response.raise_for_status()

        # Convert into JSON
        variables = response.json()["variables"]

        # Save the json text as a dataframe
        df = (
            pd.DataFrame
            .from_dict(variables, orient="index")
            .reset_index(names="variable")
        )

        # Gives you a second way to access the variable
        # (along with the returned variable)
        self.df = df

        return df


    def search(
        self,
        keyword
    ):
        """Search every text column for a keyword."""
        # If there's no dataframe use download() function to get the census variable df
        if self.df is None:
            self.download()

        # Lowercase all keywords
        keyword = keyword.lower()

        # Create a boolean mask that tells us which rows contain keywords in any column
        mask = (
            self.df.fillna("") # fill na with empty string
            .astype(str) # Read all columns as strings
            .apply( # get the columns that have the keywords
                lambda col: col.str.lower().str.contains(keyword)
            )
            .any(axis=1) # Look across each row
        )

        return (
            self.df.loc[mask] # Keep only the rows where the mask is True
            .sort_values("variable")
            .reset_index(drop=True)
        )


    def table(
        self,
        table_code: str
    ):
        """Return all variables belonging to a table.

        Parameters:
            table_code (string): the table the user wants to retrive variables for.
        """
        # Make sure data is loaded
        if self.df is None:
            self.download()

        table_code = table_code.upper()

        return(
            self.df[ # Filter by variable column
                self.df["variable"].str.startswith(table_code)
            ]
            .sort_values("variable")
            .reset_index(drop=True)
        )


    def concepts(self):
        """
        List available concepts.

        Returns:
            DataFrame of unique Census concepts in the metadata
        """

        # Make sure the data is loaded
        if self.df is None:
            self.download()

        return (
            self.df["concept"]
            .dropna()
            .sort_values()
            .unique()
        )




