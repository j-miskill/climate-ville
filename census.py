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
        self.base_url = "https://api.census.gov/data/"
        # https://api.census.gov/data/{YEAR}/{DATASET}?get={VARIABLES}&for={GEO_TYPE}:{GEO_ID}&key={API_KEY}
        # let's try to get 10 metrics that would be worthwhile to explore!
        self.metrics = {
            "poverty": "DP03_0119PE",
            "male_income": "DP03_0093E",
            "female_income": "DP03_0094E"
        }

    def find_city_id(self, city:str):
        tmp_url = self.base_url + "2022/acs/acs1/profile"
        params = {"key": os.getenv("CENSUS_KEY"),
                  "get": "NAME",
                  "for": "county:*",
                  "in": "state:51"
                  }
        
        r = requests.get(tmp_url, params=params)
        try:
            values = list(json.loads(r.text))
            df = pd.DataFrame(values[1:], columns=values[0])
            df['NAME'] = df['NAME'].str.lower()
            df['NAME'] = df['NAME'].str.replace(" ", "")
            city = city.lower()
            record_looking_for = df[df['NAME'].str.contains(city)]
            if record_looking_for is not None:
                return record_looking_for['county'].item()
        except Exception:
            raise Exception("URL ERROR, MAKE SURE IT IS CORRECTLY CONFIGURED")
        


    def get_data_for_city(self, city:str, data_selections: str):
        city_id = self.find_city_id(city)

        data_selections = data_selections.replace(" ", "")

        get_metrics = ""
        items = data_selections.split(",")

        get_metrics += self.metrics[items[0]] + ","
        for i in range(1, len(items)):
            item = items[i]
            m = self.metrics[item]
            print(m)
            get_metrics += m + ","
        
        get_metrics += "NAME"

        tmp_url = self.base_url + "2022/acs/acs1/profile"
        params = {"key": os.getenv("CENSUS_KEY"),
                  "get": get_metrics,
                  "for": f"county:{city_id}",
                  "in": "state:51"}
        
        r = list(json.loads(requests.get(tmp_url, params=params).text))
        return pd.DataFrame(r[1:], columns=r[0])
    

    def upload_data_to_postgres(self, data):
        pass

    def connect_to_postgres(self):
        pass

    
    



    
    





    