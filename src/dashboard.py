import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    """Load Processed Data"""
    covid_data = pd.read_csv("data/processed/covid_data.csv")
    covid_data["Date"] = pd.to_datetime(covid_data["Date"])

    with open("data/processed/summary.json", "r") as f:
        summary_stats = pd.read_json(f)

    return covid_data, summary_stats


def main():
    st.title("🏥 COVID-19 Dashboard")
    st.markdown("Analyze Covid impact on healthcare systems globally.")

    # Load data
    try:
        covid_data, summary_stats = load_data()
    except FileNotFoundError:
        st.error(
            "Data is not loaded, make sure to run data collection and data processing scripts before running this script.."
        )
        st.stop()
    # sidbar filters
    st.sidebar("🔍 Filters")
    countries = ["All"] + sorted(covid_data["Country/Region"].unique())
    selected_country = st.sidebar.selectbox("Select Country", countries)
    date_range = st.sidebar.selection(
        "Select Date Range",
        value=(covid_data["Date"].min(), covid_data["Date"].max()),
        min_value=covid_data["Date"].min(),
        max_value=covid_data["Date"].max(),
    )

    # Filter data based on the selection
    filtered_data = covid_data.copy()

    if selected_country != "All":
        filtered_data = filtered_data[
            filtered_data["Country/Region"] == selected_country
        ]

    if len(date_range) == 2:
        filtered_data = filtered_data[
            (filtered_data["Date"] >= pd.to_datetime(date_range[0]))
            & (filtered_data["Date"] <= pd.to_datetime(date_range[1]))
        ]
