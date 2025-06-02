#Collect the data in this script with various methods
import os
import requests
import pandas as pd
from datetime import datetime, timedelta

class COVIDDataCollector:
    def __init__(self):
        self.base_urls = {
            'jhu_cases':'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
            'jhu_deaths':'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
            'jhu_recovered':'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
        }
    
    def download_data(self, save_path='data/raw'):