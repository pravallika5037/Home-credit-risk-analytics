import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import config
from Utils.data_loader import load_dataset

st.set_page_config(
    page_title="Default Risk Analysis",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = load_dataset(config.DATASET_FILES["application"])

    # Calculate age
    df["AGE_YEARS"] = -df["DAYS_BIRTH"] / 365.25

    # Age groups
    df["AGE_GROUP"] = pd.cut(
        df["AGE_YEARS"],
        bins=[0, 25, 35, 45, 55, np.inf],
        labels=["< 25", "26 - 35", "36 - 45",
                "46 - 55", "> 56"]
    )

    # Income bands
    df["INCOME_BAND"] = pd.cut(
        df["AMT_INCOME_TOTAL"],
        bins=[0, 75000, 150000, 300000, 600000, np.inf],
        labels=["< 75K", "75K - 150K",
                "150K - 300K", "300K - 600K", "> 600K"]
    )

    return df


df = load_data()

# Dashboard title
st.title("⚠️ Default Risk Analysis")
st.caption(
    "Analyze loan default patterns and identify high-risk customer segments."
)

# Sidebar filters
st.sidebar.header("Filters")

contract = st.sidebar.multiselect(
    "Contract Type",
    df["NAME_CONTRACT_TYPE"].dropna().unique(),
    default=list(df["NAME_CONTRACT_TYPE"].dropna().unique())
)

gender = st.sidebar.multiselect(
    "Gender",
    df["CODE_GENDER"].dropna().unique(),
    default=list(df["CODE_GENDER"].dropna().unique())
)

education = st.sidebar.multiselect(
    "Education",
    df["NAME_EDUCATION_TYPE"].dropna().unique(),
    default=list(df["NAME_EDUCATION_TYPE"].dropna().unique())
)

income = st.sidebar.multiselect(
    "Income Band",
    df["INCOME_BAND"].dropna().unique(),
    default=list(df["INCOME_BAND"].dropna().unique())
)

age = st.sidebar.multiselect(
    "Age Group",
    df["AGE_GROUP"].dropna().unique(),
    default=list(df["AGE_GROUP"].dropna().unique())
)

# Filter data
filtered = df[
    (df["NAME_CONTRACT_TYPE"].isin(contract)) &
    (df["CODE_GENDER"].isin(gender)) &
    (df["NAME_EDUCATION_TYPE"].isin(education)) &
    (df["INCOME_BAND"].isin(income)) &
    (df["AGE_GROUP"].isin(age))
].copy()

# Calculate KPIs
total = len(filtered)

defaults = filtered["TARGET"].sum()

non_defaults = total - defaults

default_rate = (
    defaults / total * 100 if total > 0 else 0
)

default_customers = filtered[
    filtered["TARGET"] == 1
]

average_credit = default_customers[
    "AMT_CREDIT"
].mean()

average_income = default_customers[
    "AMT_INCOME_TOTAL"
].mean()

# High-risk prediction probability
# Only available if a PD column exists in the dataset
pd_columns = [
    "PD", "PREDICTED_PROBABILITY", "DEFAULT_PROBABILITY"
]

pd_column = next(
    (c for c in pd_columns if c in filtered.columns),
    None
)

if pd_column:
    high_risk = (
        filtered[pd_column] >= 0.20
    ).sum()
else:
    high_risk = None

# KPI cards
st.subheader("Default Risk Overview")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total Defaults", f"{defaults:,.0f}")

c2.metric(
    "Default Rate",
    f"{default_rate:.2f}%"
)

c3.metric(
    "Non-default Customers",
    f"{non_defaults:,}"
)

c4.metric(
    "High-risk Applications",
    f"{high_risk:,}" if high_risk is not None else "N/A"
)

c5.metric(
    "Avg. Credit (Defaulters)",
    f"₹ {average_credit:,.0f}"
    if pd.notna(average_credit) else "N/A"
)

c6.metric(
    "Avg. Income (Defaulters)",
    f"₹ {average_income:,.0f}"
    if pd.notna(average_income) else "N/A"
)

st.divider()

# Default vs Non-default
st.subheader("Default vs Non-default")

risk_data = pd.DataFrame({
    "Status": ["Default", "Non-default"],
    "Customers": [defaults, non_defaults]
})

fig1 = px.pie(
    risk_data,
    names="Status",
    values="Customers",
    hole=0.60,
    color="Status",
    color_discrete_map={
        "Default": "#D94B45",
        "Non-default": "#45B99A"
    }
)

fig1.update_traces(
    textinfo="percent+label"
)

# Default rate by gender
gender_data = (
    filtered.groupby("CODE_GENDER")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

gender_data.columns = ["Gender", "Default Rate"]

fig2 = px.bar(
    gender_data,
    x="Gender",
    y="Default Rate",
    color="Gender",
    text_auto=".2f",
    title="Default Rate by Gender"
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, width="stretch")

with col2:
    st.plotly_chart(fig2, width="stretch")

# Default rate by education
st.subheader("Default Rate by Education")

education_data = (
    filtered.groupby("NAME_EDUCATION_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

education_data.columns = ["Education", "Default Rate"]

education_data = education_data.sort_values(
    "Default Rate",
    ascending=True
)

fig3 = px.bar(
    education_data,
    x="Default Rate",
    y="Education",
    orientation="h",
    text_auto=".2f",
    color="Default Rate",
    title="Default Rate by Education"
)

st.plotly_chart(fig3, width="stretch")

# Default rate by income band
st.subheader("Default Rate by Income Band")

income_data = (
    filtered.groupby("INCOME_BAND", observed=True)["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

income_data.columns = ["Income Band", "Default Rate"]

fig4 = px.bar(
    income_data,
    x="Income Band",
    y="Default Rate",
    text_auto=".2f",
    color="Default Rate",
    title="Default Rate by Income Band"
)

st.plotly_chart(fig4, width="stretch")

# Default rate by age group
st.subheader("Default Rate by Age Group")

age_data = (
    filtered.groupby("AGE_GROUP", observed=True)["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

age_data.columns = ["Age Group", "Default Rate"]

fig5 = px.bar(
    age_data,
    x="Age Group",
    y="Default Rate",
    text_auto=".2f",
    color="Default Rate",
    title="Default Rate by Age Group"
)

st.plotly_chart(fig5, width="stretch")

# Default rate by contract type
st.subheader("Default Rate by Contract Type")

contract_data = (
    filtered.groupby("NAME_CONTRACT_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
)

contract_data.columns = ["Contract Type", "Default Rate"]

fig6 = px.bar(
    contract_data,
    x="Contract Type",
    y="Default Rate",
    text_auto=".2f",
    color="Contract Type",
    title="Default Rate by Contract Type"
)

st.plotly_chart(fig6, width="stretch")

# High-risk customer segment
st.subheader("High-Risk Customer Segment (Sample)")

high_risk_data = filtered[
    filtered["TARGET"] == 1
]

columns = [
    "SK_ID_CURR",
    "TARGET",
    "CODE_GENDER",
    "NAME_EDUCATION_TYPE",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "NAME_CONTRACT_TYPE",
    "DAYS_BIRTH"
]

table = high_risk_data[columns].head(100).copy()

table["DAYS_BIRTH"] = table["DAYS_BIRTH"].abs()

st.dataframe(
    table,
    width="stretch"
)

# Download CSV
csv = table.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Table (CSV)",
    data=csv,
    file_name="high_risk_customers.csv",
    mime="text/csv"
)

st.caption(
    f"Total Applications: {total:,} | "
    f"Total Defaults: {defaults:,}"
)