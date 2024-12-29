# src/main.py
from pathlib import Path
from typing import List, Callable
from functools import partial
from utils.logger import setup_logger

from utils.types import MovieData, PlotConfig
from src.data_analysis.data_processing import read_movie_data
from src.data_analysis.visualization import (
    create_heatmap, create_genre_comparison,
    create_yearly_trends, create_runtime_analysis,
    save_plot
)

import warnings

warnings.filterwarnings("ignore")

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# Skonfiguruj główny logger
logger = setup_logger(__name__, 'logs/main.log')


def create_plot_functions(config: PlotConfig) -> List[Callable[[MovieData], None]]:
    """Create list of plot generation functions with config"""
    plot_configs = [
        ('heatmap', create_heatmap),
        ('genres', create_genre_comparison),
        ('trends', create_yearly_trends),
        ('runtime', create_runtime_analysis)
    ]

    return [
        partial(plot_func, config=config)
        for name, plot_func in plot_configs
    ]


def process_and_visualize(
        data_path: Path,
        output_dir: Path,
        config: PlotConfig
) -> None:
    """Main processing pipeline"""
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read and process data
        logger.info("Reading and processing data...")
        movie_data = read_movie_data(data_path)

        # Generate and save all plots
        logger.info("Generating visualizations...")
        plot_functions = create_plot_functions(config)

        plot_names = {
            'create_heatmap': 'heatmap',
            'create_genre_comparison': 'genres',
            'create_yearly_trends': 'trends',
            'create_runtime_analysis': 'runtime'
        }

        for plot_func in plot_functions:
            # Get the original function name from the partial object
            original_func_name = plot_func.func.__name__
            plot_name = plot_names.get(original_func_name, original_func_name)

            try:
                fig = plot_func(movie_data)
                save_plot(fig, plot_name, output_dir, config)
                logger.info(f"Generated {plot_name} plot")
            except Exception as e:
                logger.error(f"Failed to generate {plot_name}: {str(e)}")

        logger.info("Visualization complete!")

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise


def main():
    """Entry point"""
    config = PlotConfig()
    data_path = Path(r'C:\Users\szyme\PycharmProjects\FunctionProgrammingLab\data\Rotten Tomatoes Movies.csv')
    output_dir = Path('plots')

    process_and_visualize(data_path, output_dir, config)


if __name__ == "__main__":
    main()
