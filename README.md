# Movie Analysis Project

Functional programming approach to movie data analysis and visualization.

## Project Structure

```
FunctionProgrammingLab/
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── types.py
│   │   └── logger.py
│   ├── data_analysis/
│   │   ├── __init__.py
│   │   ├── data_insights.py
│   │   ├── data_processing.py
│   │   └── visualization.py
│   ├── __init__.py
│   └── main.py
├── data/         # Dane wejściowe
│   └── Rotten Tomatoes Movies.csv
├── plots/        # Wygenerowane wykresy
│   ├── movie_analysis_heatmap.png
│   ├── movie_analysis_genres.png
│   ├── movie_analysis_trends.png
│   └── movie_analysis_runtime.png
├── logs/         # Pliki logów
│   ├── main.log
│   ├── data_processing.log
│   ├── visualization.log
│   └── types.log
├── .gitignore
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Sequence diagram and features

```mermaid
sequenceDiagram
    participant Main as main.py
    participant DP as data_processing.py
    participant Types as types.py
    participant Viz as visualization.py
    participant DI as data_insights.py
    participant FS as FileSystem
    Main->>Types: Create PlotConfig
    Main->>DP: read_movie_data(file_path)
    DP->>FS: Read CSV file
    FS-->>DP: Raw DataFrame
    
    rect rgba(0, 128, 0, 0.1)
        Note over DP: process_raw_data
        DP->>DP: *convert_dates
        DP->>DP: *convert_numeric_columns
        DP->>DP: *filter_valid_data
        DP->>DP: *clean_genres
    end
    DP->>Types: Create MovieData
    Types-->>DP: MovieData instance
    DP-->>Main: Return MovieData
    Main->>Main: create_plot_functions(config)
    
    rect rgba(255, 0, 0, 0.1)
        Note over Main,DI: Generate insights
        Main->>DI: generate_key_insights(movie_data, output_dir)
        DI->>Types: valid_ratings/valid_runtime
        Types-->>DI: Filtered DataFrame
        DI->>DI: Generate markdown
        DI->>FS: Save insights.md
    end
    
    rect rgba(0, 0, 255, 0.1)
        Note over Main,Viz: Generate each visualization
        loop For each plot function
            Main->>Viz: plot_func(movie_data)
            Viz->>Types: valid_ratings/valid_runtime
            Types-->>Viz: Filtered DataFrame
            Viz->>Viz: Create visualization
            Viz-->>Main: Return Figure
            Main->>Viz: save_plot(fig, name, output_dir)
            Viz->>FS: Save PNG file
        end
    end
    Note over Main: Processing complete
```
- Functional programming approach with immutable data structures
- Pure functions for data processing and visualization
- Type hints and runtime type checking
- Comprehensive test suite
- Poetry for dependency management

## Installation

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

## Usage

Run the analysis:
```bash
poetry run python src/main.py
```

Run tests:
```bash
poetry run pytest
```

## Key Principles

- Immutable data structures using `@dataclass(frozen=True)`
- Pure functions for all data transformations
- Function composition for data processing pipelines
- Strong type hints and validation
- Comprehensive error handling
- Clear separation of concerns
