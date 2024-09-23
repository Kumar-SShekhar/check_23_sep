import json
import re

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from dotenv import load_dotenv
load_dotenv()

# Initialize the global store for chat histories
store = {}

# Method to create session-based message history
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
        
def extract_json_from_string(text):
    print(text)
    json_pattern = re.compile(
        r'<json>\s*({[\s\S]*?})\s*</json>|'           
        r'```(?:json)?\s*({[\s\S]*?})\s*```|'         
        r'({[\s\S]*?})'                              
    )
    match = json_pattern.search(text)
    
    if match:
        # Extract the matched string, filtering the tuple for valid non-None elements
        json_str = "".join([m for m in match.groups() if m is not None]).strip()

        try:
            # Parse the JSON string
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}, content: {json_str}")
            return None
    else:
        print("No valid JSON structure found.")
        return None

