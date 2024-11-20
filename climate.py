from geopy.geocoders import Nominatim 
import requests
import json
import os

class ClimateAgent():

    def __init__(self):
        self.base_noaa_url = "https://www.ncei.noaa.gov/access/services/search/v1/"
        

    def get_lat_long(self, location: str): 
        loc_agent = Nominatim(user_agent="Geopy Library")
        search = loc_agent.geocode(location)
        return search.latitude, search.longitude
    
    def get_bounding_parameters(self, latitude: float, longitude: float):
        
        pass

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
    
