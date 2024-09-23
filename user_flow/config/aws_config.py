import  os
import sys

## Settings to allow imports from another folder or packages
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..', '..')
sys.path.append(root_dir)
import boto3
from dotenv import load_dotenv
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws import ChatBedrock
load_dotenv()


def bedrock_embedding(model_id):
    # Set up the AWS Bedrock client
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )

    # Initialize Bedrock Embeddings with Titan v2
    embeddings = BedrockEmbeddings(
        model_id=model_id, 
        client=bedrock_runtime
    )

    return embeddings

# Method to initialize the LLM
def initialize_llm(model_id,temperature):
    llm = ChatBedrock(
            model_id=model_id,
            model_kwargs=dict(temperature=temperature),
            streaming=True
        )
    return llm