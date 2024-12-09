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
    server, engine = cd.connect_to_postgres(os.getenv("POSTGRES_PASSWORD"), host="postgres")

    try:
        # see if there is a city_ids table
        query = """
        SELECT * 
        FROM city_ids
        """
        pd.read_sql(query, con=engine)
    
    except:
        
        cities = list(cd.get_all_cities()['city'])
        print(cities)

        cities_and_ids = {"city": [],
                  "id": []}
        print("Getting all city names and ids")
        for c in cities:
            try:
                if c == "fauquier":
                    c = "front royal"
                if c == "jamescity":
                    c = "williamsburg"
                if c == "princewilliam":
                    c = "manassas"
                if c == "spotsylvania":
                    c = "fredericksburg"
                if c == "albemarle":
                    c = "charlottesville"


                if c == "beach":
                    c = "Virginia Beach"
                c = c + ", virginia"
                id = ca.get_station_id(c)
                cities_and_ids['city'].append(c)
                cities_and_ids['id'].append(id)

            except:
                continue
        final_df = pd.DataFrame.from_dict(cities_and_ids)
        cd.upload_cities_to_postgres(cities_and_ids, engine=engine)

        print("Getting all city data")
        counties = list(cities_and_ids['id'])
        city_df = pd.DataFrame()
        for c in cities:
            try:
                df = cd.get_data_for_city(c, years=["2009", "2023"])
                city_df = pd.concat([city_df, df], ignore_index=True)
            except:
                continue

        cd.upload_city_data_to_postgres(city_df, engine=engine)

        print("Getting all climate data")
        full_df = pd.DataFrame()
        for c in cities:
            try:
                if c == "fauquier":
                    c = "front royal"
                if c == "jamescity":
                    c = "williamsburg"
                if c == "princewilliam":
                    c = "manassas"
                if c == "spotsylvania":
                    c = "fredericksburg"
                if c == "albemarle":
                    c = "charlottesville"
                if c == "beach":
                    c = "Virginia Beach"
                c = c + ", virginia"
                print("Working on:", c)
                station_id = ca.get_station_id(c)
                climate_df = ca.get_data_for_station_id(station_id=station_id, start_date="1940-01-01", end_date="2023-12-31")
                full_df = pd.concat([full_df, climate_df], ignore_index=True)
            except:
                continue

        ca.upload_data_to_postgres(full_df, engine=engine)

        print("FINISHED UPLOADING EVERYTHING")

    


    
