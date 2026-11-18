import numpy as np
import pandas as pd


def calculate_default_rate(data: pd.DataFrame) -> float:
    target = pd.to_numeric(data["TARGET"], errors="coerce").dropna()
    if target.empty:
        return 0.0
    return float(target.eq(1).mean() * 100)


def get_average_income(values: pd.Series) -> float:
    numeric_values = pd.to_numeric(values, errors="coerce").dropna()
    if numeric_values.empty:
        return 0.0
    return float(numeric_values.mean())


def calculate_age(data: pd.DataFrame) -> pd.Series:
    birth_days = pd.to_numeric(data["DAYS_BIRTH"], errors="coerce")
    return birth_days.abs() / 365.25


def create_age_groups(age: pd.Series) -> pd.Series:
    return pd.cut(
        age,
        bins=[0, 25, 35, 45, 55, np.inf],
        labels=["< 25", "26 - 35", "36 - 45", "46 - 55", "> 56"],
        include_lowest=True,
    )


def create_income_groups(income: pd.Series) -> pd.Series:
    return pd.cut(
        income,
        bins=[0, 75000, 150000, 300000, 600000, np.inf],
        labels=["< 75K", "75K - 150K", "150K - 300K", "300K - 600K", "> 600K"],
        include_lowest=True,
    )
