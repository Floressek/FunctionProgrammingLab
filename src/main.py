# src/main.py
from pathlib import Path
from typing import List, Callable, Tuple
from functools import partial
import warnings

from matplotlib.figure import Figure

from src.utils import MovieData, PlotConfig
from utils.types import MovieData, PlotConfig
from utils.logger import setup_logger
from utils.config import ProjectConfig
from data_analysis.data_processing import read_movie_data
from data_analysis.data_insights import generate_key_insights
from data_analysis.visualization import (
    create_heatmap,
    create_genre_comparison,
    create_yearly_trends,
    create_runtime_analysis,
    save_plot
)

warnings.filterwarnings("ignore")

ProjectConfig.setup()
logger = setup_logger(__name__, ProjectConfig.get_log_file("main"))

PlotFunction = Tuple[str, Callable[[MovieData, PlotConfig], None]]


def _create_plot_functions(config: PlotConfig) -> list[
    tuple[str, Callable[[MovieData, PlotConfig], Figure]] | tuple[str, Callable[[MovieData, PlotConfig], Figure]] |
    tuple[str, Callable[[MovieData, PlotConfig], Figure]] | tuple[str, Callable[[MovieData, PlotConfig], Figure]]]:
    """Create list of plot generation functions with config"""
    return [
        ("heatmap", create_heatmap),
        ("genres", create_genre_comparison),
        ("trends", create_yearly_trends),
        ("runtime", create_runtime_analysis)
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

        # Generate insights
        logger.info("Generating insights...")
        _ = generate_key_insights(movie_data, ProjectConfig.PLOTS_DIR)  # print insights

        # Generate and save plots
        logger.info("Generating visualizations...")
        plot_functions = _create_plot_functions(config)

        for plot_name, plot_func in plot_functions:
            try:
                fig = plot_func(movie_data, config)
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
    # Tried to use relative paths, but it didn't work, just add the full path of both on your machine
    # data_path = Path(r'C:\Users\szyme\PycharmProjects\FunctionProgrammingLab\data\Rotten Tomatoes Movies.csv')
    # output_dir = Path(r'C:\Users\szyme\PycharmProjects\FunctionProgrammingLab\plots')
    #
    # process_and_visualize(data_path, output_dir, config)

    data_path = ProjectConfig.DATA_DIR / "Rotten Tomatoes Movies.csv"
    output_dir = ProjectConfig.PLOTS_DIR

    process_and_visualize(data_path, output_dir, config)


if __name__ == "__main__":
    main()
