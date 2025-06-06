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
    # sidebar filters
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

    # Key Metrics Row
    st.header("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_cases = (
            filtered_data["Confirmed Cases"].max() if not filtered_data.empty else 0
        )
        st.metric("Total Cases", f"{total_cases:,}")

    with col2:
        total_deaths = filtered_data["Deaths"].max() if not filtered_data.empty else 0
        st.metric("Total Deaths", f"{total_deaths:,}")

    with col3:
        total_fatality_rate = (
            (total_deaths / total_cases * 100) if total_cases > 0 else 0
        )
        st.metric("Fatality Rate", f"{total_fatality_rate:.2f}%")

    with col4:
        countries_count = (
            filtered_data["Country/Region"].nunique() if not filtered_data.empty else 0
        )
        st.metric("Countries Affected", f"{countries_count:,}")

    # Charts
    if not filtered_data.empty:
        st.header("📈 Time Series Analysis")

        # Aggregate by date for timeseries
        time_series_data = (
            filtered_data.groupby("Date")
            .agg(
                {
                    "New_Cases": "sum",
                    "New_Deaths": "sum",
                    "Cases_7day_avg": "sum",
                    "Deaths_7day_avg": "sum",
                }
            )
            .reset_index()
        )

        fig_time = go.Figure()
        fig_time.add_trace(
            go.Scatter(
                x=time_series_data["Date"],
                y=time_series_data["Cases_7day_avg"],
                mode="lines",
                name="7-Day Avg New Cases",
                line=dict(color="blue"),
            )
        )

        fig_time.update_layout(
            title="7-Day Average New Cases Over Time",
            xaxis_title="Date",
            yaxis_title="New Cases",
            hovermode="x unified",
        )

        st.plotly_chart(fig_time, use_container_width=True)

        # Geographical Distribution
        if selected_country == "All":
            st.header("🌍 Global Distribution")

            latest_data = filtered_data[
                filtered_data["Date"] == filtered_data["Date"].max()
            ]
            top_countries = latest_data.nlargest(20, "Confirmed Cases")

            fig_geo = px.bar(
                top_countries,
                x="Confirmed Cases",
                y="Country/Region",
                color="Confirmed Cases",
                title="Top 20 Countries by Confirmed Cases",
                orientation="h",
            )
            fig_geo.update_layout(height=600)
            st.plotly_chart(fig_geo, use_container_width=True)
        else:
            st.warning("NO Data available for selected filters.")

        # Healthcare Insights section
        st.header("🏥 Healthcare Insights")

        with st.expnder("Key Findings"):
            st.write(
                """
                     1. **Peak Load Periods**: Identify when healthcare systems experienced maximum strain
                     2. **Resource Allocation**: Understand regional variations in healthcare capacity needs
                    3. **Recovery Patterns**: Analyze how different regions managed pandemic waves
                    4. **Demographic Impact**: Examine which populations were most affected
        
                    **Business Value:**
                    - Hospital capacity planning optimization
                    - Resource allocation efficiency improvements
                    - Emergency preparedness enhancement
                    - Cost reduction through predictive insights
                     """
            )
            # Footer
            st.markdown("-----")
            st.markdown("Dashboard created for healthcare analytics project.")


if __name__ == "__main__":
    main()
