# Collect the data in this script with various methods
import os
import pandas as pd
import requests
from datetime import datetime, timedelta


class COVIDDataCollector:
    def __init__(self):
        self.base_urls = {
            "jhu_cases": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
            "jhu_deaths": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
            "jhu_recovered": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
        }

    def download_data(self, save_path="data/raw"):
        """Download COVID-19 data from Johns Hopkins"""
        os.makedirs(save_path, exist_ok=True)

        for name, url in self.base_urls.items():
            try:
                print(f"Downloading {name} data...")
                df = pd.read_csv(url)
                filename = f"{name}.csv"
                df.to_csv(os.path.join(save_path, filename), index=False)
                print(f"✓Saved {name} data to {filename}")
            except Exception as e:
                print(f" ✗ Error downloading {name} data: {e}")

    def load_population_data(self):
        """Generate population data for per capita calculations"""

        population_data = {
            "US": 331900000,
            "India": 1380000000,
            "China": 1440000000,
            "Brazil": 213000000,
            "Russia": 146000000,
            "France": 67000000,
            "United Kingdom": 67000000,
            "Germany": 83000000,
            "Italy": 60000000,
            "Spain": 47000000,
        }

        pop_df = pd.DataFrame(
            list(population_data.items()), columns=["Country/Region", "Population"]
        )
        pop_df.to_csv("data/raw/population_data.csv", index=False)
        return pop_df


if __name__ == "__main__":
    collector = COVIDDataCollector()
    collector.download_data()
    collector.load_population_data()
    print("Data Collection Complete.")
