from geopy.geocoders import Nominatim 
import requests
import json
import os
import numpy
import pandas as pd
import math

class ClimateAgent():

    def __init__(self):
        self.noaa_token = os.getenv("NCDC_TOKEN")

    def get_lat_long(self, location: str): 
        loc_agent = Nominatim(user_agent="Geopy Library")
        search = loc_agent.geocode(location)
        return search.latitude, search.longitude
    
    def get_bounding_box(self, latitude: float, longitude: float, buffer: int):
        """
            Need to get a north, east, south, and west coordinate for the bounding box parameters in order to 
            select an area in the NOAA api. 
        """
        # check to make sure the buffer is a valid size
        if buffer > 100 or buffer < 0:
            raise Exception("Buffer needs to be in between 0 and 100 as an integer")
        
        if buffer is None: 
            raise Exception("Buffer cannot be none")

        # check to make sure that the latitude and longitude are valid coordinates
        if latitude > 90.0 or latitude < -90.0:
            raise Exception("Latitude is outside of the valid bounds")

        if longitude > 180.0 or longitude < -180.0:
            raise Exception("Longitude is outside the valid bounds")
        
        mile_offset = 69 # 69 miles per degree offset

        latitude_offset = buffer / mile_offset # ChatGPT
        longitude_offset = buffer / (mile_offset * math.cos(math.radians(latitude))) # ChatGPT calc
        
        north = round((latitude + latitude_offset), 3)
        south = round((latitude - latitude_offset), 3)
        east = round((longitude + longitude_offset), 3)
        west = round((longitude - longitude_offset), 3)

        bounding_box = (north, west, south, east)
        return bounding_box
         

    def get_useragent(self):
        url = "https://httpbin.org/user-agent"
        r = requests.get(url)
        useragent = json.loads(r.text)['user-agent']
        return useragent

    def make_headers(self, email='jcm4bsq@virginia.edu'):
        useragent = self.get_useragent()
        headers = {
            'User-Agent': useragent,
            'From': email
        }
        return headers
    
    def get_station_id(self, city:str):
        """
            Let's figure out how to grab a station ID from this dataset
        """
        base = "https://www.ncei.noaa.gov/access/services/search/v1/data"
        lat, long = self.get_lat_long(city)
        bb = self.get_bounding_box(lat, long, buffer=10)
        headers = self.make_headers()
        bounding_box = f"{bb[0]},{bb[1]},{bb[2]},{bb[3]}"
        params = {"dataset":"global-summary-of-the-month",
                  "bbox": bounding_box,
                  "dataTypes": "TMIN,TMAX,PRCP",
                  "startDate": "2022-01-01",
                  "endDate": "2022-02-01"}
        
        r = requests.get(base, params=params, headers=headers)
        list_of_stations = json.loads(r.text)['results']
        name_of_station = list_of_stations[0]['stations'][0]['name']
        station_id = list_of_stations[0]['stations'][0]['id']

        return station_id
    

    def get_data_for_station_id(self, station_id, start_date, end_date):
        """
            purpose: grab data from the ncei datasets to populate the database 
        """
        base = "https://www.ncei.noaa.gov/access/services/data/v1"
        headers = self.make_headers()
        params = {"dataset":"daily-summaries",
          "dataTypes": "TMIN,TMAX,PRCP", 
          "startDate": start_date,
          "endDate": end_date,
          "stations": station_id}
        r = requests.get(base, params=params, headers=headers)
        return r.text




        
        
    
