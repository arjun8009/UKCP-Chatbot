from embeddings import get_image_excerpts_from_database
from llms import get_llm_output, get_or_set_openai_api_key
from choose_caption_prompt import system_instruction, user_prompt
import pandas as pd
from scipy import spatial  # for calculating vector similarities for search
import os
import time
import openai
import json
from pydantic import BaseModel,Field

class ImageIndexes(BaseModel):
    Index: list[int] = Field(description="List of indexes of the images to be returned from 0-19.")


def provide_image_llm_response(query):
    global user_prompt
    chat_history = []
    print("In images query",query)
    df = pd.read_parquet("data/imagecaptions_ukcp_do.parquet")
    #df = pd.read_parquet("backend/data/New_Captions_file.parquet")
    df_results = get_image_excerpts_from_database(query, df, top_n=20) # top_n is the number of excerpts to return from the database for the given query.
    excerpts = df_results['strings'].tolist()
    print(excerpts,len(excerpts))
    user_prompt = user_prompt.replace("<CAPTION>", str(excerpts))
    user_prompt = user_prompt.replace("<QUESTION>", query)
    chat_history.append({"role":"system","content":system_instruction})
    chat_history.append({"role":"user","content":user_prompt})

    #print(chat_history)
    client = openai.OpenAI()
    response = client.beta.chat.completions.parse(
        model='gpt-4o',
        response_format=ImageIndexes,
        messages=chat_history,
        temperature=0,
        max_tokens=500,
    )
    response_message = response.choices[0].message.parsed
    response = response_message.Index
    print("response is",response)
    if isinstance(response,list):
        response = [i if i<20 else i%20 for i in response]
        return df_results["filename"].iloc[response[0]],list(df_results["url"].iloc[response]),list(df_results["strings"].iloc[response])
    else:
        response_indexes = [i if i<20 else i%20 for i in response["Index"]]  
        return df_results["filename"].iloc[response["Index"][0]],list(df_results["url"].iloc[response_indexes]),list(df_results["strings"].iloc[response_indexes])