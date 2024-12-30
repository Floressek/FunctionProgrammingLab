from pathlib import Path

class ProjectConfig:
    """Configuration for the project."""
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent # ;) 3 levels up
    LOGS_DIR = PROJECT_ROOT / "logs"
    DATA_DIR = PROJECT_ROOT / "data"
    PLOTS_DIR = PROJECT_ROOT / "plots"

    @classmethod
    def setup(cls):
        """Create necessary directories."""
        for directory in [cls.DATA_DIR, cls.PLOTS_DIR]:
            directory.mkdir(exist_ok=True)

        if not cls.LOGS_DIR.exists():
            cls.LOGS_DIR.mkdir()

    @classmethod
    def get_log_file(cls, name: str) -> str:
        """Return a path to a log file with the specified name."""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        return str(cls.LOGS_DIR / f"{name}.log")