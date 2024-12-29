# src/main.py
from dataclasses import dataclass
from typing import NewType, Callable, Iterator, Dict, List, Tuple
from functools import partial, reduce, compose
from src.utils.logger import setup_logger


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Type definitions for better type safety
Rating = NewType('Rating', float)
Year = NewType('Year', int)
MovieCount = NewType('MovieCount', int)

logger = setup_logger(__name__, 'logs/main.log')

@dataclass(frozen=True)
class MovieData:
    """Immutable container for movie data"""
    df: pd.DataFrame

    @property
    def valid_ratings(self) -> pd.DataFrame:
        return self.df[
            (self.df['tomatometer_rating'].between(0, 100)) &
            (self.df['audience_rating'].between(0, 100))
            ]


@dataclass(frozen=True)
class PlotConfig:
    """Immutable configuration for plotting"""
    figure_size: Tuple[int, int]
    dpi: int
    style: Dict[str, any]


# Pure functions for data processing
def read_movie_data(file_path: Path) -> MovieData:
    """Pure function to read and validate movie data"""
    df = pd.read_csv(file_path)
    processed_df = process_raw_data(df)
    return MovieData(processed_df)


def process_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function for initial data processing"""
    return (df.pipe(convert_dates)
            .pipe(convert_numeric_columns)
            .pipe(filter_valid_data))


def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function to convert date columns"""
    return df.assign(
        release_year=pd.to_datetime(df['in_theaters_date'],
                                    errors='coerce').dt.year
    )


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function to convert numeric columns"""
    numeric_columns = ['tomatometer_rating', 'audience_rating',
                       'runtime_in_minutes']
    return df.assign(**{
        col: pd.to_numeric(df[col], errors='coerce')
        for col in numeric_columns
    })


def filter_valid_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pure function to filter valid data"""
    return df[
        df['runtime_in_minutes'].between(0, 300) &
        df['tomatometer_rating'].between(0, 100) &
        df['audience_rating'].between(0, 100) &
        df['release_year'].between(1900, 2024)
        ]


# Pure functions for visualization
def create_heatmap(data: MovieData, config: PlotConfig) -> plt.Figure:
    """Pure function to create heatmap"""
    valid_data = data.valid_ratings
    bins = np.linspace(0, 100, 11)

    heatmap_data = calculate_heatmap_data(valid_data, bins)
    return plot_heatmap(heatmap_data, config)


def calculate_heatmap_data(df: pd.DataFrame,
                           bins: np.ndarray) -> np.ndarray:
    """Pure function to calculate heatmap data"""
    return np.histogram2d(
        df['tomatometer_rating'],
        df['audience_rating'],
        bins=bins
    )[0]


# Kompozycja funkcji dla pipeline'ów przetwarzania
process_and_visualize = compose(
    partial(create_heatmap, config=default_config),
    read_movie_data
)


# Main execution with error handling through Either monad
def main() -> None:
    try:
        data_path = Path('data/Rotten Tomatoes Movies.csv')
        result = process_and_visualize(data_path)
        save_plots(result, Path('plots'))
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")


if __name__ == "__main__":
    main()