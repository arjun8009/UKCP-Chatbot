system_instruction = """You will be given a list of 20 captions and a query. Your job is to return 5 indexes of the captions that best answers the query. you can only give indexes between 0 to 19 where 
0 is the first caption and 19 is the last caption.
Do not answer anything apart from 0 to 19.
JSON_RESPONSE_FORMAT:
{
  "Index": <Five Numbers from 0 to 19>,
}"""

user_prompt ="""

CAPTIONS:
<CAPTION>

QUESTION:
<QUESTION>

ANSWER:
"""