import  os
import sys

## Settings to allow imports from another folder or packages
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..', '..')
sys.path.append(root_dir)
import boto3
from langchain_aws.embeddings import BedrockEmbeddings


def get_s3_resources():
    s3_resource = boto3.resource(
        service_name="s3",
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    )
    return s3_resource

def get_s3_client():
    s3_client = boto3.client(
        service_name="s3",
        region_name=os.getenv("AWS_DEFAULT_REGION"),
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    )
    return s3_client


def list_bucket_contents(bucket):
    print(f"Object lists for the bucket: {bucket}")
    for obj in bucket.objects.filter():
        # Skip directories
        if obj.size == 0 and obj.key.endswith("/"):
            print(obj.key)
            continue
        else:
            print(obj.key)