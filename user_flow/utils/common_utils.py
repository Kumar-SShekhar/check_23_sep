from fastapi import HTTPException
import json

def read_json_file(file_path):
    try:
        # Open the JSON file and load its content
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"Error decoding JSON from file: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
