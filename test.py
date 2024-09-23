import requests
import json

# API endpoint
url = 'http://127.0.0.1:8000/userQA'  # Replace with your actual API URL
payload = {
    "sessionID": "ed7ca24d-92ce-41c1-a07f-a5fc4eca9b44",
  "assetID": "0af29264-d87a-4c92-a9a3-68be74674165",
  "projectID": "3ed96407-42f6-4e12-a787-f56b2a7d2b5789",
  "question": "What is the primary goal of the Climate Change (Emissions Reduction Targets) (Scotland) Act 2019?"
}

# Set the headers to accept JSON
headers = {
    'Content-Type': 'application/json'
}

# Send the POST request to the API
response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True)

# Print the streaming response
if response.status_code == 200:
    print("Streaming response from API:")
    for chunk in response.iter_lines():
        if chunk:
            print(chunk.decode('utf-8'))  # Decoding and printing the streamed chunks
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)


# import requests

# def test_chat_stream(message: str):
#     url = f"http://127.0.0.1:8000/chat_stream/{message}"

#     # Send a GET request to the API and stream the response
#     with requests.get(url, stream=True) as response:
#         if response.status_code != 200:
#             print(f"Failed to connect: {response.status_code}")
#             return

#         # Iterate over the streamed content
#         for chunk in response.iter_content(chunk_size=None):
#             if chunk:  # filter out keep-alive new chunks
#                 print(chunk.decode('utf-8'))

# # Example usage
# test_chat_stream("Hello, how is the weather today?")

