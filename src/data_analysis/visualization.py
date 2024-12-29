from functools import reduce
from typing import Tuple, List, Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from matplotlib.pyplot import figure

from src.utils.types import MovieData, PlotConfig
from src.utils.logger import setup_logger

logger = setup_logger(name='data_analysis', log_file='logs/visualization.log')


class VisualizationError(Exception):
    """Custom exception for visualization errors."""
    pass


def _setup_plot_style(config: PlotConfig) -> None:
    """Set plot style."""
    try:
        # plt.style.use('seaborn-poster') # throws error TODO find why
        plt.rcParams.update(config.style)
    except Exception as e:
        logger.error(f'Failed while setting plot style: {str(e)}')
        raise VisualizationError(f'Error setting plot style: {str(e)}')


def _calculate_heatmap_data(df: pd.DataFrame) -> np.ndarray:
    """Calculate heatmap data."""
    try:
        heatmap_data = np.zeros((10, 10))  # 10x10 matrix bc 0-10 to 90-100 ranges

        def __update_heatmap_data(acc: np.ndarray, row: pd.Series) -> np.ndarray:  # helper function
            """Update heatmap data."""
            # Binns data into 10 bins then, helps with OOB but not necessary cause we already filtered
            x_bin = min(int(row.tomatometer_rating // 10), 9)
            y_bin = min(int(row.audience_rating // 10), 9)
            acc[9 - y_bin, x_bin] += 1  # Lecimy od gory do dolu, bo od najwiekszej do najm. oceny i przesuwamy sie
            return acc

        return reduce(__update_heatmap_data, df.itertuples(),
                      heatmap_data)  # TODO expects iterable, not itertuples check
    except Exception as e:
        logger.error(f'Failed calculating heatmap data: {str(e)}')
        raise VisualizationError(f'Error calculating heatmap data: {str(e)}')


def create_heatmap(data: MovieData, config: PlotConfig) -> plt.Figure:
    """Create heatmap."""
    try:
        _setup_plot_style(config)
        fig = plt.figure(figsize=config.figure_size, dpi=config.dpi)

        valid_data = data.valid_ratings
        heatmap_data = _calculate_heatmap_data(valid_data)

        sns.heatmap(
            heatmap_data,
            cmap='YlGnBu',
            annot=True,
            fmt='g',
            xticklabels=[f'{i}-{i+10}' for i in range(0, 100, 10)],
            # range(0, 100, 10) -> 0, 10, 20, 30, 40, 50, 60, 70, 80, 90
            yticklabels=[f'{i}-{i+10}' for i in range(90, -1, -10)],
            # range(90, -10, -10) -> 90, 80, 70, 60, 50, 40, 30, 20, 10, 0
        )

        plt.title(f'Critics vs Audience Ratings\n(Total: {len(valid_data):,} movies)')
        plt.xlabel('Critics Rating (%)')
        plt.ylabel('Audience Rating (%)')

        return fig
    except Exception as e:
        logger.error(f'Failed creating heatmap: {str(e)}')
        raise VisualizationError(f'Error creating heatmap: {str(e)}')


def plot_genre_bars(genre_stats: pd.DataFrame) -> plt.Figure:
    """Plot genre bars."""
    try:
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

        def _create_bar_data(col: str, offset: float, color: str) -> None:
            """Create bar data."""
            positions = np.arange(len(genre_stats.index)) + offset
            heights = genre_stats[(col, 'mean')].values  # takes the mean values
            errors = genre_stats[(col, 'std')].values / 2  # shows error both sides

            ax.bar(positions, heights, 0.35, yerr=errors, color=color)

        list(map(
            lambda params: _create_bar_data(*params),  # unpacks the tuple
            # list of tuples as args for the lambda
            [
                ('tomatometer_rating', -0.2, 'lightblue'),
                ('audience_rating', 0.2, 'orange')
            ]
        ))

        return fig
    except Exception as e:
        logger.error(f'Failed creating genre bars: {str(e)}')
        raise VisualizationError(f'Error creating genre bars: {str(e)}')


def save_plot(fig: plt.Figure, name: str, output_dir: Path, config: PlotConfig) -> None:
    """Save plot."""
    try:
        output_path = output_dir / f'movie_analysis_{name}.png'
        fig.savefig(output_path, dpi=config.dpi, bbox_inches='tight')
        plt.close(fig)  # close the figure to free up memory
        logger.info(f'Plot saved successfully to {output_path}.')
    except Exception as e:
        logger.error(f'Failed saving plot: {str(e)}')
        raise VisualizationError(f'Error saving plot: {str(e)}')

# TODO PRZEROBIC STAD NA NOWO

def create_genre_comparison(data: MovieData, config: PlotConfig) -> plt.Figure:
    """Create genre comparison visualization"""
    _setup_plot_style(config)
    fig, ax = plt.subplots(figsize=config.figure_size)

    genre_stats = (data.df.groupby('genre')
                   .agg({
        'tomatometer_rating': ['mean', 'count', 'std'],
        'audience_rating': ['mean', 'count', 'std']
    })
                   .pipe(lambda x: x[x[('tomatometer_rating', 'count')] >= 10])
                   .nlargest(10, ('tomatometer_rating', 'mean')))

    x = np.arange(len(genre_stats.index))

    def plot_rating_bars(rating_type: str, offset: float, color: str) -> None:
        col = 'tomatometer_rating' if rating_type == 'Critics' else 'audience_rating'
        ax.bar(
            x + offset,
            genre_stats[(col, 'mean')],
            0.35,
            yerr=genre_stats[(col, 'std')] / 2,
            label=rating_type,
            color=color
        )

    list(map(
        lambda params: plot_rating_bars(*params),
        [('Critics', -0.2, 'lightblue'), ('Audience', 0.2, 'lightgreen')]
    ))

    ax.set_ylabel('Average Rating (%)')
    ax.set_title('Top 10 Genres by Rating')
    ax.set_xticks(x)
    ax.set_xticklabels(genre_stats.index, rotation=45, ha='right')
    ax.legend()

    return fig


def create_yearly_trends(data: MovieData, config: PlotConfig) -> plt.Figure:
    """Create yearly trends visualization"""
    _setup_plot_style(config)
    fig = plt.figure(figsize=config.figure_size)

    yearly_stats = (data.df.groupby('release_year')
                    .agg({
        'tomatometer_rating': ['mean', 'std', 'count'],
        'audience_rating': ['mean', 'std', 'count']
    }).pipe(lambda x: x[x[('tomatometer_rating', 'count')] >= 5]))

    years = yearly_stats.index.values

    def plot_trend(rating_type: str, color: str, label: str) -> None:
        mean = yearly_stats[(rating_type, 'mean')].values
        std = yearly_stats[(rating_type, 'std')].values
        count = yearly_stats[(rating_type, 'count')].values
        ci = 1.96 * std / np.sqrt(count)

        plt.plot(years, mean, color=color, label=label, linewidth=2)
        plt.fill_between(years, mean - ci, mean + ci, color=color, alpha=0.2)
        plt.scatter(years, mean, color=color, alpha=0.5,
                    s=count / count.max() * 100)  # Zmniejszony rozmiar punktów

    list(map(
        lambda params: plot_trend(*params),
        [('tomatometer_rating', 'blue', 'Critics'),
         ('audience_rating', 'green', 'Audience')]
    ))

    plt.xlabel('Year')
    plt.ylabel('Average Rating (%)')
    plt.title('Rating Trends Over Time (with 95% CI)')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Dodanie marginesu dla lepszej czytelności
    plt.margins(x=0.05, y=0.2)
    return fig

def create_runtime_analysis(data: MovieData, config: PlotConfig) -> plt.Figure:
    """Create runtime analysis visualization"""
    _setup_plot_style(config)
    fig = plt.figure(figsize=(15, 10))

    valid_data = data.valid_runtime
    runtime_bins = np.linspace(30, 240, 8)
    rating_bins = np.linspace(0, 100, 21)

    # First subplot - heatmap
    plt.subplot(211)
    hist_data = np.histogram2d(
        valid_data['runtime_in_minutes'],
        valid_data['tomatometer_rating'],
        bins=(runtime_bins, rating_bins)
    )[0]

    # Create custom normalization for better visualization of distribution
    from matplotlib.colors import LogNorm

    # Use logarithmic normalization to better show differences in smaller values
    norm = LogNorm(vmin=1, vmax=np.max(hist_data))

    im = plt.imshow(hist_data.T,
                    aspect='auto',
                    origin='lower',
                    cmap='YlOrRd',  # Yellow-Orange-Red colormap
                    norm=norm,
                    extent=[runtime_bins[0], runtime_bins[-1], rating_bins[0], rating_bins[-1]])

    # Create custom colorbar with more detailed scale
    cbar = plt.colorbar(im)
    cbar.set_label('Number of Movies', size=10)

    # Set custom tick locations for more detailed scale
    # Generate logarithmically spaced ticks
    tick_locations = np.logspace(0, np.log10(np.max(hist_data)), 10)
    cbar.set_ticks(tick_locations)
    # Round tick labels to whole numbers
    cbar.set_ticklabels([f'{int(x)}' for x in tick_locations])

    plt.xlabel('Runtime (minutes)')
    plt.ylabel('Critics Rating (%)')
    plt.title('Movie Distribution by Runtime and Critics Rating')
    plt.yticks(np.linspace(0, 100, 11))
    plt.xticks(runtime_bins, [f'{int(x)}' for x in runtime_bins], rotation=45)

    # Second subplot - boxplots
    plt.subplot(212)

    # Create box plot positions
    positions = np.arange(len(runtime_bins) - 1)
    width = 0.35

    # Group data by runtime ranges
    runtime_groups = valid_data.groupby(pd.cut(valid_data['runtime_in_minutes'], runtime_bins))

    # Critics ratings boxplot
    bp1 = plt.boxplot([group['tomatometer_rating'].values for name, group in runtime_groups],
                      positions=positions - width / 2,
                      widths=width,
                      patch_artist=True,
                      boxprops=dict(facecolor='skyblue', color='blue'),
                      medianprops=dict(color='darkblue'),
                      flierprops=dict(marker='o', markerfacecolor='skyblue'),
                      labels=[''] * (len(runtime_bins) - 1))

    # Audience ratings boxplot
    bp2 = plt.boxplot([group['audience_rating'].values for name, group in runtime_groups],
                      positions=positions + width / 2,
                      widths=width,
                      patch_artist=True,
                      boxprops=dict(facecolor='orange', color='darkgoldenrod'),
                      medianprops=dict(color='darkorange'),
                      flierprops=dict(marker='o', markerfacecolor='orange'),
                      labels=[''] * (len(runtime_bins) - 1))

    # Set x-ticks in the middle of the paired boxes
    plt.xticks(positions, [f'({int(runtime_bins[i])}, {int(runtime_bins[i + 1])}]'
                           for i in range(len(runtime_bins) - 1)], rotation=45)

    # Add legend
    plt.legend([bp1["boxes"][0], bp2["boxes"][0]], ['Critics Rating', 'Audience Rating'],
               loc='upper right')

    plt.xlabel('Runtime Range (minutes)')
    plt.ylabel('Rating (%)')
    plt.title('Ratings Distribution by Runtime Range')
    plt.grid(True, alpha=0.3)

    # Adjust layout
    plt.tight_layout()

    return fig
