from functools import partial, reduce
from typing import Callable, List, Dict, Any
import pandas as pd
from pathlib import Path

from src.utils.types import MovieData
from src.utils.logger import (setup_logger)
from src.utils.config import ProjectConfig

logger = setup_logger('data_analysis', ProjectConfig.get_log_file('data_processing'))


class DataProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass


def read_movie_data(file_path: Path) -> MovieData:
    """Read and validate data from file -> after processed"""
    try:
        logger.info("Data processing module initialized")  # Test logging
        logger.info(f'Reading movie data from {file_path}.')
        df = pd.read_csv(file_path)
        processed_data = process_raw_data(df)
        return MovieData(df=processed_data)
    except Exception as e:
        logger.error(f'Error reading movie data: {str(e)}')
        raise DataProcessingError(f'Error reading movie data: {str(e)}')


def process_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process raw data."""
    try:
        processing_functions: List[Callable[[pd.DataFrame], pd.DataFrame]] = [
            # list of functions to apply to the data in order, first dataFrame is the input, second is the output
            _convert_dates,
            _convert_numeric_columns,
            _filter_valid_data,
            _clean_genres
        ]
        return reduce(lambda data, func: func(data), processing_functions,
                      df)  # 3 args: function(lambda), iterable, initial value
    except Exception as e:
        logger.error(f'Error processing pipline failed: {str(e)}')
        raise DataProcessingError(f'Processing pipline error: {str(e)}')


def _convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert dates"""
    try:
        return df.assign(
            release_year=pd.to_datetime(
                df['in_theaters_date'], errors='coerce'  # if error, return NaT
            ).dt.year  # extract year
        )
    except Exception as e:
        logger.error(f'Data conversion failed: {str(e)}')
        raise DataProcessingError(f'Data conversion error: {str(e)}')


def _convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert numeric columns."""
    try:
        numeric_columns = {
            'tomatometer_rating': 'float64',
            'audience_rating': 'float64',
            'runtime_in_minutes': 'float64',
        }

        conversion_results = {
            col: pd.to_numeric(df[col], errors='coerce')  # if error, return NaN
            for col in numeric_columns.keys()  # for each column in the dict
        }

        return df.assign(
            **conversion_results)  # the double asterisk unpacks the dictionary: example: {'a': 1, 'b': 2} -> a=1, b=2

    except Exception as e:
        logger.error(f'Error converting numeric columns: {str(e)}')
        raise DataProcessingError(f'Error converting numeric columns: {str(e)}')


def _filter_valid_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out rows with invalid data."""
    try:
        conditions = [
            df['release_year'].between(1900, 2024),
            df['tomatometer_rating'].between(0, 100),
            df['audience_rating'].between(0, 100),
            df['runtime_in_minutes'].between(0, 280),
        ]

        return df[reduce(lambda x, y: x & y, conditions)]  # all conditions must be true
    except Exception as e:
        logger.error(f'Error filtering data: {str(e)}')
        raise DataProcessingError(f'Error filtering data: {str(e)}')


def _clean_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Clean genres column."""
    try:
        return df.assign(
            genre=df['genre'].fillna('Unknown')  # fill NaN with 'Unknown'
        )

    except Exception as e:
        logger.error(f'Error cleaning genres: {str(e)}')
        raise DataProcessingError(f'Error cleaning genres: {str(e)}')
