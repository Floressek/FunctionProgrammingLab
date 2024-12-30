from typing import List, Tuple, Dict, Any, Union, NewType
from dataclasses import dataclass
import pandas as pd
import numpy as np
from pathlib import Path
from .logger import setup_logger
from .config import ProjectConfig

logger = setup_logger('utils', ProjectConfig.get_log_file('types'))

# Alias for common types
Rating = NewType('Rating', float)
Year = NewType('Year', int)
MovieCount = NewType('MovieCount', int)


@dataclass(frozen=True)
class MovieData:
    """Dataclass for movie data. - > immutable!"""  # less error-prone.
    df: pd.DataFrame

    @property
    def valid_ratings(self) -> pd.DataFrame:
        """Return only rows with valid ratings."""
        filtered_df = self.df[
            (self.df['tomatometer_rating'].between(0, 100) &
             self.df['audience_rating'].between(0, 100))
        ]
        logger.info(f'Filtered {len(filtered_df)} rows with valid ratings.')
        return filtered_df

    @property
    def valid_runtime(self) -> pd.DataFrame:
        """Return only rows with valid runtime."""
        filtered_df = self.df[
            self.df['runtime_in_minutes'].between(0, 280)
        ]
        logger.info(f'Filtered {len(filtered_df)} rows with valid runtime.')
        return filtered_df

@dataclass(frozen=True)
class PlotConfig:
    """Dataclass for plot configuration."""
    figure_size: Tuple[int, int] = (15, 10) # default value
    font_size: int = 10
    title_size: int = 14
    label_size: int = 12
    tick_size: int = 10
    dpi: int = 300
    style: Dict[str, Any] = None

    def __post_init__(self): # called after __init__
        if self.style is None:
            object.__setattr__(self, 'style', { # object.__setattr__ set the attribute bc it's frozen
                'figure.figsize': self.figure_size,
                'font.size': self.font_size,
                'axes.titlesize': self.title_size,
                'axes.labelsize': self.label_size,
                'xtick.labelsize': self.tick_size,
                'ytick.labelsize': self.tick_size
            })
        logger.debug('Plot configuration initialized.')
