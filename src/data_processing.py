import pandas as pd
import numpy as np
from datetime import datetime
import os


class COVIDDataProcessor:
    def __init__(self, data_path="data/raw/"):
        self.data_path = data_path

    def load_raw_data(self):
        # Load raw data files
        try:
            self.cases = pd.read_csv(f"{self.data_path}jhu_cases.csv")
            self.deaths = pd.read_csv(f"{self.data_path}jhu_deaths.csv")
            self.population = pd.read_csv(f"{self.data_path}population_data.csv")
            print("Raw data loaded successfully.")
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            raise

    def transform_data(self):
        """Transform raw data into a usable format"""
        # Melt the cases and deaths dataframes

        def melt_covid_data(df, value_name):
            date_cols = df.columns[4:]  # Skip the first 4 columns

            melted_df = df.melt(
                id_vars=["Province/State", "Country/Region", "Lat", "Long"],
                value_vars=date_cols,
                var_name="Date",
                value_name=value_name,
            )
            # convert date string to dattime
            melted_df["Date"] = pd.to_datetime(melted_df["Date"])
            return melted

        cases_long = melt_covid_data(self.cases, "Confirmed Cases")
        deaths_long = melt_covid_data(self.deaths, "Deaths")

        # Meerge both data sets
        covid_data = cases_long.merge(
            deaths_long[
                ["Province/State", "Country/Region", "Lat", "Long", "Date", "Deaths"]
            ],
            on=["Province/State", "Country/Region", "Lat", "Long", "Date"],
            how="left",
        )

        # Calculate daily new cases and deaths
        covid_data = covid_data.sort_values(
            ["Country/Region", "Province/State", "Date"]
        )
        covid_data["New Cases"] = covid_data.groupby(
            ["Country/Region", "Province/State"]
        )["Confirmed Cases"].diff()
        covid_data["New Deaths"] = covid_data.groupby(
            ["Country/Region", "Province/State"]
        )["Deaths"].diff()

        # Handle negative values data correction
        covid_data["New Cases"] = covid_data["New Cases"].clip(lower=0)
        covid_data["New Deaths"] = covid_data["New Deaths"].clip(lower=0)

        # Calculate 7-day rolling averages
        covid_data["7_day Avg New Cases"] = (
            covid_data.groupby(["Country/Region", "Province/State"])["New Cases"]
            .rolling(7)
            .mean()
            .reset_index(level=0, drop=True)
        )
        covid_data["7_day Avg New Deaths"] = (
            covid_data.groupby(["Country/Region", "Province/State"])["New Deaths"]
            .rolling(7)
            .mean()
            .reset_index(level=0, drop=True)
        )

        return covid_data

    def add_population_metrics(self, covid_data):
        """Add per capita metrics"""
        # Meerg with population data
        covid_data = covid_data.merge(
            self.population, on=["Country/Region"], how="left"
        )

        # Calculate per capita metrics for 100K population
        covid_data["Cases per 100K"] = (
            convid_data["Confirmed Cases"] / convid_data["Population"] * 100000
        )

        covid_data["Deaths per 100K"] = (
            convid_data["Deaths"] / convid_data["Population"] * 100000
        )

        covid_data["fatality_rate"] = (
            covid_data["Deaths"] / covid_data["Confirmed Cases"] * 100
        )

        return covid_data

    def create_summary_stats(self, covid_data):
        """Create summary statistics for dashboard

        Args:
            covid_data (DataFrame): _description_
        """
        latest_date = covid_data["Date"].max()
        latest_data = covid_data[covid_data["Date"] == latest_date]

        global_summary = {
            "total_cases": latest_data["Confirmed Cases"].sum(),
            "total_deaths": latest_data["Deaths"].sum(),
            "countries_affected": latest_data["Country/Region"].nunique(),
            "latest_date": latest_date.strftime("%Y-%m-%d"),
            "global_cfr": latest_data["Deaths"].sum()
            / latest_data["confirmed_cases"].sum(),
        }

        return global_summary

    def save_processed_data(self, covid_data, summary_stats):
        """Save processed data and summary statistics to CSV files.

        Args:
            covid_data (DataFrame): _description_
            summary_stats (DictType): _description_
        """
        covid_data.to_csv("data/processed/covid_data.csv", index=False)

        import json

        with open("data/processed/summary_stats.json", "w") as f:
            json.dump(summary_stats, f, default=str)

        print("✓ Processed data and summary statistics saved successfully.")

    def process_all(self):
        """Run Complete Processing Pipeline"""

        print("Starting data processing...")
        print("Loading raw data....")
        self.load_raw_data()

        print("Transforming data...")
        covid_data = self.transform_data()

        print("Adding population metrics...")
        covid_data = self.add_population_metrics(covid_data)

        print("Creating summary statistics...")
        summary_stats = self.create_summary_stats(covid_data)

        print("Saving processed data...")
        self.save_processed_data(covid_data, summary_stats)

        return covid_data, summary_stats


if __name__ == "__main__":
    processor = COVIDDataProcessor()
    covid_data, summary_stats = processor.process_all()
    print("Data Processing Complete.")
    print(f"Convid data data frame shape{covid_data.shape}")
    print("Processed Data Sample:")
    print(covid_data.head())
    print("Summary Statistics:")
    print(summary_stats)
