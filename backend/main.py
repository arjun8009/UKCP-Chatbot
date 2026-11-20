from database_helpers import *
import re
import pyproj
import pickle
import requests
import pandas as pd
import pickle
from query_helpers import *
from get_llm_RAG_response import tool_rag_data_response
from openai import OpenAI
from pydantic import BaseModel, Field
import os
os.environ["OPENAI_API_KEY"] = ''


def get_lat_long_range(place_name):
        # Input is a comma separated location
        places = place_name.split(',')
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        if len(places)==1:
            # Define the Nominatim API endpoint
            # Make a request to the Nominatim API
            params = {
                "q": place_name,
                "format": "json",
                "countrycodes": "gb",
                "limit": 1  # Limit the results to one place
            }
            headers = {
                "User-Agent": "Your User Agent"
            }
            response = requests.get(nominatim_url, params=params, headers=headers)
            # Parse the JSON response
            data = response.json()

            # Extract the bounding box coordinates if available
            if data:
                place = data[0]
                if "boundingbox" in place:
                    bounding_box = place["boundingbox"]
                    south, north, west, east = map(float, bounding_box)
                    print(f"South: {south}, North: {north}, West: {west}, East: {east}")
                else:
                    print("Bounding box not available for this place.")
            else:
                print("No results found for the specified place.")
            southwest = (south, west)
            northeast = (north, east)
            return southwest,northeast
        else:
            south = 90.0
            west = 180.0
            north = -90.0
            east = -180.0
            for place_name in places:
                # Make a request to the Nominatim API for each place
                params = {
                    "q": place_name,
                    "format": "json",
                    "countrycodes": "gb",
                    "limit": 1  # Limit the results to one place
                }

                response = requests.get(nominatim_url, params=params)
                data = response.json()

            # Extract the bounding box coordinates if available
                if data:
                    place = data[0]
                    if "boundingbox" in place:
                        bbox = place["boundingbox"]
                        south = min(south, float(bbox[0]))
                        north = max(north, float(bbox[1]))
                        west = min(west, float(bbox[2]))
                        east = max(east, float(bbox[3]))

        # Extract the final combined bounding box coordinates
        southwest = (south, west)
        northeast = (north, east)
        return southwest,northeast

class IdentifyLocation(BaseModel):
    location : str = Field(description="The location mentioned in the query. With 2 constrains : 1. It should be a location in UK and 2. It can be queried by openstreet map. Otherwise return None or empty")

    
def identify_location_in_query(query):

    prompt = """You are a location identifier. Your task is to identify the location in query. \
            Hereby United Kingdom is reffered to as UK .Given the query do the following steps: \
            1. Read the query \
            2. Identify the location in the query which can be a city,county, country (which needs to be limited to the UK) and abstract region refferences like SW UK or East Devon \
            3. Constraint : Extracted city,county,country and region in any field and for any query must be located in the United Kingdom. Otherwise it will be invalid. \
            4. If the location is not valid then return empty or None. """

    messages = [{"role":"system","content":prompt},{"role":"user","content": query}]
    client = OpenAI()
    output = client.beta.chat.completions.parse(model = "gpt-4o-mini",messages=messages,temperature=0,response_format=IdentifyLocation)
    return output


def extract_locations(query):
    # Get every word in the query
    locations = identify_location_in_query(query)
    # Parse the structured output
    parsed_locations = locations.choices[0].message.parsed
    print("Extracted Locations:", parsed_locations)
    # get corresponding location data
    place_name = parsed_locations.location
    if not place_name:
        return None,None,None
    print("Formulated Place Name:", place_name)
    SW,NE = get_lat_long_range(place_name)
    return place_name,SW,NE




# The Aim of this function is to get the UKCP file name connected to the product. Each filename is dependent on the resolution and 
# the mapping can be seen below. Once the filename and the resolution is derived then the parameters for the query can be extracted.
def file_localization(query):
    query = query.lower()
    print(query)
    variable_requirements = None
    with open(os.path.join(os.getcwd(),"backend","variable_requirements.pkl"),'rb') as file:
        variable_requirements = pickle.load(file)
    query = query.lower()
    locations,SW,NE = extract_locations(query)
    lat1 = SW[0]
    long1 = SW[1]
    lat2 = NE[0]
    long2 = NE[1]
    latitude = [lat1, lat1, lat2, lat2]
    longitude = [long1, long2, long1, long2]
    projection_params = {
        'proj': 'tmerc',
        'lat_0': 49.0,  # Latitude of the origin
        'lon_0': -2.0,  # Longitude of the central meridian
        'k_0': 0.9996012771,  # Scale factor
        'x_0': 400000.0,  # False easting
        'y_0': -100000.0  # False northing
    }
    exact_mapping = {
        '60-notdaily-derived' : 'ds5_subset_01',
        '60-daily-derived':'ds5_subset_02',
        '25-notdaily-notderived':'ls1_subset_02',
        '60-notdaily-notderived':'ls2_subset_01',
        '60-daily-notderived':'ls2_subset_02',
        '2.2-notdaily-notderived':'ls3a_subset_01',
        '2.2-daily-notderived':'ls3a_subset_02',
        '2.2-hourly-notderived':'ls3a_subset_03',
        '12-notdaily-notderived':'ls3_subset_01',
        '12-daily-notderived':'ls3_subset_02',
        '12-notdaily-globalwarming':'ls3_subset_01',
        '12-daily-globalwarming':'ls3_subset_02',
        'historic-notdaily-notderived':'ls6_subset_01',
        'historic-daily-notderived':'ls6_subset_02'
    }
    

    tm_projection = pyproj.Proj(projection_params)
    E1, N1 =  pyproj.transform(pyproj.Proj(proj='latlong'), tm_projection, long1, lat1)
    E2, N2 =  pyproj.transform(pyproj.Proj(proj='latlong'), tm_projection, long2, lat2)
    E1 = round(E1)
    E2 = round(E2)
    N1 = round(N1)
    N2 = round(N2)
    print("Eastings Range : {0} to {1}".format(E1, E2))
    print("Northings Range : {0} to {1}".format(N1, N2))
    # Search if the resolution is in the query. Also if the resolution is mentioned then check for things like derived or daily
    resolution = re.search(r"\b(?:60|25|12|2\.2|5|historic)(?:\s?km)?\b", query, re.IGNORECASE)
    chosen_file = None
    if not resolution:
        return (None,E1,E2,N1,N2)
    if str(resolution.group(0)).startswith('60'):
        time_resolution_search = re.search(r'daily|Daily',query)
        derived_search = re.search(r'derived|Derived',query)
        if time_resolution_search:
            if derived_search:
                chosen_file = exact_mapping["60-daily-derived"]
            else:
                chosen_file = exact_mapping["60-daily-notderived"]
        else:
            if derived_search:
                chosen_file = exact_mapping["60-notdaily-derived"]
            else:
                chosen_file = exact_mapping["60-notdaily-notderived"]
    elif str(resolution.group(0)).startswith('25'):
        chosen_file = exact_mapping["25-notdaily-notderived"]

    elif (str(resolution.group(0)).startswith('2.2') or str(resolution.group(0)).startswith('5')):
        time_resolution_search = re.search(r'daily|Daily|hourly|Hourly',query)
        if time_resolution_search:
            print(time_resolution_search)
            chosen_file = exact_mapping["2.2-"+time_resolution_search.group(0)+"-notderived"]
        else:
            chosen_file = exact_mapping["2.2-notdaily-notderived"]
    elif str(resolution.group(0)).startswith('12'):
        time_resolution_search = re.search(r'daily|Daily',query)
        globalwarming_search = re.search(r'global warming|global warming',query)
        if time_resolution_search:
            if globalwarming_search:
                chosen_file = exact_mapping["12-daily-globalwarming"]
            else:
                chosen_file = exact_mapping["12-daily-notderived"]
        else:
            if globalwarming_search:
                chosen_file = exact_mapping["12-notdaily-globalwarming"]
            else:
                chosen_file = exact_mapping["12-notdaily-notderived"]
    else:
        time_resolution_search = re.search(r'daily|Daily',query)
        if time_resolution_search:
            chosen_file = exact_mapping["historic-daily-notderived"]
        else:
            chosen_file = exact_mapping["historic-notdaily-notderived"]
    file_final = [i for i in variable_requirements if i["filename"] == chosen_file][0]
    print(file_final)
    return (file_final,E1,E2,N1,N2)


