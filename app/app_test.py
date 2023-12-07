from fastapi import FastAPI
import pandas as pd
from config import Config
import duckdb
import time
import os
import json
from config import Config

cfg = Config(os.environ['CONFIG'])
token = os.getenv('TOKEN')

app = FastAPI()

# Define a route using a decorator
@app.get("/")
def read_root():
    return {"Hello": "World"}


# Define another route with a path parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, query_param: str = None):
    return {"item_id": item_id, "query_param": query_param}

