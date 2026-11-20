from flask import jsonify
from flask_cors import CORS
import pandas as pd
import sqlite3
import gunicorn
from sqlalchemy import create_engine
import psycopg2
import os
import pickle
from ukcpapidata import extract_place_name, extract_locations
import  ukcp_api_client 
import helpers
from variable_specification import values,labels
from ukcp_api_client.client import UKCPApiClient
import numpy as np 
import pandas as pd
import netCDF4
import re
import zipfile
import unicodedata
from github import Github
from variable_selection import user_prompt,system_instruction
import json
import openai
import traceback
import copy
from pydantic import BaseModel,Field
import boto3
from database_helpers import *
import shutil
os.environ["OPENAI_API_KEY"] = "" ""


def preprocess_api_data(response,excerpts):
    return jsonify([{'role':'assistant','content':response},
                    {'role':'user','sources':excerpts}])

def preprocess_zip_data(response,excerpts,llm_extraction=False):
    return jsonify([{'role':'assistant','content':response,'Data':True,'llm_extraction':llm_extraction},
                    {'role':'user','sources':excerpts}])


def evaluate_helper_function(param_value,final_value):
    param_function = param_value.split("/")[-1].split("?")[0]
    params_req  = param_value.split("/")[-1].split("?")[1].split("&")
    print("param function",param_function)
    print("params req", params_req)
    function_params = {}
    result = None
    for i in params_req:
        extracted_param = str(i.split("=")[0]).lower()
        if extracted_param == "ensemble":
            extracted_param = "ensemblememberset"
        extracted_param_value = final_value[extracted_param]
        function_params[extracted_param] = extracted_param_value
    print("function params",function_params)
    if hasattr(helpers,param_function):
        function_call = getattr(helpers,param_function)
        result = function_call(**function_params)
    return result[1]


def get_or_set_openai_api_key():
    '''
    This function will check if the openai api key is set in the secrets.json file. If not, it will ask the user to enter the api key.
    '''
    import json
    if os.path.exists("apikey.json"):
        with open("apikey.json") as f:
            secrets = json.load(f)

    openai_api_key = secrets['api_key']

    os.environ["OPENAI_API_KEY"] = "" ""
    return None


class TimesliceSchema(BaseModel):
    timeslice : str = Field(description="Timeslice of the format start year|end year eg 1981|2019 or None if no information is given. Format is very important")

def process_timeslice(query,response):

    prompt = """You will be given a question that was asked to the user and the users response \
                1. The question asks the users to choose a range of time slice. \
                2. The timeslice can be a range of a set of choices all given in the question \
                3. Now based on the users response. The actual timeslice needs to be start year|end year \
                4. For example if the user says "I want the range between 1982 to 2040" then timeslice is 1982|2040 \
                5. Again if the question says that only 3 timeslices are possible then choose the closest timeslice based on the user response.  \
                6. If the response does not contain any information return None
                7. This information will go to an API calls which is very specific. The format needs to be correct. startyear|endyear."""
    
    messages = [{"role":"system","content":prompt},
                {"role":"user","content":f"The question asked is {query} and user response is {response}"}]
    
    client = openai.OpenAI()
    response = client.beta.chat.completions.parse(model="gpt-4o-mini",
                                                  temperature=0, messages=messages,response_format=TimesliceSchema)
    return response.choices[0].message.parsed


class Matches(BaseModel):
    keys : list[str] = Field(description="key for a single match or keys for multiple matches or None for no matches")
    values: list[str] = Field(description="value for a single match or values for multiple matches or None for no matches")

def search_ask_llm(query,datadict):
    global user_prompt
    chat_history = []
    chat_history.append({"role": "system", "content": system_instruction})
    user_prompt_dup = user_prompt
    user_prompt = user_prompt.replace("<Question>", query)
    user_prompt = user_prompt.replace("<DataDicitionary>", datadict)
    chat_history.append({"role": "user", "content": user_prompt})
    user_prompt = user_prompt_dup
    client = openai.OpenAI()
    response = client.beta.chat.completions.parse(
        model='gpt-4o',
        messages=chat_history,
        temperature=0,
        response_format=Matches
    )
    response_message = response.choices[0].message.parsed
    keys = response_message.keys
    values = response_message.values
    return keys,values

def search_or_ask(query,value,datadict):
    try:
        print("llm ask",query,value,str(datadict))
        get_or_set_openai_api_key()
        keys,values = search_ask_llm(query,datadict)
        print("llm choice",keys)
        if keys[0]!="None" or keys[0] is not None or keys[0]!="NONE":   
            return keys
        else:
            return None
    except Exception as e:
        print("normal choice",e)
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
            return None
        return found_value



def param_search(possible_values,email):
    universal_dict = {}
    path = os.path.join(os.getcwd(), "universal_explanation_dict.pkl") 
    with open(path,"rb") as file:
        universal_dict = pickle.load(file)
    path = os.path.join(os.getcwd(), "data_state")
    final_values = None
    if count_final_values(email)!=0:
        final_values = extract_final_values(email)
    else:
        final_values = {}  
    print("final_values",final_values)
    helper_values = []
    variable_map = {values[i]:labels[i] for i in range(len(values))}
    for i in possible_values.keys():
        value = possible_values[i].split(',')
        data_dict = {i:universal_dict[i] if i in universal_dict else i for i in value}
        if(str(i).startswith("area")):
            final_values[i] = value[0]
            continue

        if(str(i).startswith("dataf")):
            final_values[i] = "netcdf"
            continue

        if(str(i).startswith("resol")):
            final_values[i] = possible_values["resolution"]
            continue

        if(str(i).startswith("filename")):
            final_values[i] = " "
            continue

        if (len(value) == 1 and str(value[0]).startswith("__LOCAL")):
            helper_values.append({i:value[0]})
            continue
        elif len(value) == 1:
            print("In one",value,i)
            final_values[i] = value[0]
            continue
        else:
            update_final_values(final_values,email)
            return i,value
    
    helper_value_keys = [str(list(j.keys())[0]) for j in helper_values]
    print(helper_value_keys)
    if "variable" not in helper_value_keys:
        for k in helper_values:
            function_values = evaluate_helper_function(list(k.values())[0],final_values)
            existing_filenames = extract_filenames(email)
            existing_filenames[list(k.keys())[0]] = ",".join(function_values) if isinstance(function_values,list) else function_values
            update_filenames(existing_filenames,email)
            if isinstance(function_values,list):
                data_dict = {i:universal_dict[i] if i in universal_dict else i for i in function_values}
                update_final_values(final_values,email)
                return list(k.keys())[0],function_values
            else:
                update_final_values(final_values,email)
                final_values[list(k.keys())[0]] = function_values
    else:
        function_values = evaluate_helper_function(list(helper_values[helper_value_keys.index("variable")].values())[0],final_values)
        existing_filenames = extract_filenames(email)
        existing_filenames["variable"] = ",".join(function_values) if isinstance(function_values,list) else function_values
        update_filenames(existing_filenames,email)
        data_dict = {i:universal_dict[i] if i in universal_dict else i for i in function_values}
        return "variable",function_values
    
    if("timeslice" not in final_values.keys()):
        update_final_values(final_values,email)
        return "timeslice",["1981","2100"]
    update_final_values(final_values,email)

def add_area_to_params(param,eastings,northings):
    queries = []
    param2 = copy.deepcopy(param)
    E1,E2 = eastings
    N1,N2 = northings
    resolution = param["resolution"]
    print("E1 E2 N1 N2 before conversion",E1,E2,N1,N2)
    resolution_file_mapping = {
        '60':'tas_hadukgrid_uk_60km_ann_202201-202212.nc',
        '25':'tas_hadukgrid_uk_25km_ann_202101-202112.nc',
        '12':'tas_hadukgrid_uk_12km_ann_202201-202212.nc',
        '5':'tas_hadukgrid_uk_5km_ann_202101-202112.nc',
        '2.2':'tas_hadukgrid_uk_5km_ann_202101-202112.nc'
    }
    filepath = os.path.join(os.getcwd(), resolution_file_mapping[resolution])
    dataset = netCDF4.Dataset(filepath,'r')
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
        param["area"] = "bbox|"+str(E1)+"|"+str(N1)+"|"+str(E2)+"|"+str(N2)
        queries.append(param)
    else:
        param["area"] = "point|"+str(e1[0])+"|"+str(n1[0])
        queries.append(param)
        param2["area"] = "point|"+str(e2[0])+"|"+str(n2[0])
        queries.append(param2)

    return queries


def make_api_call_for_rag(querystring,filenames):
    print("api string",querystring)
    api_key = ""
    path = os.path.join(os.getcwd(), "my-outputs")
    for i,j in enumerate(querystring):
        cli = UKCPApiClient(outputs_dir=path, api_key=api_key)
        filename = filenames[i].split("_")
        filename_created = filename[0].upper()+"_"+str(filename[1]).capitalize()+"_"+filename[-1]
        request_url = "https://ukclimateprojections-ui.metoffice.gov.uk/wps?service=WPS&request=Execute&version=1.0.0&Identifier={0}&Format=text/xml&Inform=true&Store=false&Status=false&DataInputs={1}".format(filename_created,j[:len(j)-1])
        file_urls = cli.submit(request_url)
    return file_urls


def make_api_call(querystring,filenames,params,email):
    try:
        print(filenames)
        universal_dict = {}
        filenames_finally_downloaded = []
        with open(os.path.join(os.getcwd(), "universal_explanation_dict.pkl"),"rb") as file:
            universal_dict = pickle.load(file)
        path = os.path.join(os.getcwd(), "my-outputs")
        shutil.rmtree(path, ignore_errors=True)
        for i,j in enumerate(querystring):
            query_param = params[i]
            print("query param",query_param)
            location = query_param["location"]
            variable = universal_dict[query_param["variable"]].replace(" ","-").lower().encode("ascii", "ignore").decode("ascii").replace("/","_")
            temporal_average = query_param["temporalaverage"].lower() if query_param.get("temporalaverage",None) is not None else "no-temporal-average"
            scenario = query_param["scenario"].lower() if query_param.get("scenario",None) is not None else "rcp8.5"
            if "climatechangetype" in query_param.keys():
                filename_recc = location + "_" + variable + "_" + query_param["climatechangetype"] + "_" + query_param["timeslice"].replace("|","_") + "_" + str(query_param["resolution"]) + "km_" + temporal_average + "_" + scenario + "_" +str(i)
            else:
                filename_recc = location + "_" + variable + "_" + "no-climate-change-type" "_" + query_param["timeslice"].replace("|","_") + "_" + str(query_param["resolution"]) + "km_" + temporal_average + "_" + scenario + "_" + str(i)
            print("api string",querystring)
            api_key = ""
            cli = UKCPApiClient(outputs_dir=path, api_key=api_key)
            filename = filenames[i].split("_")
            filename_created = filename[0].upper()+"_"+str(filename[1]).capitalize()+"_"+filename[-1]
            print(filename_created)
            request_url = "https://ukclimateprojections-ui.metoffice.gov.uk/wps?service=WPS&request=Execute&version=1.0.0&Identifier={0}&Format=text/xml&Inform=true&Store=false&Status=false&DataInputs={1}".format(filename_created,j[:len(j)-1])
            file_urls = cli.submit(request_url)
            for k in os.listdir(path):
                if k.endswith(".nc") and not k.startswith(location):
                    os.rename(os.path.join(path,k),os.path.join(path,filename_recc+"_requested_on_"+k))
                    filenames_finally_downloaded.append(filename_recc+"_requested_on_"+k)
        print(os.listdir(os.path.join(os.getcwd(), "my-outputs")))
        return filenames_finally_downloaded 
    except Exception as e:
        traceback.print_exc()
        

def create_s3_client():
    s3_client = boto3.client(
    "s3",
    endpoint_url = "",
    aws_access_key_id = "",
    aws_secret_access_key = "" 
    )
    return s3_client
def create_s3_resource():
    s3_resource = boto3.resource(
    "s3",
    endpoint_url = "",
    aws_access_key_id = "",
    aws_secret_access_key = ""
    )
    return s3_resource

def upload_folder(s3_client, bucket_name, local_directory, s3_folder_name):
    print("In upload folder",bucket_name,local_directory,s3_folder_name)
    print("Existing files",len(os.listdir(local_directory)))
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            local_file_path = os.path.join(root, file)
            
            # Create the relative path for s3
            relative_path = os.path.relpath(local_file_path, local_directory)
            s3_key = os.path.join(s3_folder_name, relative_path).replace("\\", "/")

            # Upload the file
            print(f"Uploading {local_file_path} to {s3_key}...")
            s3_client.upload_file(local_file_path, bucket_name, s3_key)


def zip_folder(folder_path, zip_name):
    print("zip folder")
    zip_file_path = os.path.join(f"{folder_path}",f"{zip_name}")
    print("zip file path",zip_file_path)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".nc"):
                    file_path = os.path.join(root, file)
                    print("file path",file_path)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return zip_file_path

def download_folder(s3_resource, bucket_name, folder_name, local_directory):

    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=folder_name):
        target = os.path.join(local_directory,os.path.relpath(obj.key,folder_name))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key,target)

def convert_to_zip(email):
    print("In convert to zip with email",email)
    client = create_s3_client()    
    destination_folder_name = email.split("@")[0].replace(".","_")
    try:
        upload_folder(client,"ukcpspace","my-outputs",destination_folder_name)
    except Exception as e:
        print("Error uploading files",e)
    return

def make_datainputs_string(params):
    try:
        print("params",params)
        key_api_mapping = {
            'climatechangetype':'ClimateChangeType',
            'temporalaverage':'TemporalAverage',
            'dataformat':'DataFormat',
            'ensemblememberset':'EnsembleMemberSet',
            'timeslice':'TimeSlice',
            'returnperiod':'ReturnPeriod'
        }
        not_req = ["Area.type","Filename","Resolution","Simple","Daily data","Are you aquainted with climate data extraction","Location","meaning"]
        keys = [key_api_mapping[i] if i in key_api_mapping.keys() else i.capitalize() for i in params.keys()]
        keys_final = [i for i in keys if i not in not_req]
        querystring = ""
        print(keys_final)
        for i in keys_final:
            if params[i.lower()] is not None:
                if isinstance(params[i.lower()],list):
                    params[i.lower()]= params[i.lower()][0]
                querystring += i+"="+params[i.lower()]+";"
        return querystring
    except Exception as e:
        traceback.print_exc()





def format_options_string(param,values,timeslice=False):
    universal_dict = {}
    path = os.path.join(os.getcwd(), "universal_explanation_dict.pkl") 
    with open(path,"rb") as file:
        universal_dict = pickle.load(file)
    if timeslice:
        base_string = """This parameter  <strong>{0}</strong> requires a range between <strong>{1}</strong> and <strong>{2}</strong>.""".format("timeslice",values[0],values[1])
    else:
        base_string  = """Please provide the value of the parameter <strong>{0}</strong> <br>""".format(param)
        for i in values:
            explain = universal_dict.get(i,None)
            if explain is not None:
                base_string = base_string + "* " + "<strong>{0}:</strong>  <strong>{1}</strong>".format(i,explain) + "<br>"
            else:
                base_string = base_string + "* " + "<strong>{0}</strong>".format(i) + "<br>"
    return base_string

