"""
Cross-platform Path Utilities

Provides platform-independent path handling for Linux/Windows/macOS.
Follows Linus principle: "Code should work everywhere, not just on my machine"
"""

from pathlib import Path
import os


def get_project_root() -> Path:
    """
    Get project root directory (cross-platform)

    Works by finding the directory containing 'CLAUDE.md'
    Returns absolute Path object
    """
    # Start from current file location
    current = Path(__file__).resolve()

    # Walk up directory tree to find project root
    for parent in [current] + list(current.parents):
        if (parent / "CLAUDE.md").exists():
            return parent
        if (parent / "README.md").exists() and (parent / "src").exists():
            return parent

    # Fallback: assume we're in src/main/python/utils
    return current.parent.parent.parent.parent


def get_data_dir() -> Path:
    """Get data directory (cross-platform)"""
    return get_project_root() / "data"


def get_file_storage_dir() -> Path:
    """Get file storage directory (cross-platform)"""
    base = os.getenv("FILE_STORAGE_PATH")
    if base:
        return Path(base)
    return get_data_dir() / "file_storage"


def get_database_path() -> Path:
    """Get database file path (cross-platform)"""
    db_url = os.getenv("DATABASE_URL", "")

    if db_url.startswith("sqlite:///"):
        # Extract path from SQLite URL
        db_path = db_url.replace("sqlite:///", "")
        if db_path.startswith("/") or ":" in db_path:
            # Absolute path
            return Path(db_path)
        # Relative path
        return get_project_root() / db_path

    # Default
    return get_data_dir() / "gallup_strengths.db"


def get_output_dir() -> Path:
    """Get output directory (cross-platform)"""
    return get_project_root() / "output"


def get_reports_dir() -> Path:
    """Get reports directory (cross-platform)"""
    return get_output_dir() / "reports"


def get_logs_dir() -> Path:
    """Get logs directory (cross-platform)"""
    return get_project_root() / "logs"


def ensure_dir_exists(path: Path) -> Path:
    """
    Ensure directory exists, create if not (cross-platform)

    Args:
        path: Directory path to ensure

    Returns:
        Path object (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# Convenience functions for common paths
def data_file(filename: str) -> Path:
    """Get path to data file (cross-platform)"""
    return get_data_dir() / filename


def file_storage_file(filename: str) -> Path:
    """Get path to file storage file (cross-platform)"""
    return ensure_dir_exists(get_file_storage_dir()) / filename


def output_file(filename: str) -> Path:
    """Get path to output file (cross-platform)"""
    return ensure_dir_exists(get_output_dir()) / filename


def report_file(filename: str) -> Path:
    """Get path to report file (cross-platform)"""
    return ensure_dir_exists(get_reports_dir()) / filename


# Example usage:
if __name__ == "__main__":
    print(f"Project root: {get_project_root()}")
    print(f"Data dir: {get_data_dir()}")
    print(f"File storage: {get_file_storage_dir()}")
    print(f"Database: {get_database_path()}")
    print(f"Reports: {get_reports_dir()}")

    # Test cross-platform file creation
    test_file = file_storage_file("test.json")
    print(f"Test file path: {test_file}")
    print(f"Path exists: {test_file.parent.exists()}")
