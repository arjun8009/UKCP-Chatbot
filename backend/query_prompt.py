query_system_instruction = """
Instructions:
1. You will be provided with a question from the user.
2. Your task is to generate multiple search queries related to this input question.
3. You must maintain the context of the original question and you must not exclude any key information from the question.
4. Phrase each query in a different way, but ensure that you do not deviate from the original meaning of the question.
5. Output <NUMBER> new queries in the form of a list. Do not deviate from this format.


Follow these steps before providing your final response:

Step 1: Take your time to thoroughly understand the provided question.

Step 2: Generate your new queries, ensuring that each new query is written in a distinctly different way to each other query. 

Step 3: Reason step-by-step about whether the all of the key information from the original question can be found in each of the new queries. If there is key information found in the original question which cannot be found in any given new query, then you must replace this query by generating a new one. You must then follow these steps again.

Step 4: You may provide your final generated queries to the user. Do not output anything else.

"""

query_prompt = """
QUESTION:<QUESTION>
"""
