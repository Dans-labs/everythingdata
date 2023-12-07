from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
from config import Config
import duckdb
import time
import os
import json
from llmframe import LLMFrame
from config import Config
from typing import Optional

cfg = Config(os.environ['CONFIG'])
token = os.getenv('TOKEN')

app = FastAPI()

# Define a route using a decorator
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/tranformers")
def transformers(job='sql_generator', format: Optional[str] = None):
    if not format:
        format = 'html'
    llm = LLMFrame(config=cfg[job], job=job)
    df = llm.loader()
    query = cfg[job]['query']
    
    m = llm.create_message(table_name = "df", query = query)
    llm.debug_messages(m)
    messages = llm.prepare_message(m)
    o = llm.run_pipeline(messages)
    if format == 'html':
        return HTMLResponse(content=str(o[0]['generated_text']).replace('\n', '<br>'), status_code=200)
    else:
        return json.dumps(o)

# Define another route with a path parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, query_param: str = None):
    return {"item_id": item_id, "query_param": query_param}

