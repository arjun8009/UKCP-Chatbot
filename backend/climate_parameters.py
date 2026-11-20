import openai
from pydantic import BaseModel ,Field, Json, ConfigDict
import pickle
import os
import json
os.environ["OPENAI_API_KEY"] = ''
from database_helpers import extract_tool_state

client = openai.OpenAI()

class ClimateResponseFormat(BaseModel):
    model_config = ConfigDict(extra='forbid')
    relevant_parameters: Json = Field(description="A dictionary containing the relevant parameters and their values based on the user query and the provided JSON dataset")
    reasoning_trace: str = Field(description="A detailed reasoning trace explaining why each parameter was chosen or not chosen based on the user query and the provided JSON dataset")

def search_climate_json(spatial_temporal_resolution: str = None):


    spatial_temporal_resolution_mapping = {
        "60km_daily": "ls2_subset_02",
        "60km_not_daily": "ls2_subset_01",
        "12km_daily": "ls3_subset_02",
        "12km_not_daily": "ls3_subset_01",
        "25km_daily": "ls1_subset_02",
        "25km_not_daily": "ls1_subset_01"
    }
    with open("variable_req.json", "r") as f:
        climate_jsons = json.load(f)
    
    items = []
    for item in climate_jsons:
        if (spatial_temporal_resolution is not None and item.get("filename", None) == spatial_temporal_resolution_mapping.get(spatial_temporal_resolution, "")):
            items.append(item)
    return items

def expand_climate_json_abbreviations(abbreviation: list[str]):
    
    with open("universal_explanation_dict.pkl", "rb") as f:
        abbreviation_mapping = pickle.load(f)

    return [abbreviation_mapping.get(abbr, abbr) for abbr in abbreviation]


def decide_climate_parameters(filename: str, climatechangetype: str, statement: str, location: list[str], time_period: str):
    # Define tools available to the LLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "expand_climate_json_abbreviations",
                "description": "Expand abbreviations in climate data parameters to their full forms",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "abbreviation": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of abbreviations to expand"
                        }
                    },
                    "required": ["abbreviation"]
                }
            }
        }
    ]
    
    # Build the JSON context for the prompt
    with open("variable_req.json", "r") as f:
        climate_jsons = json.load(f)
    json_items = [item for item in climate_jsons if item.get("filename", None) == filename and item.get("climatechangetype", None) == climatechangetype][0] if filename and climatechangetype else None

    json_context = json.dumps(json_items, indent=2) if json_items else "[]"
    
    # Initial message with prompt and context
    messages = [
        {"role": "system", "content": prompt2.replace("<<JSON>>", json_context)},
        {"role": "user", "content": f"Filename: {filename}\nUser Query: {statement}\nClimate Change Type: {climatechangetype}\nLocation: {location}\nTime Period: {time_period}"}
    ]
    
    # Tool call loop
    max_iterations = 5
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            temperature=0)
                
        # Add assistant response to messages
        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls
        })
        print(messages[1:])
        
        # Check if there are tool calls
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            # No more tool calls, return final response
            return response.choices[0].message.content
        
        # Execute each tool call
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            if func_name == "expand_climate_json_abbreviations":
                result = expand_climate_json_abbreviations(**func_args)
            else:
                result = f"Unknown function: {func_name}"
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    
    # Max iterations reached
    return "Max iterations reached without final answer"



prompt2 = """You are an expert in choosing correct parameters for climate data given a json of a dataset. \
    Follow the steps below to choose the correct parameters  : \
    1. You will be given a single short json which contains keys and values.\
    2. For keys containing multiple values in a list, you need to choose the most relevant value based on the user query. \
    3. locations will be provided to you so just add it in the json as a key value pair. Time period will also be provided so modify the timeslice parameter using that. \
    3. Exceptions : Variable,Scenario and location can have multiple values and you need to choose all the relevant ones and timeslice is [lower_bound, upper_bound]. So apart from these ideally key:"value" should be included \
    4. The Json VALUES may contain abbreviations so call tool expand_climate_json_abbreviations with a list of the abbreviations to get their full forms. \
    5. Final output is a JSON of the same format as the input JSON but with only the relevant values in the list (do not include full forms or new keys and values) and a reasoning trace. \
    VERY IMPORTANT POINTS:
    1. All parameters except variable, location and timeslice will always have 1 values. Do not forget this. Even temporal average will have 1 value.
    so to make it clear "variable", "scenario" "timeslice" and location : type list and rest type "str"
    2. Timeslice is a list always [start year : str  , end year : str] (only year in string is accepted here)
    <<JSON>>

    """

prompt = """ You are an expert in choosing correct parameters for climate data given a user query. Now the parameters need to be chosen from \
a set of available climate datasets. Each dataset can have multiple parameters and the JSON is a list of all the available datasets and their parameters. Given a user query you need to choose the most relevant dataset and parameters from the JSON. \
You have a search_climate_json function which takes a key or a spatial_temporal_resolution and returns all the datasets which have that key in their parameters. You can use this function to find relevant datasets and parameters. \

Here is how you solve the problem step by step : \
1. Read the user query. Understand the user requirement. If the user query is simple enough and not a big case study go to next step. Otherwise feel free to ask more questions to the user. \
2. Next identify the location in UK and time period for which the climate data needs to be extracted. If not mentioned always ask for it. No possibility for assumptions here. Location can be a single or multiple locations in UK so location : list[str] \
3. Next using the location and time period as refference identify the spatial and temporal resolution most suitable for the query. Available spatial resolutions are 60km, 12km, 25km. Available temporal resolutions are daily, not daily (monthly, yearly,seasonal) \
4. One identified make the spatio_temporal resolution string in the format of {spatial_resolution}_{temporal_resolution} (e.g. 60km_daily, 60km_not_daily) \
5. Use the search_climate_json function to find all datasets which have the identified spatio_temporal resolution. \
6. Once done you now need to choose the relevant dataset from the list of datasets. \
7. Once you have the choice then call the tool decide_climate_parameters with the filename and climatechangetype of the chosen dataset and a statement with the user's query. \
8. Finally call the tool extract_climate_info with 2 args, the JSON parameter as a dictionary and a reasoning trace as a string. This will do the formatting for the user. \
9. Remember a single json schema is to be returned once and multiple jsons or multiple outputs with different parameters are not allowed


IMPORTANT POINTS : \
0. If nothing matches directly to the user requirments, choose the closest.
1. Always follow the steps and do not skip any step. \
2. spatio_temporal_resolution string is just spatialresolution_temporalresolution with an underscore in between. so it will always have a number followed by km followed by an underscore followed by either daily or not_daily. \
3. climatechangetype is either absolute or anomaly. \
4. call the tool extract_climate_info with 2 args, the JSON parameter as a dictionary and a reasoning trace as a string. This is vital to format the output into user requirements and the last step. \
5. If nothing matches directly to the user requirments, choose the closest.
6. Remember a single json schema is to be returned once and multiple jsons or multiple outputs with different parameters are not allowed.
"""

def choose_climate_parameters(user_query: str, email:str):
    # Define tools available to the LLM
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_climate_json",
                "description": "Search for climate datasets by spatial_temporal_resolution",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spatial_temporal_resolution": {
                            "type": "string",
                            "description": "The spatial and temporal resolution string (e.g., '60km_daily', '12km_not_daily')"
                        }
                    },
                    "required": ["spatial_temporal_resolution"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "decide_climate_parameters",
                "description": "Choose correct parameters for climate data given a dataset filename and user query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The filename of the chosen climate dataset"
                        },
                        "statement": {
                            "type": "string",
                            "description": "The user's query or requirement"
                        },
                        "climatechangetype": {
                            "type": "string",
                            "description": "The type of climate change to consider (absolute or anomaly)"
                        },
                        "location": {
                            "type": "array",
                            "items":{
                                "type":"string"
                                },
                            "description": "The locations in the UK for which the climate data is needed"
                        },
                        "time_period": {
                            "type": "string",
                            "description": "The time period for which the climate data is needed"
                        }
                    },
                    "required": ["filename", "statement", "climatechangetype", "location", "time_period"]
                }
            }
        },

        {
        "type": "function",
        "function": {
            "name": "extract_climate_info",
            "description": "Extract relevant climate parameters",
            "parameters": ClimateResponseFormat.model_json_schema(),
            "strict": True
        }
    }
    ]
    
    # Initial message with prompt and user query
    exisiting_messages = extract_tool_state(email,"extraction")
    
    if exisiting_messages is not None and len(exisiting_messages) > 0:
        messages = list(json.loads(list(exisiting_messages)[0]))
        messages.append({"role":"user","content":user_query})
    else:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
    
    # Tool call loop
    max_iterations = 5
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            temperature=0
        )
        
        # Add assistant response to messages
        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls
        })

        
        # Check if there are tool calls
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            # No more tool calls, return final response
            return response.choices[0].message.content,messages
        
        # Execute each tool call
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            if func_name == "search_climate_json":
                result = search_climate_json(**func_args)
            elif func_name == "decide_climate_parameters":
                result = decide_climate_parameters(**func_args)
            elif func_name == "extract_climate_info":
                return func_args,messages  # This is the final output, so we return it directly
            else:
                result = f"Unknown function: {func_name}"
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    
    # Max iterations reached
    return "Max iterations reached without final answer"

