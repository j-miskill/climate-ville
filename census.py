"""
    A class to connect to the census API and extract data as needed
"""

import pandas as pd
import numpy as np
import os
import requests
import json

class CensusData:

    def __init__(self):
        self.base_url = "https://api.census.gov/data"

    def access_economic_data(self, city:str, years:list):
        endpoint = "/" + str(years[0]) + "/" + "ecnbasic"
        params = {'key': os.getenv("CENSUS_KEY")}
        print(self.base_url + endpoint)
        r = requests.get(self.base_url + endpoint)
        return r.text





    