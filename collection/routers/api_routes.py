from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from db_collection.create_collection import download_and_create_project_collection

# Define Router
collection_router = APIRouter()

# Pydantic model for request validation
class ProjectDetails(BaseModel):
    config_s3_bucket_name: str
    docs_s3_bucket_name: str
    project_id: str

# POST endpoint to create the project collection
@collection_router.post("/create-collection")
def create_project_collection(details: ProjectDetails):
    docs_bucket_name = details.docs_s3_bucket_name
    config_bucket_name = details.config_s3_bucket_name
    project_id = details.project_id

    try:
        # Call the function from your collection logic
        download_and_create_project_collection(docs_bucket_name, config_bucket_name, project_id)
        return {"message": "Collection Created Successfully"}
    except HTTPException as e:
        raise e
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")
