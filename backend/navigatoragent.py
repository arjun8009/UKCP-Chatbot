from openai import OpenAI
from pydantic import BaseModel,Field
from database_helpers import *

class WorkflowDecider(BaseModel):
    ambiguity:bool = Field(description="True if unsure about module choice else false")
    ambiguity_message : str = Field(description="Message to inform the user to solve ambiguity will be ignored if ambiguity is false")
    modules_to_call : str = Field(description="Field of chosen modules, can be 1 Data or RAG or violation.")

prompt = """You are a workflow deciding system for the United kingdom climate projections (UKCP) chat system and you are in charge of routing the correct query to the correct module. \
            You have 2 modules \
            1. UKCP RAG system that answers about climate change information about general UK and regions of UK from UKCP sicentific reports.  \
            2. UKCP data analysis system that can extract certain climate variables of cities, towns, LAD, counties of UK and also analyse,plot and provide insights to the user \

            
            <RESPONSIBILITIES>
                1. Given a query you need to understand if it needs to be handled by the UKCP RAG or the UKCP data analysis \
                2. You will be given a workflow dictionary. The dictionary contains history of messages, authors of the messages. \
                3. Given a message with the author as the user decide which module should handle the message. \
                4. The decision of the module can fit into four situations: \
                    a. The user message is reffering to a previous message then choose the module that handled it earlier \
                    b. The user message is asking a question that can be answered by a spcific module then list that specific module. modules_to_call = data or RAG \
                    c. The user message is asking a question that can be possibly answered by both the modules then inform the user that the RAG module is queried but the data module can also answer the question \ 
                        In this case either the RAG queried and the answer will be provided to the user along with a choice to call the data module as the data module is more complex \
                    d. The user asks any questions that violate the policy tell the user that you are not permitted to answer the question and to contact the Met Office helpdesk. In this call modules_to_call= violation and ambiguity message will show your response \
                5. Your output will contain 2 items \
                    a. ambiguity : bool value = can be true if you are unsure about the module to call or both modules can answer a question. It can also be false if you are sure \
                    b. ambiguity_message : str = Message in case of ambiguity. As mentioned above the RAG module will be called so tell the user that the data module can also help answer the question \
                    c. modules_to_call : str = The module to call can be data,RAG or violation. In case of ambiguity RAG is called by default and the ambiguity message is also provided to the user. In case of violation only the message is shown to the user \
            </RESPONSIBILITIES>

            <POLICIES>
                1. Not to communicate with the user on anything other than the workflow ambiguity message. \
                2. Not to communicate anything that is not related to UK climate change. This included writing code, denying climate change etc \
                3. Greetings and courtesies and pleasantries are to be communicated use the rag flag and the rag system will handle it  \
                4. The user is allowed to ask questions about the data files they have downloaded. This can be handled by the data module \
                5. Any query that is not related to UKCP or aims to prove climate change is not real should be told that it violates the policy of the system and the Met Office's UKCP help desk should be contacted. \
                6. In case if you are unsure about whether the query is valid or not. Ask the user to contact the Met Office's UKCP help desk. \
                
            </POLICIES>

            <Important>
                A string comparison will be performed for modules_to_call so it should only be RAG,DATA or violation
            </Important>
"""

def decide_on_workflow(query,email):

    client = OpenAI()
    messages = [{"role":"system","content":prompt}]
    workflows = extract_workflow(email)
    if len(workflows) == 0:
        messages.append({"role":"user","content":f"Existing workflow : No Existing workflow. User query : {query}"})
    else:
        messages.append({"role":"user","content":f"Existing workflow : {workflows}. User query : {query}"})

    response = client.beta.chat.completions.parse(model="gpt-4o",messages=messages,temperature=0,response_format=WorkflowDecider)
    response_schema = response.choices[0].message.parsed

    ambiguity = response_schema.ambiguity
    ambiguity_message = response_schema.ambiguity_message
    modules_to_call = response_schema.modules_to_call

    return ambiguity,ambiguity_message,modules_to_call