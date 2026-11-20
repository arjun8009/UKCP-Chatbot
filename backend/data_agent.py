from openai import OpenAI
import json
from database_helpers import *
from flask import jsonify
from query_helpers import preprocess_zip_data
import traceback

client = OpenAI()
prompt = """You are a data agent for the United Kingdom climate projections chat system. Listed below are your resources, responsibilities and policies \  
    <Resources> \
        1. A list of user data files already downloaded for the user can be None or empty too \
        2. A ukcp data tool that extracts data by giving the user a form. You will be informed what data is downloaded and if it a success or not \
        3. A data analysis tool which needs a query and the relevant data filenames to analyze, plot and make insights from the data. \
    </Resources>
    
    <Responsibilities> 
        1. You will be delegated a query related to analyszing some data or getting some data. \
        2. You will need to decide what tool or steps you will need to use to get the answer. \
            a. Lets say if the query asks to plot some data. you will need to check if the data file exists otherwise use the data tool to get the data and the analysis tool get the insights \
            b. If the data file exists then you can just call the analysis tool. \
        3. Data analysis tool can ask follow up questions to get more clarity on what the user wants. So you will need to decide how to answer those questions. \
        4. Finally after getting the response from the tools. Summarise the responses and generate an answer. \
        5. If the data analysis tool returns some data then show the data too and add a few lines of comments. \
        6. Always check what files are downloaded and just like a conversational agent ensure that the correct data is downloaded when the response from the data extraction is provided. Always inform the user of the discrepancy \
        
    </Responsibilities>
    
    <Policies>
        1. You are not to answer anything that is not supported by the data. Make observations on the results by the data analysis but no conclusions \
        2. If the user asks you a question that does not require getting climate data or analysing it or is not related to your responsibilities then ask the user to contact the Met office Helpdesk \
        3. Keeping within the bounds of your policies outweights everything else \
        4. Ensembles are model runs contained in the data, files with the same parameters but different indexes like _0, _5 are not different ensembles. Do not confuse them, they are different file parts with random ids. \
        5. If you get files with multiple RCPs then analysis should be done for `each RCP` so tell the analysis agent in a single query to analyze each RCP separately and report on each RCP. \
    </Policies>
    
    <Tools>
        1. UKCP climate data extractor \
            a. Arguments need : message = (type : str) = A query which explains exactly what data is missing and needs to be exactly. Do not ask for data that is already present \
            b. Functionality : When this tool will call it will try to establish parameters appropriate and download climate data. It requires a location to be present in the query in text format. It can make bounding boxes itself. \
            c. Response : Response will contain 2 keys \
                    i. success : If true the data has been successfully extracted otherwise false for failed \
                    ii. Filename : The filename of the extracted data \
            d. The data extraction tool can only handle 1 location at a time so multiple queries need to be made for different locations \
                eg Find var1 and 2 for London : This is correct \
                eg Find var1 and 2 for London and Bristol : This is incorrect and correct way is to make 2 calls to the tool \
        
        2. Data Analysis \
             a. arguments : query = (type:str) = What kind of statistical analysis needs to performed or what plots need to be made. Query should contain details of ensemble and spatial aggregation. Do not list filenames here \
                            filenames = (type:list[str]) = A list of all filenames to be used in the analysis \
             b. Response : Response will contain some analysis numbers and/or plot paths. You do not need to worry about plot paths. Just generate a answer on the analysis and inform the user that a related plot has been generated to support this. \
        
        Remember the data analysis tool should return the "approach to the problem or how it solved the problem" as a part of the answer. If it returns include it in the final answer. If not ask it to include it as it is important to know how the problem was tackled. \
    </Tools> \
    
    <Aggregation>
        1. There are two types of Aggregation:
            a. Ensemble Member Aggregation : For each file should ensemble members be aggregated. Human confirmation is needed here \
            b. Spatial Aggregation : So for a point in time, I have climate variable say temperature at each lat-long, Should I average or treat each grid cell separately. This information needs to be provided to data analysis
                eg london at 12km can res can have n grids so given a query do I average accross the N grids or treat each grid cell separately.
    <Aggregation>
    
    <Things To Remember>
        1. The data extraction tool will talk to the user separately. So make sure only 1 tool request is called at a time \
        2. data files are named as <location>_<climate_variable>_<absolute or anomaly>_<timeslice>_<resolution>_<parts>_<extracted_on_date> \
        3. Do not add Filenames in the query. There is a separate field in the tool for that. It avoids confusion \
        3. Remember the data analysis tool should return the "approach to the problem or how it solved the problem" as a part of the answer. If it returns include it in the final answer. If not ask it to include it as it is important to know how the problem was tackled. \
        4. If the data_extraction tool provides a reasoning trace then include it with the final answer. \
        5. Data Extraction tool can only handle 1 location at a time \
        
        6. If you get files with multiple RCPs then analysis should be done for `each RCP` so tell the analysis agent in a single query to analyze each RCP separately and report on each RCP in a single query. \
    </Things To Remember>

    <Human Confirmation>
        Since the data of interest is climate data being consistent is of vital information. So for any given task that requires analysis or processing of the data do the following
        1. Data availability is constrained and the tool chooses the best data. Things you cannot ask the users 
            a. using absolute or anomaly values
            b. using specific RCP's
        2. if 60, 12km data file is being used then ask the user if they want to aggregate model ensembles or not and mention it to the analysis tool always
        since you do not know how many model ensembles are present in data files do not hallucinate the value. Just ask the user if they want to aggregate or not and pass this information to the data analysis tool. \
        if nothing is mentioned in the query ask the user always.
        eg : user : Give me 60km temperature data of Exeter between 2010-2012 -> Do not ask to aggregate the ensembles as this is just asking for the data \
             user : plot/ process/ do something with the data -> ask about aggregation
    </Human Confirmation> \
    
    OUTPUT:
    TEXT :
    OUTPUTS ALWAYS IN MARKDOWN. 
    DATA:
    For DATA SHOWN IN ANSWER FORMAT THE DATA INTO A MARKDOWN TABLE  
    """

tools_definition = [
    {
        "type": "function",
        "name": "data_extraction",
        "description" : "Tool used to extract data. Will tell you when the data extraction is complete.",
        "parameters" : {
            "type":"object",
            "properties":{
                "message": {
                    "type":"string",
                    "description":"A query which explains exactly what data is missing and needs to be exactly. Do not ask for data that is already present"
                }
            }
        }
    },
    {
        "type":"function",
        "name":"data_analysis",
        "description":"Tool to analyze data from different climate data file",
        "parameters":{
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":"The query to be provided to the data analysis agent with information on spatial and ensemble aggregation. Do not list Filenames here"
                },
                "filenames":{
                    "type":"array",
                    "items":{"type":"string"},
                    "description":"The list of filenames on which the analysis or plots are to be generated"
                }
            }
        }
    }
]

def data_agent(query,chat_history,email,time,download=False):
    try:
        from server import decide_on_form_entries,analyse_data,list_files
        data = None
        plots = None
        intermediate_text = " "
        data_analysis_history = None

        if not download:
            files = list_files(email)
            print("FILES PRESENT BEFORE CALLING THE DATA AGENT",files)
            messages= [
                {"role":"system","content":prompt},
                {"role":"user","content":f"The query is {query} and the chat history is {chat_history}. Also you have the following data files {files}"}
            ]
        else:
            print("Entered Tool resume script")
            messages = extract_tool_state(email,"analysis")
            messages = json.loads(list(messages)[0])
            call_id = messages[-1]["call_id"]
            delete_toolstate(email,"analysis")
            messages.append({"type": "function_call_output","call_id": call_id,"output": query})
            print("New Messages",messages)

        response = client.responses.create(
            model="gpt-5-mini",
            input=messages,
            tools=tools_definition)
        
        print("RESPONSE FROM LLM ANALYSIS", response)
        

        while(response.output[-1].type == "function_call") :
            
            for i in response.output:
                clean_msg = {
                    k: v for k, v in i.model_dump().items()
                    if k != "status"
                }
                messages.append(clean_msg)

                if i.type != "function_call" and i.type!="reasoning":
                    intermediate_text = intermediate_text + "\n" + i.content[0].text

                elif i.type == "function_call" and i.name == "data_extraction":
                    query = json.loads(i.arguments)['message']
                    store_tool_state(messages,email,"analysis")
                    return decide_on_form_entries(query,email)

                elif i.type == "function_call" and i.name == "data_analysis":
                    query = json.loads(i.arguments)['query']
                    filenames = json.loads(i.arguments)['filenames']
                    if data_analysis_history is None:
                        data_analysis_history = [{"role":"user","content":query}]
                        data,plots,code =  analyse_data(query,[{"role":"user","content":query}],email,time,filenames)
                    else:
                        data_analysis_history.append({"role":"user","content":query})
                        data,plots,code =  analyse_data(query,data_analysis_history,email,time,filenames)
                    
                    messages.append({"type": "function_call_output","call_id": i.call_id,"output": data})
                    data_analysis_history.append({"role":"assistant","content":data})
            
            response = client.responses.create(
                    model="gpt-5-mini",
                    input=messages,
                    tools=tools_definition)
        
        if data is not None:

            if plots is not None:
                sources = [{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'content':[code],'captions':[f"Results of analysis on the data for the query {query}"],'hasImage':True,'Url':plots, 'llm_extraction':False}]
                update_workflow(email=email,workflow={"owner":"Data","content":response.output_text})
                return preprocess_zip_data(response.output_text,sources,llm_extraction=False)
            else:
                update_workflow(email=email,workflow={"owner":"Data","content":response.output_text})
                return preprocess_zip_data(response.output_text,[{'File':"",'page_number':" ",'Paragraph_num':" ",'content':[code],'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}],llm_extraction=False)
            
        else:
            update_workflow(email=email,workflow={"owner":"Data","content":response.output_text})
            return   preprocess_zip_data(response.output_text,[{'File':"",'page_number':" ",'Paragraph_num':" ",'Relevance':100,'captions':"",'hasImage':False,'Url':"",'hasData':False}],llm_extraction=False)
    except Exception as e:
        print(traceback.format_exc())
        update_workflow(email=email,workflow={"owner":"Data","content":"Something went wrong"})
        delete_toolstate(email,"analysis")
        delete_final_values(email)
        return None
    
        
            

    
    
