import  os
import sys
from sqlalchemy.exc import SQLAlchemyError

## Settings to allow imports from another folder or packages
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
sys.path.append(root_dir)
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from configparser import ConfigParser
import psycopg2

## Fetching the Credentials from the database.ini file
def config(filename=r'database/database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return db

## Connection to the db for Structured data
def connect_to_postgres_db():
    conn = None
    try:
        params = config()
        # print("*"*50)
        # print(params)
        conn = psycopg2.connect(**params)
        # print("Database connection successful")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    return conn


## Connection to the vector db for the Embeddings
def connect_to_postgres_vector_db():
    try:
        params = config()
        db_url = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
        engine = create_engine(db_url)
        # print("Vector database connection successful")
        return engine
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
connect_to_postgres_db()