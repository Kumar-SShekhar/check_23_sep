import requests
import time
import os
from langchain_core.documents import Document

class LlamaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.cloud.llamaindex.ai/api'
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def upload_pdf(self, file_path):
        url = f'{self.base_url}/parsing/upload'
        files = {
            'file': (file_path, open(file_path, 'rb'), 'application/pdf')
        }

        response = requests.post(url, headers=self.headers, files=files)

        if response.status_code == 200:
            print(f"Processing File {os.path.basename(file_path)}")
            return response.json()['id']
        else:
            print(f"Error uploading file: {response.status_code}, {response.text}")
            return None

    def check_job_status(self, job_id):
        url = f'{self.base_url}/parsing/job/{job_id}'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error checking job status: {response.status_code}, {response.text}")
            return None

    def get_json_result(self, job_id):
        """Fetches the parsing result in Json format."""
        url = f'{self.base_url}/parsing/job/{job_id}/result/json'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching Json result: {response.status_code}, {response.text}")
            return None


def get_parsed_documents(file_path,metadata_json):
    llama_api = LlamaAPI(os.getenv("LLAMA_CLOUD_API_KEY"))
    job_id = llama_api.upload_pdf(file_path)
    if not job_id:
        return
    while True:
        status = llama_api.check_job_status(job_id)
        if status and status.get('status') == 'SUCCESS':
            break
        else:
            print("Parsing job in progress...")
        time.sleep(5)

    json_objects = llama_api.get_json_result(job_id)
    json_lists = json_objects["pages"]
    documets = []
    relative_path = os.path.basename(file_path)
    for idx,page in enumerate(json_lists):
        metadata = {"source":relative_path,"page":page["page"]}
        for key in metadata_json.keys():
            metadata[key] = metadata_json[key]
        document = Document(page_content=page['text'], metadata=metadata)
        documets.append(document)

    return documets