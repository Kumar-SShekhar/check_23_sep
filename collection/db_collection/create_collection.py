import  os
import sys

## Settings to allow imports from another folder or packages
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
sys.path.append(root_dir)

from langchain_postgres import PGVector
from langchain_postgres.vectorstores import DistanceStrategy
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
from config.aws_config import bedrock_embedding
from database.postgres_connection import connect_to_postgres_db, connect_to_postgres_vector_db
from collection_utils.collection_utils import get_project_config,get_project_folder_from_id,get_project_metadata
from document_preprocessing.llamaparse_processing import get_parsed_documents
from utils.aws_utils import get_s3_client,get_s3_resources
from fastapi import HTTPException

def get_existing_ids(cur, document_id,project_id):
    id_selection_query = f"""SELECT id FROM public.langchain_pg_embedding WHERE id LIKE '{document_id}%' AND collection_id= (SELECT uuid FROM public.langchain_pg_collection WHERE name='{project_id}')"""
    try:
        cur.execute(id_selection_query)
        ids = cur.fetchall()
        return ids
    except:
        return []

def insert_documents(vectorstore, documents, document_id,text_splitter,project_id):
    docs = text_splitter.split_documents(documents=documents)
    for i, doc in enumerate(docs):
        doc.metadata["id"] = f"{document_id}_{project_id}_{i + 1}"
    vectorstore.add_documents(
        documents=docs,
        ids=[doc.metadata["id"] for doc in docs],
    )

def process_documents(documents,document_id, cur, vectorstore,text_splitter,project_id):
    ids = get_existing_ids(cur, document_id,project_id)
    if ids:
        vectorstore.delete(ids=ids)
    insert_documents(vectorstore, documents, document_id, text_splitter,project_id)

def create_document_collection(config_json,documents,document_id):
    embeddings = bedrock_embedding(model_id=config_json["collection_flow_v"]["parameters"]["embeddings_model"])
    db_conn = connect_to_postgres_db()
    cur = db_conn.cursor()
    if config_json["collection_flow_v"]["parameters"]["similarity_matching"].lower() == "euclidean":
        distance_strategy=DistanceStrategy.EUCLIDEAN
    elif config_json["collection_flow_v"]["parameters"]["similarity_matching"].lower() == "mmr":
        distance_strategy = DistanceStrategy.MAX_INNER_PRODUCT
    else:
        distance_strategy = DistanceStrategy.COSINE

    project_id = config_json['project_metadata']['project_id']
    vectorstore = PGVector(
        collection_name=project_id,
        collection_metadata={'Desc': config_json['project_metadata']['project_desc']},
        embedding_length = config_json["collection_flow_v"]["parameters"]["vector_size"],
        connection=connect_to_postgres_vector_db(),
        embeddings=embeddings,
        distance_strategy=distance_strategy
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config_json["collection_flow_v"]["parameters"]["chunk_size"],
        chunk_overlap=config_json["collection_flow_v"]["parameters"]["chunk_overlap"],
        length_function=len,
        is_separator_regex=False,
    )

    process_documents(documents,document_id,cur,vectorstore,text_splitter,project_id)

def download_and_create_project_collection(docs_bucket_name, config_bucket_name, project_id):
    s3_resource = get_s3_resources()
    s3_client = get_s3_client()

    docs_bucket = s3_resource.Bucket(docs_bucket_name)
    
    try:
        # Attempt to get project configuration
        project_config = get_project_config(config_bucket_name, project_id, s3_client)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Config file for project ID '{project_id}' not found in bucket '{config_bucket_name}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving project config: {str(e)}")
    
    try:
        # Attempt to get project folder
        prefix = get_project_folder_from_id(docs_bucket, project_id)
        if not prefix:
            raise HTTPException(status_code=404, detail=f"Project folder for project ID '{project_id}' not found in docs bucket")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving project folder: {str(e)}")

    try:
        # Attempt to get project metadata
        metadatas = get_project_metadata(docs_bucket_name, prefix, s3_client)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Metadata file not found: {str(e)}")
    
    files_found = False

    # Process documents based on project configuration
    if len(project_config["collection_flow_v"]["parameters"]["add_docs"]) == 0:
        for obj in docs_bucket.objects.filter(Prefix=prefix):
            if obj.size == 0 and obj.key.endswith("/"):
                continue
            else:
                if obj.key.endswith(".json"):
                    continue
                else:
                    files_found = True
                    with tempfile.TemporaryDirectory() as temp_dir:
                        file_path = f"{temp_dir}/{obj.key}"
                        doc_id = os.path.basename(obj.key)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        s3_client.download_file(docs_bucket_name, obj.key, file_path)
                        docs = get_parsed_documents(file_path, metadatas.get(doc_id, {}))
                        create_document_collection(project_config, docs, doc_id)
    else:
        for doc_id in project_config["collection_flow_v"]["parameters"]["add_docs"]:
            key = f"{prefix}{doc_id}"
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = f"{temp_dir}/{key}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                s3_client.download_file(docs_bucket_name, key, file_path)
                docs = get_parsed_documents(file_path, metadatas.get(doc_id, {}))
                create_document_collection(project_config, docs, doc_id)
                files_found = True

    if not files_found:
        raise HTTPException(status_code=404, detail=f"No files found in folder '{prefix}' for project ID '{project_id}'")

