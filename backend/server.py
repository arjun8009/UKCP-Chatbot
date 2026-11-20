from flask import Flask, request, jsonify,send_file
from flask_cors import CORS
from main import provide_gpt_response,get_lat_long_range
import pandas as pd
from sqlalchemy import create_engine
from helpfunction import resolve_questions_in_data_module
import psycopg2
import os
import pickle
import numpy as np 
import pandas as pd
from query_helpers import *
import time
from database_helpers import *
import requests
import uuid
import shutil
from data_agent import data_agent
import pyproj
import traceback
from navigatoragent import decide_on_workflow
from climate_parameters import choose_climate_parameters

app = Flask(__name__)
CORS(app)
@app.route('/receive-data', methods=['POST'])
def receive_data():
    print("Entered Received data")
    data = request.get_json()
    user_input = data
    print(user_input)
    incomplete=None
    pipeline_index = None
    email = user_input["updated_message"][-1]["email"]
    time = user_input["updated_message"][-1]["time"]
    dataOption = None
    
    if (not user_input["updated_message"][-1]["hasData"]) or (user_input["updated_message"][-1]["dataOption"]=="/Text") or (user_input["updated_message"][-1]["dataOption"]=="/Image") or (user_input["updated_message"][-1]["dataOption"]=="/Both") or (user_input["updated_message"][-1]["dataOption"]=="/Help"):
        if user_input["updated_message"][-1].get("incomplete",None) is not None:
            incomplete = True
        if user_input["updated_message"][-1].get("pipelineIndex",None) is not None:
            pipeline_index = user_input["updated_message"][-1].get("pipelineIndex",1)

        if user_input["updated_message"][-1].get("dataOption",None) is not None:
            dataOption = user_input["updated_message"][-1].get("dataOption",1)

        for i in user_input["updated_message"]:
            if "hasData" in i:
                del i["hasData"]
            if "Data" in i:
                del i["Data"]
            if "incomplete" in i:
                del i["incomplete"]
            if "pipelineIndex" in i:
                del i["pipelineIndex"]
            if "dataOption" in i:
                del i["dataOption"]
        delete_filenames(email)
        delete_final_values(email)
        response = preprocess_data(user_input,incomplete,pipeline_index,dataOption,email,time)
        print("Response in receive data",response)
    return response


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status='ok')


@app.route('/login-verify', methods=['POST'])
def login_verify():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    result = extract_login(email,password)
    return jsonify({"success":result})

@app.route('/login-signup', methods=['POST'])
def signup_verify():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    name = data["name"]
    signup(name,email,password)
    return jsonify({"success":True})

@app.route('/api/session-end', methods=['POST'])
def session_end():
    try:
        data =  json.loads(request.data.decode('utf-8'))
        print(data)
        start = str(data.get('start', 0))
        end = str(data.get('end', 0))
        email = str(data.get('email', 0))
        #duration = end - start
        print("Session duration recorded", start,end,email)
        session_store(start, end, email)
        return jsonify({"message": "Session duration recorded"})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})

@app.route('/receive-feedback_db', methods=['GET'])
def provide_db_data():
    conn_string = ""
    conn = psycopg2.connect(conn_string) 
    try:
        cursor = conn.cursor() 
        sql1 = '''select * from feedbackukcp;'''
        cursor.execute(sql1) 
        data = cursor.fetchall()
    except Exception as e:
        print({e})
        conn.rollback()
        conn.close()
    conn.close()
    df = pd.DataFrame(data=data)
    df.columns = ["question","answer","extracts","feedback","index"]
    json_results = df.to_json(orient='records')
    return json_results







def data_parameter(email):
    try:
            universal_dict = {}
            path = os.path.join(os.getcwd(), "universal_explanation_dict.pkl") 
            with open(path,"rb") as file:
                universal_dict = pickle.load(file)
            path = os.path.join(os.getcwd(),"data_state")
            possible_values = None
            possible_values = extract_filenames(email)
            final_values = {}
            pending = {}
            remaining_keys = None

            
            if count_final_values(email)!=0:
                final_values = extract_final_values(email)

            remaining_keys = set(possible_values.keys()) - set(final_values.keys())

            
            print("final values in data parameter",final_values)
            print("remaining keys",remaining_keys)

            if len(remaining_keys) == 0:
                return None
            else:
                new_possible_values = {}
                for l in remaining_keys:
                    new_possible_values[l] = possible_values[l]
                params = param_search(new_possible_values,email)
                print("params",params)
                if (params is not None) and (len(params) == 2):
                    if params[0] == "timeslice" and len(params[1]) ==2:
                        response =  (params[0],params[1],True)
                    else:
                        response = (params[0],params[1],False)
                    return response
    except Exception as e:
        delete_final_values(email)
        delete_toolstate(email,"analysis")
        delete_toolstate(email,"data")

        response = preprocess_api_data("I am unable to process your request at the moment. Please try again later.",[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}])
        print("Error in data_parameter")
        traceback.print_exc()
        return response



@app.route('/download', methods=['POST'])
def download():
    email = request.get_json()["emailid"]
    folder_name = email.split("@")[0].replace(".","_") + "/"
    s3_resource = create_s3_resource()

    # Create a unique directory for this user using UUID
    unique_id = str(uuid.uuid4())
    local_directory = os.path.join("tmp",f"s3_download_{unique_id}")
    rel_directory = os.path.join("tmp",f"s3_download_{unique_id}")
    os.makedirs(local_directory, exist_ok=True)

    # Download and zip the folder
    print("In Download",)
    download_folder(s3_resource, "ukcpspace", folder_name, local_directory)
    zip_path = zip_folder(local_directory, 'data.zip')
    print("zip path",zip_path)
    rel_directory = os.path.join(rel_directory,"data.zip")
    print(rel_directory)

    # Prepare file for download
    response = send_file(rel_directory, as_attachment=True) 
    # Clean up the directory after sending the file
    shutil.rmtree(os.path.join("tmp"), ignore_errors=True)

    return response

def list_files(email):
    s3_client = create_s3_client()
    response = s3_client.list_objects_v2(Bucket="ukcpspace", Prefix=email.split("@")[0].replace(".","_"))
    file_list = []
    if 'Contents' in response:
        for obj in response['Contents']:
            if not obj['Key'].endswith('/'):  # Skip folders
                file_list.append(obj['Key'])
    file_list = [i for i in file_list if i.endswith(".nc")]
    files = "\n".join(file_list)
    if len(files) == 0:
        return []
    else:
        return files



def analyse_data(query,chat_history,email,time,filenames):
    try:
        
        api_url = 'http://localhost:8080/dataanalysis/get_results'
        filenames = [i.split("/")[-1] for i in filenames]
        data = {'query': query, 'email':email,'chat_history': chat_history, 'filenames': filenames}
        response = requests.get(api_url, json=data)
        response = response.json()
        print(response)
        text_response = response.get('response')
        image_url = response.get('path')
        code = response.get('code')
        store_question_and_answers(query,text_response,email,"",time)
        if image_url is not None:
            return text_response,image_url,code
        else:
            return text_response,None,code
    except Exception as e:
        return jsonify([{'role':'assistant','content':"Something went wrong. Please type the query again"},
                            {'role':'user','sources':[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}]}])
        

def preprocess_data(user_input,incomplete,pipeline_index,dataOption,email,time):
    print("In preprocess data")
    history = user_input["updated_message"]
    if len(history) < 3:
        delete_workflows(email)
        delete_filenames(email)
        delete_final_values(email)
        delete_toolstate(email,"analysis")
        delete_toolstate(email,"extraction")
    query = user_input["updated_message"][-1]["content"]
    update_workflow(email=email,workflow={"owner":"user","content":query})
    ambiguity,msg,workflow = decide_on_workflow(query,email)
    print("Decided Info",ambiguity,msg,workflow)
    blank_excerts = [{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}]
    
    if ambiguity:
        print("Entered amibguity")
        response,excerpts,data = provide_gpt_response(user_input,incomplete,pipeline_index,dataOption)
        response = response + "\n" + msg
        update_workflow(email=email,workflow={"owner":"RAG","content":response})
        return jsonify([{'role':'assistant','content':response},
                        {'role':'user','sources':excerpts}])

    elif workflow.lower() == "rag":
        print("Entered RAG")
        response,excerpts,data = provide_gpt_response(user_input,incomplete,pipeline_index,dataOption)
        update_workflow(email=email,workflow={"owner":"RAG","content":response})
        return jsonify([{'role':'assistant','content':response},
                        {'role':'user','sources':excerpts}])
    elif workflow.lower() == "data":
        print("Entered Data")
        response = data_agent(query,user_input["updated_message"],email,time)
        print("Response from data agent",response)
        return response
    else:
        print("Entered violation")
        update_workflow(email=email,workflow={"owner":"Navigator","content":msg})
        return  jsonify([{'role':'assistant','content':msg},
                        {'role':'user','sources':blank_excerts}])

def make_bbox_to_queries(final_values):
        try:
            locations = final_values["location"]
            all_queries = []
            for location in locations:
                SW,NE = get_lat_long_range(location)
                lat1 = SW[0]
                long1 = SW[1]
                lat2 = NE[0]
                long2 = NE[1]
                projection_params = {
                    'proj': 'tmerc',
                    'lat_0': 49.0,  # Latitude of the origin
                    'lon_0': -2.0,  # Longitude of the central meridian
                    'k_0': 0.9996012771,  # Scale factor
                    'x_0': 400000.0,  # False easting
                    'y_0': -100000.0  # False northing
                }
                tm_projection = pyproj.Proj(projection_params)
                E1, N1 =  pyproj.transform(pyproj.Proj(proj='latlong'), tm_projection, long1, lat1)
                E2, N2 =  pyproj.transform(pyproj.Proj(proj='latlong'), tm_projection, long2, lat2)
                E1 = round(E1)
                E2 = round(E2)
                N1 = round(N1)
                N2 = round(N2)
                queries = add_area_to_params(final_values,(E1,E2),(N1,N2))
                for i in queries:
                    i["location"] = location
                all_queries.extend(queries)
            return all_queries
        except Exception as e:
            traceback.print_exc()



def submit_data_request_offline(email,time,reasoning_trace=None):
    try:
        
        print("Email",email)
        final_values = extract_final_values(email)
        print("extracted final values", final_values)
        if not isinstance(final_values["location"],list):
            final_values["location"] = [final_values["location"]]
        queries = make_bbox_to_queries(final_values)

        if "scenario" in final_values.keys() and isinstance(final_values["scenario"],list):
            queries  = [
                    {**query, "variable": v, "scenario":s}
                    for query in queries
                    for v in query["variable"]
                    for s in query["scenario"]
                ]
        else:
            queries  = [
                    {**query, "variable": v}
                    for query in queries
                    for v in query["variable"]
                ]

        querystrings = []
        filenames = []
        for i in queries:
            querystrings.append(make_datainputs_string(i))
            filenames.append(final_values["filename"])
        filenames_created = make_api_call(querystrings,filenames,queries,email)
        convert_to_zip(email)
        delete_final_values(email)
        msg = f"The Data has been successfully downloaded with filenames {filenames_created} \
            Reasoing trace : {reasoning_trace}"
        return data_agent(msg,None,email,time,True)
    except Exception as e:
        traceback.print_exc()
        delete_final_values(email)
        delete_toolstate(email,"analysis")
        delete_toolstate(email,"extraction")
        update_workflow(email=email,workflow={"owner":"Data","content":"Something went wrong"})
        return preprocess_api_data("I am unable to process your request at the moment. Please try again later. Please check if the start year < end year and the location is a valid UK location. Otherwise contact the developer",[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}])




@app.route("/Submit-data-request",methods=['POST'])
def submit_data_request():
    try:
        data = request.get_json()
        email = data["email"]
        time = data["time"]
        print("Email",email)
        final_values = extract_final_values(email)
        location = final_values["location"]
        SW,NE = get_lat_long_range(location)
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
        tm_projection = pyproj.Proj(projection_params)
        E1, N1 =  pyproj.transform(pyproj.Proj(proj='latlong'), tm_projection, long1, lat1)
        E2, N2 =  pyproj.transform(pyproj.Proj(proj='latlong'), tm_projection, long2, lat2)
        E1 = round(E1)
        E2 = round(E2)
        N1 = round(N1)
        N2 = round(N2)
        queries = add_area_to_params(final_values,(E1,E2),(N1,N2))
        queries  = [
                {**query, "variable": v}
                for query in queries
                for v in query["variable"]
            ]
        querystrings = []
        filenames = []
        for i in queries:
                        querystrings.append(make_datainputs_string(i))
                        filenames.append(final_values["filename"])
        filenames_created = make_api_call(querystrings,filenames,queries,email)
        convert_to_zip(email)
        delete_final_values(email)
        msg = f"The Data has been successfully downloaded with filenames {filenames_created}"
        return data_agent(msg,None,email,time,True)
    except Exception as e:
        print(e)
        delete_final_values(email)
        delete_toolstate(email,"analysis")
        delete_toolstate(email,"extraction")
        update_workflow(email=email,workflow={"owner":"Data","content":"Something went wrong"})
        return preprocess_api_data("I am unable to process your request at the moment. Please try again later. Please check if the start year < end year and the location is a valid UK location. Otherwise contact the developer",[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False, 'llm_extraction':False}])

@app.route('/data-parameter', methods=['POST'])
def data_parameter_route():
    try:
        response = request.get_json()
        email = response["email"]
        data = response["data"]
        with open (os.path.join(os.getcwd(), "universal_explanation_dict.pkl"),"rb") as file:
            universal_data = pickle.load(file)
        opposite_universal_data = {v:k for k,v in universal_data.items()}
        print("Data received in data-parameter route",data)
        final_values = extract_final_values(email)
        if final_values is  None:
            final_values = {"simple":data["Are you aquainted with climate data Extraction"]}
            
            update_final_values(final_values,email)
        else:
            #data = {k:opposite_universal_data.get(v,v) for k,v in data.items()}
            data = {k:[opposite_universal_data.get(i,i) for i in v] if isinstance(v,list) else opposite_universal_data.get(v,v) for k,v in data.items()}
            if "start_year" in data.keys() and "end_year" in data.keys():
                timeslice = str(int(data["start_year"]) - 1) + "|" + str(int(data["end_year"]) + 1)
                del data["start_year"]
                del data["end_year"]
                data["timeslice"] = timeslice
            final_values.update(data)
            update_final_values(final_values,email)
        print("Final values after receiveing",final_values)
        
        return decide_on_form_entries(" ",email)
    except Exception as e:
        print(e)
        update_workflow(email=email,workflow={"owner":"Data","content":"Something went wrong"})
        delete_final_values(email)
        delete_toolstate(email,"analysis")
        delete_toolstate(email,"extraction")
    

def provide_next_param_values(email):
    try:
        print("Entered New Param")
        print("In new param", extract_final_values(email))
        with open (os.path.join(os.getcwd(),"universal_explanation_dict.pkl"),"rb") as file:
            data = pickle.load(file)
        values = data_parameter(email)
        if values is not None:
            print(values)
            if values[0] == "timeslice":
                if len(values[1]) == 2:
                    return (values[0],values[1],"range")
            elif values[0] == "variable":
                return (values[0],[data[i] for i in values[1]],"multiselect")
            else:
                return (values[0],[data[i] for i in values[1]],"select")
        else:
            return None
    except Exception as e:
        print(e)
        update_workflow(email=email,workflow={"owner":"Data","content":"Something went wrong"})
        delete_final_values(email)
        delete_toolstate(email,"analysis")
        delete_toolstate(email,"extraction")

    

def decide_on_form_entries(user_input,email):
    try:

        entries_in_form = extract_final_values(email)
        print("Entries in form",entries_in_form)
        
        if entries_in_form is None:
            return jsonify([{'role':'assistant','optional_message':user_input,'content':{"Are you aquainted with climate data Extraction":{"options":["Yes","No"],"type":"select"}}, "Form":True, "llm_extraction":True}
                            ,{"role":"user","sources":[{'File':" ",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'hasImage':False,'Url':" ",'captions':" ",'hasData':False,'incomplete':True}]}])
        else:
            choice = entries_in_form["simple"]
            if choice == "No":
                return llm_decide_data_offline(user_input,email)
            else:

                if "resolution" in entries_in_form.keys():
                    
                    if "filename" not in entries_in_form.keys():

                        with open(os.path.join(os.getcwd(),"variable_requirements.pkl"),'rb') as file:
                            variable_requirements = pickle.load(file)

                        exact_mapping = {
                        '25-notdaily-notderived':'ls1_subset_02',
                        '60-notdaily-notderived':'ls2_subset_01',
                        '60-daily-notderived':'ls2_subset_02',
                        '2.2-notdaily-notderived':'ls3a_subset_01',
                        '2.2-daily-notderived':'ls3a_subset_02',
                        '2.2-hourly-notderived':'ls3a_subset_03',
                        '12-notdaily-notderived':'ls3_subset_01',
                        '12-daily-notderived':'ls3_subset_02',
                        'historic-notdaily-notderived':'ls6_subset_01',
                        'historic-daily-notderived':'ls6_subset_02'
                    }
                        filename = exact_mapping[entries_in_form["resolution"]+"-"+"notdaily"+"-"+"notderived"]
                        
                        final_values = extract_final_values(email)
                        final_values["filename"] = filename
                        file_final = [i for i in variable_requirements if i["filename"] == filename][0]
                        update_filenames(file_final,email)
                        print("filename decided",filename)
                        update_final_values(final_values,email)
                    new_params = provide_next_param_values(email)
                    if new_params is not None:
                        if new_params[2] == "range":
                            return jsonify([{"role":"assitant","content":{"start_year":{"type":new_params[2],"options":new_params[1]},"end_year":{"type":new_params[2],"options":new_params[1]}},"Form":True}
                                    ,{"role":"user","sources":[{'File':" ",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'hasImage':False,'Url':" ",'captions':" ",'hasData':False,'incomplete':True}]}])
                        else:
                            return jsonify([{"role":"assitant","content":{new_params[0]:{"type":new_params[2],"options":new_params[1]}},"Form":True}
                                    ,{"role":"user","sources":[{'File':" ",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'hasImage':False,'Url':" ",'captions':" ",'hasData':False,'incomplete':True}]}])
                    else:
                        return "Success"
                else:
                    print("Entered Pre-requisite")
                    return jsonify([{"role":"assitant","content":{"resolution":{"type":"select","options":["60","25","12"]},"location":{"type":"text","options":["UK"]}},"Form":True}
                                ,{"role":"user","sources":[{'File':" ",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'hasImage':False,'Url':" ",'captions':" ",'hasData':False,'incomplete':True}]}])
    except Exception as e:
        print(e)
        update_workflow(email=email,workflow={"owner":"Data","content":"Something went wrong"})
        delete_final_values(email)


def llm_decide_data_offline(user_response, email):
    print("In LLM decide server")
    messages = extract_tool_state(email,"analysis")
    messages = json.loads(list(messages)[0])
    query = json.loads(messages[-1]["arguments"])['message']
    try:
        print(query)
        response,messages = choose_climate_parameters(query,email)
    except Exception as e:
        traceback.format_exc()
        delete_toolstate(email,"analysis")
        return jsonify([{'role':'assistant','content':"Something went wrong", 'llm_extraction':False},
                            {'role':'user','sources':[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}]}])
    if isinstance(response,dict):
        relevant_parameters = json.loads(response["relevant_parameters"])
        relevant_parameters["timeslice"] = "|".join(relevant_parameters["timeslice"]) 
        update_final_values(relevant_parameters,email)
        return submit_data_request_offline(email," ",response["reasoning_trace"])
    else:
        store_tool_state(messages=messages,email=email,tooltype="extraction")
        print(response)
        return jsonify([{'role':'assistant','content':response, 'llm_extraction':True},
                            {'role':'user','sources':[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}]}])



@app.route("/llm-decide", methods=["POST"])
def llm_decide_data():
    
    params = request.get_json()
    email = params["updated_message"][-1]["email"]
    time = params["updated_message"][-1]["time"]
    user_response = params["updated_message"][-1]["content"]
    print("In LLM decide server")
    try:
        response,messages = choose_climate_parameters(user_response,email)
    except Exception as e:
        print(traceback.format_exc())
        delete_toolstate(email,"analysis")
        return jsonify([{'role':'assistant','content':"Something went wrong", 'llm_extraction':False},
                            {'role':'user','sources':[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}]}])
    
    if isinstance(response,dict):
        print("Response from LLM",response)
        relevant_parameters = json.loads(response["relevant_parameters"])
        relevant_parameters["timeslice"] = "|".join(relevant_parameters["timeslice"]) 
        update_final_values(relevant_parameters,email)
        return submit_data_request_offline(email,time,response["reasoning_trace"])
        
    else:
        store_tool_state(messages=messages,email=email,tooltype="extraction")

        return jsonify([{'role':'assistant','content':response, 'llm_extraction':True},
                            {'role':'user','sources':[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}]}])








if __name__ == '__main__':
    # For local development using Flask's built-in server
    app.run(host="0.0.0.0")
