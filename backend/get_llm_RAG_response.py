import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
from prompt_automated import system_instruction_rag, user_prompt_rag
from query_prompt import query_system_instruction, query_prompt
import os
import openai
import pickle
import pandas as pd
import numpy as np
from scipy import spatial
import warnings
import itertools
from haystack import Document
from haystack_integrations.components.rankers.cohere import CohereRanker
from haystack.components.rankers import LostInTheMiddleRanker
from get_pickle import get_vectorizer
from query_helpers import *
import xarray as xr
from tool_based_prompt import system_instruction_tool, tool_definitions
import pyproj
import traceback
from concurrent.futures import ThreadPoolExecutor
from get_image_response import provide_image_llm_response
import json


os.environ["OPENAI_API_KEY"] = '" "'
os.environ["COHERE_API_KEY"] = ''
client = openai.OpenAI()
model = "gpt-4o-mini"
embedding_model = "text-embedding-ada-002"

def generate_queries(original_query, multiple_query_generation, query_k):

    generated_queries = [original_query]

    if multiple_query_generation:
        global query_prompt
        global query_system_instruction

        chat_history = []

        system_prompt_dup = query_system_instruction
        query_system_instruction = query_system_instruction.replace("<NUMBER>", str(query_k))
        chat_history.append({"role": "system", "content": query_system_instruction})
        query_system_instruction = system_prompt_dup

        user_prompt_dup = query_prompt
        query_prompt = query_prompt.replace("<QUESTION>", original_query)
        chat_history.append({"role": "user", "content": query_prompt})
        query_prompt = user_prompt_dup

        response = client.chat.completions.create(
            model=model,
            messages=chat_history,
            temperature=0,
            max_tokens=2048,
        )

        new_queries = response.choices[0].message.content.strip().split("\n")
        generated_queries += [q[3:] for q in new_queries]

    query_embeddings = [client.embeddings.create(model=embedding_model,input=query).data[0].embedding for query in generated_queries]
    return generated_queries, query_embeddings

def reciprocal_rank_fusion(search_results_dict, top_k, k=60):
    fused_scores = {}
        
    for chunk_indices in search_results_dict.values():
        for rank, chunk_index in enumerate(chunk_indices):
            if chunk_index not in fused_scores.keys():
                fused_scores[chunk_index] = 0
            fused_scores[chunk_index] += 1 / (rank + k)

    reranked_results = [int(chunk_index) for chunk_index, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)][:top_k]
    return reranked_results

def hierarchical_retrieval(queries, query_embeddings, hierarchical_k, hierarchical_reranking, ranker):

    path = path = os.path.join(os.getcwd(),"data")
    data = pd.read_parquet(f"{path}/document_summaries_new.parquet")
    relatedness_fn = lambda a, b: 1 - spatial.distance.cosine(a, b) 

    retrieved_ids, retrieved_chunks = {}, {}
    for i, query_embedding in enumerate(query_embeddings):
        question_relevance = np.round(np.array([relatedness_fn(query_embedding, embedding) for embedding in data.embedding]).astype(float), 16)  # distance between question embeddings and summary embeddings
        retrieved_ids[i] = np.array(data.file_id)[np.argsort(question_relevance)[::-1]][:hierarchical_k]
        retrieved_chunks[i] = np.array(data.chunk)[np.argsort(question_relevance)[::-1]][:hierarchical_k]
    
    reranked_file_ids = retrieved_ids[0] if hierarchical_reranking == False else re_ranker(queries[0], retrieved_ids, retrieved_chunks, ranker, top_k=hierarchical_k)

    return reranked_file_ids

def small_to_big_retrieval(retrieved_nodes):

    similarity_top_k=5
    desired_sections =  list(dict.fromkeys([node.metadata['section_id'] for node in retrieved_nodes]))[:similarity_top_k]

    path = path = os.path.join(os.getcwd(),"data")
    section_data = pd.read_parquet(f"{path}/data_chunks_sections.parquet")
    section_data = section_data[section_data.section_id.isin(desired_sections)]

    final_chunks = section_data.chunk.tolist()
    final_headings = section_data.heading.tolist()
    final_file_names = section_data.file_name.tolist()
    
    return final_chunks, final_headings, final_file_names


def get_llm_response(chunks, query, file_names, headings):

    global user_prompt_rag

    chat_history = []
    chat_history.append({"role": "system", "content": system_instruction_rag})
    user_prompt_dup = user_prompt_rag
    user_prompt_rag = user_prompt_rag.replace("<EXCERPTS>", "<SEP>".join(chunks))
    user_prompt_rag = user_prompt_rag.replace("<QUESTION>", query)
    # user_prompt = user_prompt.replace("<FILES>", "<SEP>".join(file_names))
    # user_prompt = user_prompt.replace("<SECTIONS>", "<SEP>".join(headings))
    chat_history.append({"role": "user", "content": user_prompt_rag})
    user_prompt_rag = user_prompt_dup

    response = client.chat.completions.create(model="o3-mini",messages=chat_history)
    response_message = response.choices[0].message.content

    return response_message


def re_ranker(query, retrieved_ids, retrieved_chunks, ranker, top_k=25):

    if ranker == 'reciprocal':
        return  reciprocal_rank_fusion(retrieved_ids, top_k)
    
    # indices method
    retrieved_ids = list(itertools.chain.from_iterable(retrieved_ids.values()))
    retrieved_chunks = list(itertools.chain.from_iterable(retrieved_chunks.values())) 
    retrieved_chunks_ids_set = {retrieved_chunks[i]: retrieved_ids[i] for i in range(len(retrieved_chunks))}

    documents = [Document(content=key,id=val) for key, val in retrieved_chunks_ids_set.items()]

    if ranker == 'cohere':
        cohere_api_key = ""
        ranker = CohereRanker(model="rerank-multilingual-v3.0", top_k=top_k) 


    
    elif ranker == 'lost':
        ranker = LostInTheMiddleRanker(word_count_threshold=2048, top_k=top_k,)

    ranked_docs = ranker.run(query=query, documents=documents,top_k=top_k)
    ranked_docs = ranked_docs["documents"]
    ranked_docs_ids = [int(doc.id) for doc in ranked_docs if str(doc.id).isdigit()]

    return ranked_docs_ids



def retrieve_nodes(queries, chunking_method, similarity_top_k, ranker=None, metadata=None):

    retrieved_nodes = get_vectorizer(chunking_method,similarity_top_k,metadata,queries)
    retrieved_ids = {key: [node.id_ for node in val if node.id_.isdigit()] for key, val in retrieved_nodes.items()}
    retrieved_chunks = {key: [node.text for node in val if node.id_.isdigit()] for key, val in retrieved_nodes.items()}
    reranked_ids = retrieved_ids[0] if ranker == None else re_ranker(queries[0], retrieved_ids, retrieved_chunks, ranker, top_k=15) # discuss how to provide chunks without reranking

    final_nodes = []
    for id in reranked_ids:
        for node in list(itertools.chain.from_iterable(retrieved_nodes.values())):
            if int(id) == int(node.id_):
                final_nodes.append(node)
                break

    return final_nodes


def answer_generation(question, chunking_method, retrieval_type, hierarchical_k, chunking_k, query_k, multiple_query_generation, 
         hierarchical_reranking, ranker, model='gpt-4o-mini'):

    
    os.environ["OPENAI_API_KEY"] = '" "'

    # generate multiple queries and their embeddings, and place them both in lists
    queries, query_embeddings = generate_queries(question, multiple_query_generation, query_k)

    metadata = None
    
    if 'hierarchical' in retrieval_type:
        # semantic search between queries and whole document summaries, reduce dataset before searching for smaller chunks
        metadata = hierarchical_retrieval(queries, query_embeddings, hierarchical_k, hierarchical_reranking, ranker)
        
    # semantic search for most relevant chunks
    retrieved_nodes = retrieve_nodes(queries, chunking_method=chunking_method, similarity_top_k=20, ranker=ranker, metadata=metadata)
    
    if 'small-to-big' in retrieval_type:
        # extract section chunks from which the most relevant paragraph / fixed length chunks derive    
        final_chunks, final_headings, final_file_names = small_to_big_retrieval(retrieved_nodes)
    else:
        final_chunks = [node.text for node in retrieved_nodes][:chunking_k]
        final_headings = [node.metadata['heading'] for node in retrieved_nodes][:chunking_k]
        final_file_names = [node.metadata['file_name'] for node in retrieved_nodes][:chunking_k]

    response = get_llm_response(final_chunks, question, final_file_names, final_headings)

    return response, final_file_names, final_headings, final_chunks

def get_GPT_answer(question):
    chat_history = []
    chat_history.append({"role": "system", "content": "Give a good answer related to UKCP"})
    chat_history.append({"role":"user","content":question})
    response = client.chat.completions.create(model=model,messages=chat_history,temperature=0,max_tokens=1024,)
    response_message = response.choices[0].message.content
    return response_message,["GPT-info"],["GPT-info"] ,["GPT-info"]

def response_from_pipeline(question,pipeline_index):
    if pipeline_index == "1" or pipeline_index == 1:
        response,final_file_names, final_headings, final_chunks = answer_generation(question,chunking_method="paragraph",retrieval_type=[None],chunking_k=20,hierarchical_k=None,query_k=None,multiple_query_generation=False,hierarchical_reranking=False,ranker=None,model=model)
    elif pipeline_index == "2" or pipeline_index == 2:
        response,final_file_names, final_headings, final_chunks = answer_generation(question,chunking_method="paragraph",retrieval_type=["small-to-big","hierarchical"],chunking_k=20,hierarchical_k=15,query_k=None,multiple_query_generation=False,hierarchical_reranking=False,ranker=None,model=model)
    elif pipeline_index =="3" or pipeline_index == 3:
        response,final_file_names, final_headings, final_chunks = answer_generation(question,chunking_method="paragraph",retrieval_type=["small-to-big","hierarchical"],chunking_k=20,hierarchical_k=20,query_k=None,multiple_query_generation=False,hierarchical_reranking=True,ranker="cohere",model=model)
    elif pipeline_index == "4" or pipeline_index == 4:
        print("Entered 4")
        response,final_file_names, final_headings, final_chunks = answer_generation(question,chunking_method="paragraph",retrieval_type=["small-to-big","hierarchical"],chunking_k=20,hierarchical_k=20,query_k=5,multiple_query_generation=True,hierarchical_reranking=True,ranker="cohere",model=model)
    else:
        print("Entered 5")
        response,final_file_names,final_headings, final_chunks = get_GPT_answer(question)

    print("RAG RESPONSE",response)
    return response,final_file_names, final_headings, final_chunks


def get_rag_response(question,add_images=False):
    url,captions = None,None
    response,final_file_names, final_headings, final_chunks = response_from_pipeline(question, pipeline_index=4)
    if add_images:
        _,url,captions =  provide_image_llm_response(question)
        response = response + "\n\n" + f"Also provided are some relevant images with captions : {captions}"
    return response,final_file_names, final_headings, final_chunks,url,captions

def extract_annual_data(variable:str, location:str, start_year:int, end_year:int):
    
    print("Extracting annual data for:", variable, location, start_year, end_year)
    try:
        data = []
        if start_year == end_year or start_year > end_year:
            end_year = start_year + 10
            
        variable_dict = {'tas': 'Mean air temperature at 1.5m',
                'pr': 'Precipitation rate (mm/day)',
                'tasmax': 'Maximum air temperature at 1.5m',
                'tasmin': 'Minimum air temperature at 1.5m',
                'sfcWind': 'Wind speed at 10m (m s-1)',
                'wsgmax10m': 'Wind speed gust maximum (m s-1)',
                'hurs': 'Relative humidity at 1.5m (%)',
                'huss': 'Specific humidity at 1.5m (1)',
                'uas': 'Eastward wind at 10m (m s-1)',
                'vas': 'Northward wind at 10m (m s-1)',
                'prsn': 'Snowfall flux (mm/day)',
                'snw': 'Surface snow amount (mm)',
                'psl': 'Sea level pressure (hPa)',
                'rls': 'Net Surface long wave flux (W m-2)',
                'rss': 'Net Surface short wave flux (W m-2)',
                'clt': 'Total cloud (%)'}
            
        variable_chosen,labels = search_ask_llm(variable,str(variable_dict))
        variable_chosen = [variable_chosen[0]]
        # Defaults that are chosen
        for variable_index in range(len(variable_chosen)):
            final_values = {'collection':'land-gcm',
                            'variable' : variable_chosen[variable_index],
                            'filename':'ls2_subset_01',
                            'temporalaverage':'ann',
                            'dataformat':'netcdf',
                            'area.type': 'bbox',
                            'resolution': '60',
                            'climatechangetype': 'absolute',
                            'ensemblememberset': 'land-rcm',
                            'baseline': None,
                            'scenario':['rcp85','rcp26'],
                            'timeslice': str(start_year) + "|" + str(end_year) }
            
            place_name, SW,NE = extract_locations(location)
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
            queries = [{**query,"scenario":s} for query in queries for s in query["scenario"]]
            querystrings_rcp85 = []
            querystrings_rcp26 = []
            filenames = []
            for i in queries:
                if i["scenario"] == "rcp85":
                    querystrings_rcp85.append(make_datainputs_string(i))
                else:
                    querystrings_rcp26.append(make_datainputs_string(i))
                filenames.append(final_values["filename"])

            _,_,saved_files_rcp85 = make_api_call_for_rag(querystrings_rcp85,filenames)
            _,_,saved_files_rcp26 = make_api_call_for_rag(querystrings_rcp26,filenames)
            path = os.path.join(os.getcwd(),"my-outputs")
            
            files_rcp85 = [i for i in saved_files_rcp85 if i.endswith('.nc')]
            files_rcp26 = [i for i in saved_files_rcp26 if i.endswith('.nc')]

            df_concat_rcp85 = []
            df_concat_rcp26 = []
            for i in files_rcp85:
                dataset = xr.open_dataset(os.path.join(path,i))
                df = dataset.to_dataframe()
                df.reset_index(inplace=True)
                df_concat_rcp85.append(df)

            for i in files_rcp26:
                dataset = xr.open_dataset(os.path.join(path,i))
                df = dataset.to_dataframe()
                df.reset_index(inplace=True)
                df_concat_rcp26.append(df)
            df_concat_rcp85 = pd.concat(df_concat_rcp85)
            df_concat_rcp26 = pd.concat(df_concat_rcp26)

            df_grouped_85 = df_concat_rcp85.groupby("year")[variable_chosen[variable_index]].mean().reset_index()
            df_grouped_26 = df_concat_rcp26.groupby("year")[variable_chosen[variable_index]].mean().reset_index()

            for j,k in df_grouped_85.iterrows():
                data.append({'year':k['year'], 'value':k[variable_chosen[variable_index]], 'location':location, 'variable':variable_chosen[variable_index], 'Climate Scenario': "RCP8.5"})
            
            for j,k in df_grouped_26.iterrows():
                data.append({'year':k['year'], 'value':k[variable_chosen[variable_index]], 'location':location, 'variable':variable_chosen[variable_index], 'Climate Scenario': "RCP2.6"})

        return data
    except Exception as e:
        print("Error in extracting annual data:", traceback.format_exc())
        return []


def handle_tool(call):
    args = json.loads(call.arguments)

    if call.name == "get_rag_response":
        question = args['question']
        add_images = args["add_images"]
        rag_response, filenames, headings, chunks,url,captions = get_rag_response(question,add_images)
        sources = {"file_names": filenames, "headings": headings, "chunks": chunks,"url":url,"captions":captions}
        return {"type": "function_call_output", "call_id": call.call_id, "output": str(rag_response),"sources": sources}

    elif call.name == "get_annual_climate_data":
        annual_data_response = extract_annual_data(
            args['variable'],
            args['location'],
            args['start_year'],
            args['end_year']
        )
        return {"type": "function_call_output", "call_id": call.call_id, "output": str(annual_data_response),"sources": {"annual_data_response": str(annual_data_response)}}

    else:
        return {"type": "function_call_output", "call_id": call.call_id, "output": "Unknown tool"}


def tool_rag_data_response(chat_history,query):

    try:

        messages = [{"role": "user", "content": system_instruction_tool},
                    {"role": "user", "content": f"The question is: {query} and the chat history is: {chat_history}"}]
        
        response = client.responses.create(
            model="o3",
            input=messages,
            tools=tool_definitions)
        
        print("response",response.output)
        filenames,headings,chunks,annual_data_response,url,captions = None, None, None,None,None,None
        
        attempts = 0
        while(response.output[-1].type == "function_call" and attempts < 10):
            
            fn_calls = [i for i in response.output if i.type == "function_call"]
            reasoning_items = [i for i in response.output if i.type=="reasoning" and (i.status!=None or i.status!=" ")]
            messages.extend(reasoning_items)

            
            for call in fn_calls:
                messages.append(call)
            
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(handle_tool, fn_calls))

            #messages.extend(results)

            for result in results:
                if "sources" in result:
                    source = result["sources"]
                    filenames = source.get("file_names", filenames)
                    headings = source.get("headings", headings)
                    chunks = source.get("chunks", chunks)
                    url = source.get("url", url)
                    captions = source.get("captions", captions)
                    if "annual_data_response" in source:
                        annual_data_response = source["annual_data_response"]
                    del result["sources"]
            
            messages.extend(results)

            response = client.responses.create(
                    model="o3",
                    input=messages,
                    tools=tool_definitions)
            
            print("response",response.output)
            
            attempts += 1
        if filenames:
            print("Entered Final \n \n \n \n \n")
            if annual_data_response is None:
                print("No Annual Data", )
                return response.output_text, filenames, headings, chunks,url,captions
            else:
                print("With Annual Data",)
                chunks.append(str(annual_data_response))
                return response.output_text, filenames, headings, chunks,url,captions
        else:
            return response.output_text, ["No Sources"],["No Sources"],["No Sources"],None,None
    except Exception as e:
        print(e)
        return "Something went wrong. Please try again", ["Error"], ["Error"], ["Error"],None,None
