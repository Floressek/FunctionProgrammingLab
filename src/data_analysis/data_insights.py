from pathlib import Path
from typing import Dict, List, NamedTuple, Any
from functools import reduce
import pandas as pd
from src.utils.types import MovieData
from src.utils.logger import setup_logger
from src.utils.config import ProjectConfig

logger = setup_logger('data_insights', ProjectConfig.get_log_file("data_insights"))

class GenreStats(NamedTuple):
    genre: str
    avg_rating: float
    movie_count: int
    avg_runtime: float

def get_genre_statistics(data: MovieData, min_movies: int = 10) -> List[GenreStats]:
    """Get statistics for each genre with minimum number of movies"""
    try:
        genre_stats = (data.df.groupby('genre')
                      .agg({
                          'tomatometer_rating': ['mean', 'count'],
                          'runtime_in_minutes': 'mean'
                      })
                      .pipe(lambda x: x[x[('tomatometer_rating', 'count')] >= min_movies]))

        return list(map(
            lambda x: GenreStats(
                genre=x[0],
                avg_rating=x[1][('tomatometer_rating', 'mean')],
                movie_count=int(x[1][('tomatometer_rating', 'count')]),
                avg_runtime=x[1][('runtime_in_minutes', 'mean')]
            ),
            genre_stats.iterrows()
        ))
    except Exception as e:
        logger.error(f"Error calculating genre statistics: {e}")
        raise

def get_movie_table_header() -> List[str]:
    return [
        "| Title | Year | Critics | Critics Votes | Audience | Audience Votes |\n",
        "|-------|------|---------|---------------|----------|----------------|\n"
    ]

def get_controversy_table_header() -> List[str]:
    return [
        "| Title | Year | Critics | Critics Votes | Audience | Audience Votes | Difference |\n",
        "|-------|------|---------|---------------|----------|----------------|------------|\n"
    ]

def format_movie_row(row) -> str:
    return (f"| {row.movie_title:<30} | {row.release_year:>4.0f} | "
            f"{row.tomatometer_rating:>6.1f}% | {int(row.tomatometer_count):>12,} | "
            f"{row.audience_rating:>6.1f}% | {int(row.audience_count):>12,} |\n")

def format_controversy_row(row) -> str:
    return (f"| {row.movie_title:<30} | {row.release_year:>4.0f} | "
            f"{row.tomatometer_rating:>6.1f}% | {int(row.tomatometer_count):>12,} | "
            f"{row.audience_rating:>6.1f}% | {int(row.audience_count):>12,} | "
            f"{abs(row.tomatometer_rating - row.audience_rating):>6.1f}% |\n")

def get_top_rated_movies(data: MovieData) -> List[str]:
    """Get top rated movies by both critics and audience"""
    try:
        # i dont know whats wrong with the types here and in the one below ;c
        return list(map(
            format_movie_row,
            data.valid_ratings
            .assign(avg_rating=lambda x: (x['tomatometer_rating'] + x['audience_rating']) / 2)
            .nlargest(20, 'avg_rating')
            .itertuples(index=False)
        ))
    except Exception as e:
        logger.error(f"Error getting top rated movies: {e}")
        raise

def find_rating_discrepancies(data: MovieData, threshold: float = 30.0) -> List[str]:
    """Find movies with big differences between critic and audience ratings"""
    try:
        return list(map(
            format_controversy_row,
            data.valid_ratings
            .assign(rating_diff=lambda x: abs(x['tomatometer_rating'] - x['audience_rating']))
            .query(f'rating_diff >= {threshold}')
            .nlargest(20, 'rating_diff')
            .itertuples(index=False)
        ))
    except Exception as e:
        logger.error(f"Error finding rating discrepancies: {e}")
        raise

def format_genre_row(stat: GenreStats) -> str:
    return f"| {stat.genre:<20} | {stat.avg_rating:>6.1f}% | {stat.movie_count:>5} | {stat.avg_runtime:>6.1f} min |\n"

def get_genre_table_header() -> List[str]:
    return [
        "| Genre                | Rating  | Count | Runtime |\n",
        "|----------------------|---------|-------|----------|\n"
    ]

def format_table_section(items: List[str], headers: List[str]) -> str:
    return reduce(lambda acc, section: acc + section, [*headers, *("".join(items))], "")

def generate_key_insights(data: MovieData, output_dir: Path) -> Dict[str, Any]:
    """Generate all insights using functional programming patterns"""
    try:
        insights = {
            "top_rated": get_top_rated_movies(data),
            "genre_stats": get_genre_statistics(data),
            "rating_discrepancies": find_rating_discrepancies(data)
        }

        markdown_sections = [
            "# Movie Analysis Insights\n",
            "\n## Top 20 Highest Rated Movies\n",
            format_table_section(insights["top_rated"], get_movie_table_header()),
            "\n## Most Controversial Movies\n",
            format_table_section(insights["rating_discrepancies"], get_controversy_table_header()),
            "\n## Genre Statistics\n",
            format_table_section(map(format_genre_row, insights["genre_stats"]), get_genre_table_header())
        ]

        markdown_content = reduce(lambda acc, section: acc + section, markdown_sections, "")
        output_path = output_dir / "movie_insights.md"
        output_path.write_text(markdown_content)
        logger.info(f"Insights saved to {output_path}")

        return insights
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise