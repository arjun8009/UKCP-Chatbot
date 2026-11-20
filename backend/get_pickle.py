import requests
import base64
import pickle

def get_vectorizer(chunking_method,similarity_top_k,metadata,queries):
    # Define the URL of your Flask API
    
    api_url = 'http://localhost:8080/api/get-index'
    # Define the query parameter if needed (e.g., chunking_method)
    params = {'chunking_method': chunking_method,'similarity_top_k':similarity_top_k,'metadata':metadata,'queries':queries}  # Replace 'default' with the actual chunking method if required

    # Make a GET request to the API
    response = requests.get(api_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        response_json = response.json()
        
        # Extract the base64-encoded pickled object from the response
        retrieved_nodes = response_json.get('vector_index')
        
        if retrieved_nodes:
            # Decode the base64 string
            nodes_serialized = base64.b64decode(retrieved_nodes)
            retrieved_nodes = pickle.loads(nodes_serialized)
            
            # Deserialize the object using pickle
            
            # Use the deserialized object (printing for demonstration)
            print("Deserialized object:")
            return retrieved_nodes
        else:
            print("Error: No 'vector_index' field in the response.")
            return None
    else:
        print(f"Error: Received status code {response.status_code} from the API.")
        print(response.text)
        return None
