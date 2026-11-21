import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import config
from Utils.data_loader import load_dataset

# Page configuration
st.set_page_config(
    page_title="Loan Application Analysis",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    df = load_dataset(config.DATASET_FILES["application"])

    # Calculate loan-to-income ratio
    df["LOAN_TO_INCOME"] = (
        df["AMT_CREDIT"] /
        df["AMT_INCOME_TOTAL"].replace(0, np.nan)
    )

    # Calculate annuity-to-income ratio
    df["ANNUITY_TO_INCOME"] = (
        df["AMT_ANNUITY"] /
        df["AMT_INCOME_TOTAL"].replace(0, np.nan)
    )

    return df


df = load_data()

# Dashboard title
st.title("💼 Loan Application Analysis")

st.caption(
    "Analyze loan amounts, contract types, and key ratios "
    "for Home Credit applications."
)

# Sidebar filters
st.sidebar.header("Filters")

# Contract type
contract_options = ["All"] + sorted(
    df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()
)

selected_contract = st.sidebar.selectbox(
    "Contract Type",
    contract_options
)

# Gender
gender_options = ["All"] + sorted(
    df["CODE_GENDER"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Gender",
    gender_options
)

# Income range
min_income = float(df["AMT_INCOME_TOTAL"].min())
max_income = float(df["AMT_INCOME_TOTAL"].max())

income_range = st.sidebar.slider(
    "Income Range",
    min_value=min_income,
    max_value=max_income,
    value=(min_income, max_income)
)

# Credit amount range
min_credit = float(df["AMT_CREDIT"].min())
max_credit = float(df["AMT_CREDIT"].max())

credit_range = st.sidebar.slider(
    "Credit Amount Range",
    min_value=min_credit,
    max_value=max_credit,
    value=(min_credit, max_credit)
)

# Target
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

if selected_gender != "All":
    filtered = filtered[
        filtered["CODE_GENDER"] == selected_gender
    ]

filtered = filtered[
    (filtered["AMT_INCOME_TOTAL"] >= income_range[0]) &
    (filtered["AMT_INCOME_TOTAL"] <= income_range[1])
]

filtered = filtered[
    (filtered["AMT_CREDIT"] >= credit_range[0]) &
    (filtered["AMT_CREDIT"] <= credit_range[1])
]

if selected_target != "All":
    filtered = filtered[
        filtered["TARGET"] == selected_target
    ]

# KPI calculations
total_applications = len(filtered)

total_loan_amount = filtered["AMT_CREDIT"].sum()

average_loan_amount = filtered["AMT_CREDIT"].mean()

median_loan_amount = filtered["AMT_CREDIT"].median()

average_loan_income = filtered["LOAN_TO_INCOME"].mean()

average_annuity_income = filtered[
    "ANNUITY_TO_INCOME"
].mean()

cash_loans = (
    filtered["NAME_CONTRACT_TYPE"] == "Cash loans"
).sum()

cash_loan_share = (
    cash_loans / total_applications * 100
    if total_applications else 0
)

average_goods_price = filtered["AMT_GOODS_PRICE"].mean()

# KPI cards
st.subheader("Loan Application Overview")

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

c1.metric(
    "Total Loan Amount",
    f"₹ {total_loan_amount:,.0f}"
)

c2.metric(
    "Average Loan Amount",
    f"₹ {average_loan_amount:,.2f}"
    if pd.notna(average_loan_amount) else "N/A"
)

c3.metric(
    "Median Loan Amount",
    f"₹ {median_loan_amount:,.2f}"
    if pd.notna(median_loan_amount) else "N/A"
)

c4.metric(
    "Avg. Loan-to-Income",
    f"{average_loan_income:.2f}"
    if pd.notna(average_loan_income) else "N/A"
)

c5.metric(
    "Avg. Annuity-to-Income",
    f"{average_annuity_income:.2f}"
    if pd.notna(average_annuity_income) else "N/A"
)

c6.metric(
    "Cash Loan Share",
    f"{cash_loan_share:.2f}%"
)

c7.metric(
    "Avg. Goods Price",
    f"₹ {average_goods_price:,.2f}"
    if pd.notna(average_goods_price) else "N/A"
)

st.divider()

# Chart 1: Loan amount distribution
st.subheader("Loan Amount Distribution")

fig1 = px.histogram(
    filtered,
    x="AMT_CREDIT",
    nbins=30,
    title="Loan Amount Distribution",
    labels={
        "AMT_CREDIT": "Loan Amount",
        "count": "Number of Applications"
    },
    color_discrete_sequence=["#36B6A5"]
)

# Add mean and median
if total_applications > 0:
    fig1.add_vline(
        x=average_loan_amount,
        line_dash="dash",
        annotation_text="Mean"
    )

    fig1.add_vline(
        x=median_loan_amount,
        line_dash="dot",
        annotation_text="Median"
    )

# Chart 2: Credit amount by contract type
st.subheader("Credit Amount by Contract Type")

contract_data = (
    filtered.groupby("NAME_CONTRACT_TYPE")["AMT_CREDIT"]
    .sum()
    .reset_index()
)

fig2 = px.bar(
    contract_data,
    x="NAME_CONTRACT_TYPE",
    y="AMT_CREDIT",
    color="NAME_CONTRACT_TYPE",
    text_auto=".2s",
    title="Credit Amount by Contract Type",
    labels={
        "NAME_CONTRACT_TYPE": "Contract Type",
        "AMT_CREDIT": "Total Credit"
    }
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, width="stretch")

with col2:
    st.plotly_chart(fig2, width="stretch")

st.divider()

# Chart 3: Loan-to-income distribution
st.subheader("Loan-to-Income Distribution")

ratio_data = filtered.dropna(
    subset=["LOAN_TO_INCOME"]
)

fig3 = px.histogram(
    ratio_data,
    x="LOAN_TO_INCOME",
    nbins=40,
    histnorm="probability density",
    title="Loan-to-Income Distribution",
    labels={
        "LOAN_TO_INCOME": "Loan / Income Ratio"
    },
    color_discrete_sequence=["#36B6A5"]
)

# Chart 4: Annuity-to-income comparison
st.subheader("Annuity-to-Income Comparison")

annuity_data = (
    filtered.groupby("TARGET")["ANNUITY_TO_INCOME"]
    .mean()
    .reset_index()
)

annuity_data["TARGET"] = annuity_data["TARGET"].map({
    0: "Non-default (0)",
    1: "Default (1)"
})

fig4 = px.bar(
    annuity_data,
    x="TARGET",
    y="ANNUITY_TO_INCOME",
    color="TARGET",
    text_auto=".2f",
    title="Annuity-to-Income Comparison",
    labels={
        "TARGET": "Application Status",
        "ANNUITY_TO_INCOME": "Average Ratio"
    },
    color_discrete_map={
        "Non-default (0)": "#36B6A5",
        "Default (1)": "#E58B32"
    }
)

# Chart 5: Contract type share
st.subheader("Contract Type Share")

contract_share = (
    filtered["NAME_CONTRACT_TYPE"]
    .value_counts()
    .reset_index()
)

contract_share.columns = [
    "Contract Type",
    "Applications"
]

fig5 = px.pie(
    contract_share,
    names="Contract Type",
    values="Applications",
    hole=0.55,
    title="Contract Type Share",
    color_discrete_sequence=["#36B6A5", "#E58B32"]
)

col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(fig3, width="stretch")

with col2:
    st.plotly_chart(fig4, width="stretch")

with col3:
    st.plotly_chart(fig5, width="stretch")

st.divider()

# Loan application details
st.subheader("📋 Loan Application Details")

columns = [
    "SK_ID_CURR",
    "NAME_CONTRACT_TYPE",
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "TARGET"
]

table = filtered[columns].head(100).copy()

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
    file_name="loan_application_data.csv",
    mime="text/csv"
)

# Footer
st.caption(
    f"Showing {len(table)} records | "
    f"Total Applications: {total_applications:,}"
)