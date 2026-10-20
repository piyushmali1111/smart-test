"""Configuration and global constants for Smart Test Selection."""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Global Seed
SEED: int = int(os.getenv("SEED", "42"))

# Paths
BACKEND_DIR: Path = Path(__file__).resolve().parent.parent.parent
PROJECT_PATH_STR: str = os.getenv("PROJECT_PATH", "sample_project")
SAMPLE_PROJECT_DIR: Path = (
    (BACKEND_DIR / PROJECT_PATH_STR)
    if not Path(PROJECT_PATH_STR).is_absolute()
    else Path(PROJECT_PATH_STR)
)
SHOP_DIR: Path = SAMPLE_PROJECT_DIR / "shop"
SAMPLE_TESTS_DIR: Path = SAMPLE_PROJECT_DIR / "tests"
ARTIFACTS_DIR: Path = BACKEND_DIR / "artifacts"
PLOTS_DIR: Path = ARTIFACTS_DIR / "plots"

# Server configuration
PORT: int = int(os.getenv("PORT", "8000"))
HOST: str = os.getenv("HOST", "0.0.0.0")
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
REAL_SLEEP: bool = os.getenv("REAL_SLEEP", "0") == "1"

# Budget configuration
BUDGET_RANGE = {
    "min": 5,
    "max": 300,
    "step": 5,
    "default": 30,
}

BUDGET_GRID = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300]
REFERENCE_BUDGET_SEC: int = 30

# Mutation & dataset parameters
TARGET_MUTANTS: int = 450
MUTANT_TIMEOUT_SEC: float = 60.0
TOTAL_ROUNDS: int = 10
TRAIN_ROUNDS_MAX: int = 7  # rounds 1..7 are train, 8..10 are holdout

# Algorithm parameters
BNB_TIME_LIMIT_SEC: float = 2.0
DP_DISCRETIZATION_UNIT_SEC: float = 0.1  # 0.1s units for knapsack capacity
