import re
from ukcp_api_client.client import UKCPApiClient
import spacy
import requests
import helpers
import pyproj
import pandas as pd
import numpy as np
import netCDF4
from variable_specification import values,labels
import copy
import pickle
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


def extract_place_name(query):
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
    return place_name



def evaluate_helper_function(param_value,final_value):
    param_function = param_value.split("/")[-1].split("?")[0]
    params_req  = param_value.split("/")[-1].split("?")[1].split("&")
    function_params = {}
    result = None
    for i in params_req:
        extracted_param = str(i.split("=")[0]).lower()
        extracted_param_value = final_value[extracted_param]
        function_params[extracted_param] = extracted_param_value
    if hasattr(helpers,param_function):
        function_call = getattr(helpers,param_function)
        result = function_call(**function_params)
    return result[1]

def search_or_ask(query,value,key,variable_map):
    found = False
    found_value = None
    for j in value:
        pattern = r'\b{}\b'.format(re.escape(j))
        match = re.search(pattern,query)
        if match:
            found_value = match.group(0)
            found = True
            break
    if not found:
        if key == "variable":
            variable_values = "\n".join([variable_map[i] for i in value])
            param = str(input("Please provide the value of {0} param possible values are {1}".format(key,variable_values)))
        else:
            param = str(input("Please provide the value of {0} param possible values are {1}".format(key,value)))
        found_value = param
    return found_value

def param_search(possible_values,query):
    final_values = {}
    helper_values = []
    variable_map = {values[i]:labels[i] for i in range(len(values))}
    for i in possible_values.keys():
        value = possible_values[i].split(',')
        if(str(i).startswith("area.type")):
            final_values[i] = value[0]
            continue
        if(str(i).startswith("dataformat")):
            final_values[i] = "csv"
            continue

        if (len(value) == 1 and str(value[0]).startswith("__LOCAL")):
            helper_values.append({i:value[0]})
        elif len(value) == 1:
            final_values[i] = value[0]
        else:
            final_values[i] = search_or_ask(query,value,i,variable_map)
    for k in helper_values:
        function_values = evaluate_helper_function(list(k.values())[0],final_values)
        if isinstance(function_values,list):
            final_values[list(k.keys())[0]] = search_or_ask(query,function_values,list(k.keys())[0],variable_map)
        else:
            final_values[list(k.keys())[0]] = function_values
    if("timeslice" not in final_values.keys()):
        i1 = str(input("Enter the lower year range "))
        i2 = str(input("Enter the upper year range "))
        final_values["timeslice"] = i1+"|"+i2
    return final_values

def add_area_to_params(param,eastings,northings):
    queries = []
    param2 = copy.deepcopy(param)
    E1,E2 = eastings
    N1,N2 = northings
    resolution = param["resolution"]
    resolution_file_mapping = {
        '60':'tas_hadukgrid_uk_60km_ann_202201-202212.nc',
        '25':'tas_hadukgrid_uk_25km_ann_202101-202112.nc',
        '12':'tas_hadukgrid_uk_12km_ann_202201-202212.nc',
        '5':'tas_hadukgrid_uk_5km_ann_202101-202112.nc'
    }
    dataset = netCDF4.Dataset(resolution_file_mapping[resolution],'r')
    Eastings = np.array(dataset.variables["projection_x_coordinate"][:])
    Northings = np.array(dataset.variables["projection_y_coordinate"][:])
    areatype = str(param["area.type"])
    e1diff = abs(Eastings - E1)
    e2diff = abs(Eastings - E2)
    n1diff = abs(Northings - N1)
    n2diff = abs(Northings - N2)
    e1 = Eastings[np.where(e1diff==np.min(e1diff))]
    e2 = Eastings[np.where(e2diff==np.min(e2diff))]
    if e1 == e2:
        index = np.where(e2diff==np.min(e2diff))[0]
        e2 = Eastings[index+1]
    n1 = Northings[np.where(n1diff==np.min(n1diff))]
    n2 = Northings[np.where(n2diff==np.min(n2diff))]
    if n1 == n2:
        index = np.where(n2diff==np.min(n2diff))[0]
        n2 = Northings[index+1]
    print(e1,e2)
    print(n1,n2)
    if areatype.startswith("bbox"):
        param["area"] = "bbox|"+str(e1[0])+"|"+str(e2[0])+"|"+str(n1[0])+"|"+str(n2[0])
        queries.append(param)
    else:
        param["area"] = "point|"+str(e1[0])+"|"+str(n1[0])
        queries.append(param)
        param2["area"] = "point|"+str(e2[0])+"|"+str(n2[0])
        queries.append(param2)

    return queries


def make_api_call(querystring,filenames):
    for i,j in enumerate(querystring):
        api_key = ""
        cli = UKCPApiClient(outputs_dir="my-outputs", api_key=api_key)
        filename = filenames[i].split("_")
        filename_created = filename[0].upper()+"_"+str(filename[1]).capitalize()+"_"+filename[-1]
        print(filename_created)
        request_url = "https://ukclimateprojections-ui.metoffice.gov.uk/wps?service=WPS&request=Execute&version=1.0.0&Identifier={0}&Format=text/xml&Inform=true&Store=false&Status=false&DataInputs={1}".format(filename_created,j[:len(j)-1])
        file_urls = cli.submit(request_url)
    return None

def make_datainputs_string(params):
    key_api_mapping = {
        'climatechangetype':'ClimateChangeType',
        'temporalaverage':'TemporalAverage',
        'dataformat':'DataFormat',
        'ensemblememberset':'EnsembleMemberSet',
        'timeslice':'TimeSlice',
        'returnperiod':'ReturnPeriod'
    }
    not_req = ["Area.type","Filename","Resolution"]
    keys = [key_api_mapping[i] if i in key_api_mapping.keys() else i.capitalize() for i in params.keys()]
    keys_final = [i for i in keys if i not in not_req]
    querystring = ""
    for i in keys_final:
        querystring += i+"="+params[i.lower()]+";"
    return querystring

def extract_entities(query):
    variable_requirements = None
    with open("variable_requirements.pkl",'rb') as file:
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
        '12-notdaily-notderived':'ls3b_subset_01',
        '12-daily-notderived':'ls3b_subset_02',
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
    resolution = re.search(r"60|25|12|2.2|historic",query)
    chosen_file = None
    if not resolution:
        resolution = input("Please provide a resolution options : 60,25,12,2.2km or historic")
    if resolution.startswith('60'):
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
    elif resolution.startswith('25'):
        chosen_file = exact_mapping["25-notdaily-notderived"]

    elif resolution.startswith('2.2'):
        time_resolution_search = re.search(r'daily|Daily|hourly|Hourly',query)
        if time_resolution_search:
            print(time_resolution_search)
            chosen_file = exact_mapping["2.2-"+time_resolution_search.group(0)+"-notderived"]
        else:
            chosen_file = exact_mapping["2.2-notdaily-notderived"]
    elif resolution.startswith('12'):
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
    params = param_search(file_final,query)
    queries = add_area_to_params(params,(E1,E2),(N1,N2))
    querystrings = []
    filenames = []
    for i in queries:
        querystrings.append(make_datainputs_string(i))
        filenames.append(i["filename"])
    print(filenames)
    make_api_call(querystrings,filenames)
    return querystrings,filenames
