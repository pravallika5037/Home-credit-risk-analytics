from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "application_train.csv"
PAGE_PATH = PROJECT_DIR / "pages" / "credit bureau analysis.py"

st.set_page_config(page_title="Credit Bureau Analysis", layout="wide")


@st.cache_data
def load_application_data():
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Dataset file not found: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)


def load_credit_bureau_page():
    if not PAGE_PATH.is_file():
        raise FileNotFoundError(f"Dashboard page not found: {PAGE_PATH}")

    spec = spec_from_file_location("credit_bureau_analysis", PAGE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load dashboard page: {PAGE_PATH}")

    page_module = module_from_spec(spec)
    spec.loader.exec_module(page_module)
    return page_module.app


try:
    application_data = load_application_data()
    render_page = load_credit_bureau_page()
except (FileNotFoundError, ImportError) as error:
    st.error(str(error))
    st.stop()

render_page(application_data)
