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
import census
import climate

if __name__ == "__main__":
    ca = climate.ClimateAgent()
    cd = census.CensusData()
    pw = os.getenv("POSTGRES_PASSWORD")
    server, engine = cd.connect_to_postgres(os.getenv("POSTGRES_PASSWORD"))

    try:
        # see if there is a city_ids table
        query = """
        SELECT * 
        FROM city_ids
        """
        pd.read_sql(query, con=engine)
    
    except:
        print("STARTING TABLE CREATION")
        cities_and_ids = pd.read_csv("data/city-ids.csv")
        cities = list(cities_and_ids['city'])
        station_ids = list(cities_and_ids['id'])
        cd.upload_cities_to_postgres(cities_and_ids, engine=engine)

        print("Getting all city data")
        counties = list(cities_and_ids['id'])
        city_df = pd.DataFrame()
        for c in cities:
            try:
                df = cd.get_data_for_city(c, years=[2009, 2023])
                city_df = pd.concat([city_df, df], ignore_index=True)
            except:
                continue
        print(city_df)
        cd.upload_city_data_to_postgres(city_df, engine=engine)

        print("Getting all climate data")
        full_df = pd.DataFrame()
        for station_id in cities:
            try:
                climate_df = ca.get_data_for_station_id(station_id=station_id, start_date="1940-01-01", end_date="2023-12-31")
                full_df = pd.concat([full_df, climate_df], ignore_index=True)
            except:
                continue

        ca.upload_data_to_postgres(full_df, engine=engine)

        print("FINISHED TABLE CREATION")

    


    
