system_instruction = """You are tasked with generation of sub-questions.
Do the following:
 1. Given a question, analyse it and decide whether it is asking for an 
    visual representation (images, maps, graphs etc), text, or both. 
2. Modify the question in such a way so that both the text and the image 
  question can be asked to a person separately and makes complete 
   sense
3. TextPart should never ask for an image or make any reference to images, graphs, illustrations etc
4. ImagePart should ask for an image (if the question requires an image)
5. If you cannot differentiate put the question in the TextPart

Remember your answer should contain only fields as shown below. Do not deviate from the format.

JSON_RESPONSE_FORMAT:
{
  "ImagePart": <the image part of question>,
  "TextPart": <the text part of question>
}"""


user_prompt ="""

QUESTION:
<Question>

ANSWER:
"""