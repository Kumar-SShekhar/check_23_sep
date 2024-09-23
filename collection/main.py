import os
from fastapi import FastAPI
from dotenv import load_dotenv
# Import routes
from routers.api_routes import collection_router
from middlewares.cors_middlewares import add_cors_middleware
from mangum import Mangum

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
add_cors_middleware(app)

# Include router
app.include_router(collection_router)

lambda_handler = Mangum(app) 
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000,reload=True)