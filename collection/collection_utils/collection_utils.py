import  os
import sys

## Settings to allow imports from another folder or packages
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
sys.path.append(root_dir)

import json
import tempfile
from utils.aws_utils import get_s3_resources
from utils.common_utils import read_json_file
from fastapi import HTTPException

def get_project_metadata(docs_bucket, prefix, s3_client):
    key = f"{prefix}metadata.json"
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{key}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            s3_client.download_file(docs_bucket, key, file_path)
            metadata_json = read_json_file(file_path)
        return metadata_json
    except Exception:
        raise HTTPException(status_code=404, detail=f"Metadata file not found at '{key}'")

def get_project_config(config_bucket_name, project_id, s3_client):
    s3_resource = get_s3_resources()
    config_bucket = s3_resource.Bucket(config_bucket_name)
    
    for obj in config_bucket.objects.filter():
        if obj.key.startswith(project_id+"_"):
            config = {}
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{obj.key}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                s3_client.download_file(config_bucket_name, obj.key, file_path)
                config = read_json_file(file_path)
            return config
    
    raise HTTPException(status_code=404, detail=f"Config file for project ID '{project_id}' not found in bucket '{config_bucket_name}'")

def get_project_folder_from_id(docs_bucket, project_id):
    for obj in docs_bucket.objects.filter():
        if obj.size == 0 and obj.key.startswith(project_id) and obj.key.endswith("/"):
            return obj.key
    
    raise HTTPException(status_code=404, detail=f"Project folder for project ID '{project_id}' not found in docs bucket")
