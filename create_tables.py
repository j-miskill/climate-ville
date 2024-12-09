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
import time

if __name__ == "__main__":
    time.sleep(10) # give postgres a second to boot up
    ca = climate.ClimateAgent()
    cd = census.CensusData()
    pw = os.getenv("POSTGRES_PASSWORD")
    server, engine = cd.connect_to_postgres(os.getenv("POSTGRES_PASSWORD"), host='postgres')

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
        cities_and_ids = cities_and_ids.drop("Unnamed: 0", axis=1)
        cities = list(cities_and_ids['city'])
        station_ids = list(cities_and_ids['id'])
        cd.upload_cities_to_postgres(cities_and_ids, engine=engine)

        # load in the city data from the csv
        city_data = pd.read_csv("data/city-data.csv")
        city_data = city_data.drop("Unnamed: 0", axis=1)
        cd.upload_city_data_to_postgres(city_data=city_data, engine=engine)


        # load in the climate data from the csv
        climate_data = pd.read_csv("data/climate-data.csv")
        climate_data = climate_data.rename(columns={
            "DATE": "date",
            "STATION": "id",
            "TMAX": "tmax",
            "TMIN": "tmin",
            "PRCP": "prcp"

        })
        climate_data = climate_data.drop("Unnamed: 0", axis = 1)
        ca.upload_data_to_postgres(climate_data=climate_data, engine=engine)


    


    
