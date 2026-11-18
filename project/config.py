from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_FILES = {
    "application": PROJECT_ROOT / "data" / "application_train.csv",
    "bureau": PROJECT_ROOT / "data" / "bureau.csv",
}

CHART_COLORS = [
    "#1B365D",
    "#0D9488",
    "#36B6A5",
    "#267C50",
    "#D49A24",
]
