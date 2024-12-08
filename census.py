"""
    A class to connect to the census API and extract data as needed
"""

import pandas as pd
import numpy as np
import os
import requests
import json
import psycopg  # postgres adapter
from sqlalchemy import create_engine  # shortcut tool to connect database to pandas
from bs4 import BeautifulSoup
import pymongo
from bson.json_util import dumps, loads
from plotly import express as px

class CensusData:

    def __init__(self):
        self.base_url = "https://api.census.gov/data/"
        # https://api.census.gov/data/{YEAR}/{DATASET}?get={VARIABLES}&for={GEO_TYPE}:{GEO_ID}&key={API_KEY}
        # let's try to get 10 metrics that would be worthwhile to explore!
        self.list_of_metrics = {"NAME":"city","DP03_0093E":"male_worker_earnings","DP03_0094E":"female_worker_earnings",
                                "DP03_0119PE":"pct_below_pov","DP04_0001E":"num_housing_units",
                                "DP02_0002E":"num_married_housing_units","DP02_0016E":"avg_household_size",
                                "DP03_0052E": "lt_10k_income","DP03_0053E": "gt_10k_lt_15k_income",
                                "DP03_0054E": "gt_15k_lt_25k_income", "DP03_0055E":"gt_25k_lt_35k_income",
                                "DP03_0056E": "gt_35k_lt_45k_income", "DP03_0057E": "gt_50k_lt_75k_income",
                                "DP03_0058E": "gt_75k_lt_100k_income", "DP03_0059E": "gt_100k_lt_150k_income",
                                "DP03_0060E": "gt_150k_lt_200k_income", "DP03_0061E": "gt_200k_income",
                                "DP02_0026E": "men_not_married", "DP02_0028E": "married_but_separated", "DP02_0030E": "divorced",
                                "DP02_0054E": "est_in_preschool", "DP02_0055E": "est_in_kindergarten",
                                "DP02_0056E": "est_in_1_8", "DP02_0057E": "est_in_9_12", "DP02_0058E": "est_in_college",
                                "DP02_0060PE": "pct_lt_ninth_grade", "DP02_0061PE": "pct_some_high_school", "DP02_0062PE": "pct_high_school",
                                "DP02_0063PE": "pct_some_college", "DP02_0064PE": "pct_associates", "DP02_0065PE": "pct_bachelors",
                                "DP02_0066PE": "pct_graduate", "DP03_0009PE": "unemployment_rate", "DP03_0033PE": "pct_in_ag_ind",
                                "DP03_0034PE": "pct_in_construction", "DP03_0035PE": "pct_in_manufacturing", "DP03_0036PE": "pct_in_wholesale_trade",
                                "DP03_0037PE": "pct_in_retail", "DP03_0038PE": "pct_in_transportation", "DP03_0039PE": "pct_in_information",
                                "DP03_0040PE" : "pct_in_finance", "DP03_0041PE": "pct_in_science", "DP03_0042PE": "pct_in_education",
                                "DP03_0043PE": "pct_in_arts", "DP03_0045PE": "pct_in_pub_ad"
                                }
        
    def get_all_cities(self):
        tmp_url = self.base_url + "2023/acs/acs1/profile"
        params = {"key": os.getenv("CENSUS_KEY"),
                  "get": "NAME",
                  "for": "county:*",
                  "in": "state:51"
                  }
        r = requests.get(tmp_url, params=params)
        values = list(json.loads(r.text))
        df = pd.DataFrame(values[1:], columns=values[0])
        df = df.rename(columns={"NAME": "city"})
        df['city'] = df['city'].str.replace("city", "")
        df['city'] = df['city'].str.replace("County", "")
        df['city'] = df['city'].str.lower()
        df['city'] = df['city'].str.replace(" ", "")
        df['city'] = df['city'].str.replace(",", "")
        df['city'] = df['city'].str.replace("virginia", "")
        return df

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
        


    def get_data_for_city(self, city:str, years=list, county=None):
        if county is None:
            city_id = self.find_city_id(city)
        else:
            city_id = county
       
        
        get_metrics = "".join(x + "," for x in self.list_of_metrics.keys())
        get_metrics = get_metrics[:len(get_metrics)-1] # get rid of the last comma that I appended

        final_df = pd.DataFrame()
        for y in range(years[0], years[1]):
    
            tmp_url = self.base_url + f"{y}/acs/acs1/profile"
            # "key": os.getenv("CENSUS_KEY")
            params = {
                    "get": get_metrics,
                    "for": f"county:{city_id}",
                    "in": "state:51"}
            try:
                r = requests.get(tmp_url, params=params).text
                r2 = list(json.loads(r))
                df = pd.DataFrame(r2[1:], columns=r2[0])
                df['year'] = y
                df = df.rename(columns=self.list_of_metrics)
                final_df = pd.concat([final_df, df], ignore_index=True)
            except:
                if "HTTP Status 404" in r:
                    print("404 Error")
                else:
                    print(r)

        # rearranging some stuff for the final df
        last_col = final_df.columns[-1]
        final_df_last_col = final_df.drop(columns=[last_col])
        final_df_last_col.insert(1, last_col, final_df[last_col])
        final_df_last_col['city'] = final_df_last_col['city'].str.replace("city", "")
        final_df_last_col['city'] = final_df_last_col['city'].str.replace("County", "")
        final_df_last_col['city'] = final_df_last_col['city'].str.lower()
        final_df_last_col['city'] = final_df_last_col['city'].str.replace(" ", "")
        final_df_last_col['city'] = final_df_last_col['city'].str.replace(",", "")
        final_df_last_col['city'] = final_df_last_col['city'].str.replace("virginia", "")
        return final_df_last_col
    
    def upload_cities_to_postgres(self, city: pd.DataFrame, engine):
        print("Uploading region information to database")
        city.to_sql("cities", con=engine, index=False, chunksize=1000, if_exists="replace")
        print("Finished uploading to database")

    def upload_city_data_to_postgres(self, city_data, engine):
        print("Uploading city data to the database")
        try:
            existing_data = pd.read_sql('SELECT city, year FROM city_data', engine)
            new_rows = city_data.merge(existing_data, on=['city', 'year'], how='left')
            new_rows = new_rows[new_rows['_merge'] == 'left_only']
            new_rows.to_sql("city_data", con=engine, index=False, chunksize=1000, if_exists="append")
        except:
            print("city_data table does not exist yet, creating now with first command")
            city_data.to_sql("city_data", con=engine, index=False, chunksize=1000, if_exists="replace")
        print("Finished uploading city data to database")


    def connect_to_postgres(self, password, user='postgres', host='localhost', port='5432', create=False):
        dbserver = psycopg.connect(user=user, password=password, host=host, port=port)
        dbserver.autocommit = True
        if create:
            # cursor is the location for writing code to run on the server
            cursor = dbserver.cursor()
            cursor.execute("DROP DATABASE IF EXISTS climate")
            cursor.execute("CREATE DATABASE climate")
        
        engine = create_engine(f"postgresql+psycopg://{user}:{password}@{host}:{port}/climate")
        return dbserver, engine
    
    def query_city_data(self, city:str, engine):
        my_query = f"""
        SELECT *
        FROM city_data
        WHERE city LIKE '{city}'
        """
        df = pd.read_sql_query(my_query, con=engine)
        return df

    


    



    
    





    