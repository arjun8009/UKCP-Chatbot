system_instruction = """ You will be given two data frames and two questions q1 and q2. q1 is the original question, q2 ask to repeat q1 with some
different or additional parameters. The data frame 1 contains column called param  which contains all the params required for a query and column possible values contains all the values a param can have
The data frame 2 contains columns called param which specifies which param is required for the query and param value which specifies which param value is already added to that param.
data frame 3 contains column encoded param values which specifies the encoded param values and column description which explains the meaning of the value.
DO THE FOLLOWING:
1. Read and understand q1 and q2. Understand what params and param values q2 wants to change or add with respect to q1. REMEMBER ONLY PARAMS THAT NEED TO BE CHANGED OR ADDED TO Q1.
2. Even if the user uses natural query to express what values need to be changed , every value has an encoded representation found in dataframe 3. Find those encoded representations.
3. For all encoded param values that need to be changed or added find the param using dataframe 1.
4. If you find things like change in location or spatial resolution then add those with keys as "location" and "resolution" 
5. REMEMBER ONLY RETURN THE ENTRIES OF COLUMN PARAM FROM dataframe2 WHERE THE VALUES NEED TO BE CHANGED

ONLY RETURN THE BELOW GIVEN JSON FORMAT AND DO NOT RETURN ANY OTHER FORMAT OR IT WILL BE REJECTED

JSON_RESPONSE_FORMAT:
{
  "<PARAM KEYS>": "<CHANGED PARAMETER VALUES>"
}

"""

user_prompt ="""

q1:
<Question1>
q2:
<Question2>
dataframe1:
<datadict1>
dataframe2:
<datadict2>
dataframe3:
<datadict3>

"""