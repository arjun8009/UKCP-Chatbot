import openai
import os
from get_llm_RAG_response import response_from_pipeline
from pydantic import BaseModel,Field

os.environ["OPENAI_API_KEY"] = ' '

helper_information = """The UKCP chatbot is trained on the following documents and all the answers include content from the documents :

['1-hr-wallingford.v2.pdf',
 '2-leeds.pdf',
 '3-forest.pdf',
 '4.-wsp.coastal-cliff-recession-under-climate-change.pdf',
 '5-uoe-cibse.pdf',
 '6-sepa.final.pdf',
 'bristol_city_council_ukcp_case_study.pdf',
 'ceh_ukcp_case_study.pdf',
 'faq_on_ukcp_local_issue.pdf',
 'forest_research_ukcp_case_study.pdf',
 'Geophysical Research Letters - 2019 - Hausfather - Evaluating the Performance of Past Climate Model Projections.pdf',
 'HCTN_101_2018P.pdf',
 'hctn_109_comparison_ukcp_cmip6.pdf',
 'Intl Journal of Climatology - 2023 - Kendon - State of the UK Climate 2022.pdf',
 'published-comment-tracker-local-2.2km.pdf',
 'published-comment-tracker.pdf',
 's41467-023-36499-9.pdf',
 'UKCP User Group Information.pdf',
 'ukcp-climate-drifts-report.pdf',
 'UKCP-Convection-permitting-model-projections-report.pdf',
 'ukcp-probabilistic-extremes-report.pdf',
 'ukcp-probabilistic-projections-v2022-additionalmaps.pdf',
 'UKCP18-Derived-Projections-of-Future-Climate-over-the-UK.pdf',
 'ukcp18-fact-sheet-derived-projections.pdf',
 'ukcp18-fact-sheet-sea-level-rise-and-storm-surge.pdf',
 'ukcp18-fact-sheet-temperature.pdf',
 'ukcp18-fact-sheet-weather-types.pdf',
 'ukcp18-fact-sheet-wind_march21.pdf',
 'ukcp18-factsheet-local-2.2km.pdf',
 'ukcp18-factsheet-precipitation.pdf',
 'ukcp18-factsheet-storms.pdf',
 'ukcp18-factsheet-using-rainfall-data-from-ukcp-v2.pdf',
 'ukcp18-guidance---caveats-and-limitations.pdf',
 'ukcp18-guidance---how-to-bias-correct.pdf',
 'ukcp18-guidance---how-to-use-the-land-projections.pdf',
 'ukcp18-guidance---representative-concentration-pathways.pdf',
 'ukcp18-how-are-the-land-projections-connected.pdf',
 'UKCP18-Land-report.pdf',
 'UKCP18-Marine-report.pdf',
 'ukcp18-newsletter.apr22.pdf',
 'ukcp18-newsletter.april-2019.pdf',
 'ukcp18-newsletter.aug21.pdf',
 'ukcp18-newsletter.oct21.pdf',
 'UKCP18-Overview-report.pdf',
 'ukcp18-overview-slidepack-march21.pdf',
 'ukcp18-overview-slidepack-notes.ff.pdf',
 'ukcp18-overview-summary.pdf',
 'ukcp18-peer-review-panel-description.pdf',
 'UKCP18-Probabilistic-Update-Report.pdf',
 'ukcp18-technical-note-clipping-and-baseline-guidance-on-land-strand-1-data-in-ukcp18.pdf',
 'ukcp18_data_availability_jul-2021.pdf',
 'ukcp18_factsheet_global_rcp_2_6.pdf',
 'ukcp18_factsheet_jet_stream.pdf',
 'ukcp18_factsheet_nao.pdf',
 'ukcp18_factsheet_probabilistic_projections.pdf',
 'ukcp18_factsheet_sea_level_rise_storm_surge_supp_data_mar23.pdf',
 'ukcp18_factsheet_snow_jul-2021.pdf',
 'ukcp18_factsheet_soil_moisture.pdf',
 'ukcp18_factsheet_weather_patterns.pdf',
 'ukcp18_guidance_data_availability_apr_21.pdf',
 'ukcp18_headline_findings_v3.pdf',
 'ukcp18_headline_findings_v4_aug22.pdf',
 'ukcp18_local_update_faq.pdf',
 'ukcp18_local_update_report_2021.pdf',
 'ukcp18_peer_review_process.pdf',
 'ukcp_graupel_technical_note.pdf',
 'ukcp_local_report_2023.pdf',
 'ukcp_tech_note_sea_level_mar23.pdf',
 'user-group-description.pdf',
 'waves_ukcp_case_study.pdf']

Pipelines : These are RAG methodologies that are used to extract information from the documents. The pipelines are as follows:
1. Pipleline 1 : Simple RAG system that uses the most relevant 5 chunks of text from the documents to answer the question. This is the default pipeline used by the chatbot.
2. Pipeline 2 : This uses paragraphs from the documents to answer the question. This is used when the question is too long and cannot be answered using the default pipeline.
3. Pipeline 3 : It uses sections and much bigger chunks of text and applies some optimization methods to extract the most relevant information.
4. Pipeline 4 : It uses sections, reranking algorithms and query augmentation methods to extract the most relevant information.

Functionalities : Text : Only text responses
Images : Only image responses
Both : Text and image responses
Data : Form like conversation that can extract information from the UKCP databases.
Data-Default : Form like conversation that can extract information from the UKCP databases. The default functionality is restricted to 60km resolution data only. It will apply defaults so less questions will be asked from the user
Data-Analysis : Can help understand the extracted data. Note it will not work if no data is exteracted from the databases. It can plot, visualize, do statistical analysis etc. But only on the downloaded data

Data Functionality : 

The data functionality can extract information from the UKCP databases.It is vital that the query to the data functionality contains the spatial resolution and the location where the climate data is to be extracted.Currently the following databases are included:

60 km res Daily, monthly and Annual data
12 km res Dailty, monthly and Annual data
2.2 km res Daily, monthly and Annual data

All datasets are restricted to UK only

Usage: 
To get text based answers use the Text option in the dropdown
Pipelines can be anything 1-5 as they only affect the text based answers
To get image based answers use the Images option in the dropdown
To get data you can use Data for long and specific data retrieval and use Data-Default for short and quick data retrieval.
Data analysis is used to understand the data extracted from the databases. It will not work if no data is extracted from the databases using the Data or Data-Default functionality.
Both gives text and image based answers.

Example Questions:

QA module :  1. What is UKCP ?
            2. What is the difference between UKCP18 and UKCP09 ?
            3. What are the climate projections for the UK ?
            4. Tell me something about UKCP temperature projections ?
            5. What are the RCPs used in UKCP18 ?
            6. What are the spatial and temporal resolutions of the UKCP18 data ?

Data or Data-default module : 1. I want to know the rainfall data for London for the next 10 years.
            2. I want to know the temperature data for London for the next 10 years.
            3. I want to know the wind data for London for the next 10 years.

Data-Analysis module : 1. I want to see the plot of rainfall data from 2018-2050 for London.
                       2. Plot the monthly temperature data for London from the year 2018.
                       3. Plot the data for temperature for the year 2002 on a map of UK.
                       4. Describe the data I have extracted from the databases.


Data Default functionality is restricted to 60km res only
"""



def provide_helpful_information(query):

    global helper_information

    helper_prompt = """You are a helpful assitant that can provide indformation. \
     Use only the provided information to answer the question. \
    1. Do not make up any information. \
    2. Do not provide any information that is not in the provided information.\
    3. It is extremely vital that you do not provide any information that is not within <Provided Information> \
    <Provided Information> \
    <Info> \
    </provided Information>"""

    chat_history = []
    helper_prompt = helper_prompt.replace("<Info>", helper_information)
    chat_history.append({"role": "system", "content": helper_prompt})
    user_prompt_dup = helper_prompt
    chat_history.append({"role": "user", "content": query})
    print(chat_history)
    helper_prompt = user_prompt_dup
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=chat_history,
        temperature=0,
        max_tokens=1024,
    )
    response_message = response.choices[0].message.content
    print(response_message)
    return response_message


def make_query(last_5_messages,query):

    prompt = """You are a query formulator. There is a RAG system that needs a user question. Sometimes user questions refer to previous questions and sometimes they do not. \
        1. Given the users last 5 QA use them to understand the context of the query. \
        2. If the query is related to the previous queries then use the context of the previous queries to form a new query that has some context and can be given to a RAG system to extract relevant information \
        3. If the query is not related to the previous queries then use the query as it is. \
        NOTE : YOUR SOLE JOB IS TO FORMULATE A QUERY THAT CAN BE GIVEN TO A RAG SYSTEM. YOU ARE NOT TO ADD ANY ADDITIONAL INFORMATION OR MAKE ANY ASSUMPTIONS. """
    
    chat_history = []
    chat_history.append({"role": "system", "content": prompt})
    
    user_prompt = f"""<QUERY>
        {query}
        </QUERY>
        
        <LAST 5 QUESTIONS>
        {last_5_messages}
        </LAST 5 QUESTIONS>"""
    
    chat_history.append({"role": "user", "content": user_prompt})
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=chat_history,
        temperature=0,
        max_tokens=256,
    )
    response_message = response.choices[0].message.content
    print(response_message)
    return response_message


def resolve_questions_in_data_module(query,user_response):

    rag_context,_,_,_ = response_from_pipeline(str(query) + "   " + str(user_response),4)
    helpful_context = provide_helpful_information(user_response)
    print("In Resolve",query,user_response)

    prompt = f"""You are a helpful assistant part of a chatbot system. The chatbot has a data module that can provide users climate data, \
        given that the users can answer questions on the choice of parameter.\
        You will be given the query and the user response. Now the chatbot has decided that the user response does not contain the specific paramter choice it had asked for \
        Your job is to do the following : \
        1. Read the query and the user response \
        2. The chatbot has a RAG and a assistant system which contain information from climate reports and usage of the chatbot. The user response will be provided as inputs to these systems to get contextual information \
        3. Use the contextual information, query and response to formulate a suitable reply for the user response \
        """
    
    user_prompt = f"""
        <QUERY>
        {query}
        </QUERY>
        
        <USER RESPONSE>
        {user_response}
        </USER RESPONSE>
        
        <RAG RESPONSE TO USER RESPONSE>
        {rag_context}
        </RAG RESPONSE TO USER RESPONSE>
        
        <ASSISTANT RESPONSE TO USER RESPONSE>
        {helpful_context}
        </ASSISTANT RESPONSE TO USER RESPONSE>"""
    
    messages = [{"role":"system","content":prompt},
                {"role":"user","content":user_prompt}]
    client = openai.OpenAI()
    resolve_response = client.chat.completions.create(model="gpt-4o-mini",
                                                      temperature=0, max_tokens=500,messages=messages)
    
    return resolve_response.choices[0].message.content


class Prefilter(BaseModel):
    asking_for_data : bool = Field(description="True if the user is asking for data otherwise false")
    message : str = Field(description="message to the user if asking_for_data is false otherwise empty string")


def prefilter_to_data_module(query):

    prompt = """You are a helper to the data module of a climate chatbot system. This data module is helpful to extract climate data from databases given a user query. \
                The chatbot has a RAG system, a data analysis system and a chatbot help system. \
                
                Now Do the following : \
                <REASONING STEPS>
                1. Given a query to the data module you need to judge if the query is asking for climate data. \
                2. If the query is asking something technical related to climate science then tell the user that it needs to be directed to QA System \
                3. If the query is asking for some guidance related to the chatbot and its data then direct the user to use the Help system \
                4. If the query is asking to analyse the data or plot something or do something with the data. Tell the user to ask for the data from the Data or Data Default system and then ask the analysis question to the Data-Analysis system \
               </REASONING STEPS> 

               <OUTPUT>
               asking_for_data : bool = True if the query is asking for data else False
               message : str = string containing the message to the user to use either of the QA,Help and Data analysis in case asking_for_data is false else empty string 
               </OUTPUT>

               <Examples>
               
               Example 1:

               INPUTS:
               <COMMENT>  The user here enquires what data the system has but does not ask for specific data </COMMENT>
               Question : what data do you have
               OUTPUTS:
               asking_for_data = False
               message = The query you have answered is most suitable to be asked to the Help section. This data module can only take questions that directly request data with type of climate variable location and spatial resolution

               Example 2:

               INPUTS : 
               <COMMENT> Although very vague query it will still be considered as asking for data as it is directly asking for data</COMMENT>
               Question : I want some climate data
               OUTPUTS:
               asking_for_data = True
               message = ""

               Example 3:
               <COMMENT>  The user here enquires what spatial resolution the system has but does not ask for specific data. This is a technical question not pertaining to the chatbot so direct to QA System </COMMENT>
               Question : what is the various spatial resolutions available for ukcp data
               OUTPUTS:
               asking_for_data = False
               message = The query you have answered is most suitable to be asked to the QA section. This data module can only take questions that directly request data with type of climate variable location and spatial resolution

              Example 4:
               <COMMENT>  The user here enquires to plot data. Here the user is not asking for data but want to plot the data. So we tell the user to get the data using data or data default and then use data analysis functionality of the chatbot</COMMENT>
               Question : plot the temperature in london between 2030 to 2040
               OUTPUTS:
               asking_for_data = False
               message = The query you have answered is most suitable to be asked to the Data Analysis section. You should ask this module to extract temperature data in london between 2030-2040 and then use the Data-Analysis module.This data module can only take questions that directly request data with type of climate variable location and spatial resolution
               
            </Examples>
                """
    messages = [{"role":"system","content":prompt},
                {"role":"user","content":f"""The user query is <Question>{query}</Question>"""}]
    
    client = openai.OpenAI()
    response_message = client.beta.chat.completions.parse(model="gpt-4o-mini",temperature=0,messages=messages,response_format=Prefilter)
    response_message = response_message.choices[0].message.parsed

    return response_message