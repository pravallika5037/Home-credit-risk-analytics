import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import config
from Utils.data_loader import load_dataset

# Page configuration
st.set_page_config(
    page_title="Income & Employment",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = load_dataset(config.DATASET_FILES["application"])

    # Employment duration in years
    df["EMPLOYMENT_YEARS"] = np.where(
        df["DAYS_EMPLOYED"] == 365243,
        np.nan,
        df["DAYS_EMPLOYED"].abs() / 365.25
    )

    # Employment duration groups
    df["EMPLOYMENT_GROUP"] = pd.cut(
        df["EMPLOYMENT_YEARS"],
        bins=[0, 1, 3, 5, 10, 15, 20, np.inf],
        labels=[
            "0-1", "1-3", "3-5", "5-10",
            "10-15", "15-20", "20+"
        ],
        include_lowest=True
    )

    return df


df = load_data()

# Dashboard title
st.title("💼 Income & Employment")
st.caption(
    "Analyze customer income levels, employment profile, "
    "and their relationship with loan default risk."
)

# Sidebar filters
st.sidebar.header("Filters")

contract_options = ["All"] + sorted(
    df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()
)

selected_contract = st.sidebar.selectbox(
    "Contract Type",
    contract_options
)

occupation_options = ["All"] + sorted(
    df["OCCUPATION_TYPE"].dropna().unique().tolist()
)

selected_occupation = st.sidebar.selectbox(
    "Occupation Type",
    occupation_options
)

income_options = ["All"] + sorted(
    df["NAME_INCOME_TYPE"].dropna().unique().tolist()
)

selected_income = st.sidebar.selectbox(
    "Income Type",
    income_options
)

target_options = ["All", 0, 1]

selected_target = st.sidebar.selectbox(
    "Target (Default)",
    target_options
)

# Apply filters
filtered = df.copy()

if selected_contract != "All":
    filtered = filtered[
        filtered["NAME_CONTRACT_TYPE"] == selected_contract
    ]

if selected_occupation != "All":
    filtered = filtered[
        filtered["OCCUPATION_TYPE"] == selected_occupation
    ]

if selected_income != "All":
    filtered = filtered[
        filtered["NAME_INCOME_TYPE"] == selected_income
    ]

if selected_target != "All":
    filtered = filtered[
        filtered["TARGET"] == selected_target
    ]

# KPI calculations
total = len(filtered)

average_income = filtered["AMT_INCOME_TOTAL"].mean()

median_income = filtered["AMT_INCOME_TOTAL"].median()

average_employment = filtered["EMPLOYMENT_YEARS"].mean()

# Employment status based on DAYS_EMPLOYED
employed = filtered["EMPLOYMENT_YEARS"].notna().sum()

unemployed = total - employed

employed_percentage = (
    employed / total * 100 if total else 0
)

unemployed_percentage = (
    unemployed / total * 100 if total else 0
)

# Default rate for recorded employed customers
employed_data = filtered[
    filtered["EMPLOYMENT_YEARS"].notna()
]

employed_default_rate = (
    employed_data["TARGET"].mean() * 100
    if len(employed_data) else 0
)

# KPI cards
st.subheader("Income & Employment Overview")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    "Average Income",
    f"₹ {average_income:,.0f}" if total else "N/A"
)

c2.metric(
    "Median Income",
    f"₹ {median_income:,.0f}" if total else "N/A"
)

c3.metric(
    "Avg. Employment Duration",
    f"{average_employment:.2f} Years"
    if pd.notna(average_employment) else "N/A"
)

c4.metric(
    "Employed Customers",
    f"{employed_percentage:.2f}%"
)

c5.metric(
    "Unemployed Customers",
    f"{unemployed_percentage:.2f}%"
)

c6.metric(
    "Default Rate (Employed)",
    f"{employed_default_rate:.2f}%"
)

st.divider()

# Chart 1: Income distribution
st.subheader("Income Distribution")

fig1 = px.histogram(
    filtered,
    x="AMT_INCOME_TOTAL",
    nbins=30,
    title="Customer Income Distribution",
    labels={
        "AMT_INCOME_TOTAL": "Income",
        "count": "Number of Customers"
    },
    color_discrete_sequence=["#267C50"]
)

if total:
    fig1.add_vline(
        x=average_income,
        line_dash="dash",
        annotation_text=f"Mean: {average_income:,.0f}"
    )

    fig1.add_vline(
        x=median_income,
        line_dash="dot",
        annotation_text=f"Median: {median_income:,.0f}"
    )

# Chart 2: Average income by occupation
occupation_income = (
    filtered.groupby("OCCUPATION_TYPE")["AMT_INCOME_TOTAL"]
    .mean()
    .reset_index()
    .sort_values("AMT_INCOME_TOTAL", ascending=False)
    .head(8)
)

fig2 = px.bar(
    occupation_income,
    x="AMT_INCOME_TOTAL",
    y="OCCUPATION_TYPE",
    orientation="h",
    text_auto=".0f",
    title="Average Income by Occupation (Top 8)",
    color_discrete_sequence=["#176B43"]
)

fig2.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

# Chart 3: Employment duration distribution
employment_data = filtered.dropna(
    subset=["EMPLOYMENT_GROUP"]
)

duration_counts = (
    employment_data["EMPLOYMENT_GROUP"]
    .value_counts()
    .sort_index()
    .reset_index()
)

duration_counts.columns = [
    "Employment Duration",
    "Customers"
]

fig3 = px.bar(
    duration_counts,
    x="Employment Duration",
    y="Customers",
    title="Employment Duration Distribution",
    color_discrete_sequence=["#C28A2C"]
)

col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(fig1, width="stretch")

with col2:
    st.plotly_chart(fig2, width="stretch")

with col3:
    st.plotly_chart(fig3, width="stretch")

st.divider()

# Chart 4: Default rate by occupation
st.subheader("Default Rate by Occupation")

occupation_default = (
    filtered.groupby("OCCUPATION_TYPE")["TARGET"]
    .mean()
    .mul(100)
    .reset_index()
    .sort_values("TARGET", ascending=False)
)

occupation_default.columns = [
    "Occupation",
    "Default Rate"
]

fig4 = px.bar(
    occupation_default,
    x="Occupation",
    y="Default Rate",
    text_auto=".2f",
    title="Default Rate by Occupation",
    color_discrete_sequence=["#D49A24"]
)

# Chart 5: Income vs Credit Amount
st.subheader("Income vs. Credit Amount")

if len(filtered) > 5000:
    scatter_data = filtered.sample(
        5000,
        random_state=42
    )
else:
    scatter_data = filtered

fig5 = px.scatter(
    scatter_data,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    color="TARGET",
    opacity=0.5,
    title="Income vs Credit Amount",
    labels={
        "AMT_INCOME_TOTAL": "Income",
        "AMT_CREDIT": "Credit Amount",
        "TARGET": "Default"
    },
    color_discrete_map={
        0: "#23784D",
        1: "#D49A24"
    }
)

correlation = filtered[
    ["AMT_INCOME_TOTAL", "AMT_CREDIT"]
].corr().iloc[0, 1]

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig4, width="stretch")

with col2:
    st.plotly_chart(fig5, width="stretch")

st.info(
    f"Income vs Credit Correlation: "
    f"r = {correlation:.2f}"
    if pd.notna(correlation)
    else "Income vs Credit Correlation: N/A"
)

st.divider()

# Customer details table
st.subheader("📋 Customer Income & Employment Details")

columns = [
    "SK_ID_CURR",
    "AMT_INCOME_TOTAL",
    "NAME_INCOME_TYPE",
    "OCCUPATION_TYPE",
    "DAYS_EMPLOYED",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "TARGET"
]

table = filtered[columns].head(100).copy()

# Convert employment days to positive values
table["DAYS_EMPLOYED"] = table["DAYS_EMPLOYED"].abs()

st.dataframe(
    table,
    width="stretch",
    hide_index=True
)

# Download CSV
csv = table.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Data (CSV)",
    data=csv,
    file_name="income_employment_data.csv",
    mime="text/csv"
)

st.caption(
    f"Showing 1 to {len(table)} of {total:,} customers"
)