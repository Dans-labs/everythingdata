from fastapi import FastAPI, Request
from nltk import tokenize, sent_tokenize
from localconfig import SYS_PROMPT, R_SYS_PROMPT
from langchain.llms import Ollama
from fastapi.responses import HTMLResponse
from nltk import tokenize, sent_tokenize
import pandas as pd
from utils import graphreader, generate_md5, infocleaner, getlanguage
from config import Config
import duckdb
import time
import os
import json
from llmframe import LLMFrame, keywords_cleaner
from config import Config
from typing import Optional
from pydantic import BaseModel
import nltk
nltk.download('punkt')

cfg = Config(os.environ['CONFIG'])
token = os.getenv('TOKEN')

app = FastAPI()

# Define a route using a decorator
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Endpoint to handle POST requests
@app.post("/graph/")
async def graph_item(info: Request):
    transferdata = await info.json()
    llm = LLMFrame()
    data = llm.graph_decompression(transferdata)
    return data

@app.get("/graph")
def graph(job='custom', prompt='graph.prompt', inputtext: Optional[str] = None):
    llm = LLMFrame()
    data = llm.graph_decompression({'text': inputtext})
    return data

@app.get("/custom")
def translate(job='custom', customquery: Optional[str] = None, language: Optional[str] = None, format: Optional[str] = None):
    query = None
    if not format:
        format = 'html'
    if not language:
        language = 'English'
    llm = LLMFrame(config=cfg[job], job=job)
    msg = llm.create_message(table_name = None, query = query, customquery=customquery)
    m = llm.create_message(table_name = None, query = query, customquery=customquery)
    llm.debug_messages(m)
    messages = llm.prepare_message(m)
    o = llm.run_pipeline(messages)
    if format == 'html':
        return HTMLResponse(content=str(o[0]['generated_text']).replace('\n', '<br>'), status_code=200)
    else:
        return json.dumps(o)

@app.get("/keywords")
def translate(job='main_keywords', customquery: Optional[str] = None, language: Optional[str] = None, format: Optional[str] = None):
    query = None
    if not format:
        format = 'html'
    if not language:
        language = 'English'
    llm = LLMFrame(config=cfg[job], job=job)
    msg = llm.create_message(table_name = None, query = query, customquery=customquery)
    m = llm.create_message(table_name = None, query = query, customquery=customquery)
    llm.debug_messages(m)
    messages = llm.prepare_message(m)
    o = keywords_cleaner(llm.run_pipeline(messages))
    if format == 'html':
        return HTMLResponse(content=str(o[0]['generated_text']).replace('\n', '<br>'), status_code=200)
    else:
        return json.dumps(o)

@app.post("/translate/")
async def translate_item(info: Request, job='translate'):
    transferdata = await info.json()
    if 'format' in transferdata:
        format = transferdata['format']
    else:
        format = 'json'
    llm = LLMFrame(config=cfg[job], job=job)
    if 'concept' in transferdata:
        m = llm.create_message(table_name = None, query = None, customquery=transferdata['concept'], context=transferdata['context'])
        messages = llm.prepare_message(m)
        o = llm.run_pipeline(messages)
        if format == 'html':
            return HTMLResponse(content=str(o[0]['generated_text']).replace('\n', '<br>'), status_code=200)
        if format == 'json':
            dataresponse = infocleaner(str(o[0]['generated_text']))
            dataresponse['concept'] = transferdata['concept']
            dataresponse['md5'] = generate_md5(dataresponse['concept']) 
            dataresponse['md5context'] = generate_md5("%s %s" % (dataresponse['concept'], transferdata['context']))
            dataresponse['lang'] = getlanguage(transferdata['context'])
            return dataresponse
        else:
            return json.dumps(o)
    return

@app.get("/translate")
def translate(job='translate', customquery: Optional[str] = None, language: Optional[str] = None, format: Optional[str] = None, context: Optional[str] = None):
    transferdata = { 'concept': customquery }
    if format:
        transferdata['format'] = format
    else:
        format = 'json'
    query = None
    if not format:
        format = 'html'
    if not language:
        language = 'English'
    if not context:
        context = 'nocontext'
    transferdata['context'] = context
    
    llm = LLMFrame(config=cfg[job], job=job)
    msg = llm.create_message(table_name = None, query = query, customquery=customquery)
    m = llm.create_message(table_name = None, query = query, customquery=customquery, context=context)
    llm.debug_messages(m)
    messages = llm.prepare_message(m)
    o = llm.run_pipeline(messages)
    if format == 'html':
        return HTMLResponse(content=str(o[0]['generated_text']).replace('\n', '<br>'), status_code=200)
    else:
        #return json.dumps(o)
        if o:
            dataresponse = infocleaner(str(o[0]['generated_text']))
            dataresponse['concept'] = transferdata['concept']
            dataresponse['md5'] = generate_md5(dataresponse['concept'])
            dataresponse['md5context'] = generate_md5("%s %s" % (dataresponse['concept'], transferdata['context']))
            dataresponse['lang'] = getlanguage(transferdata['context'])
            return dataresponse

@app.get("/summarize")
def summarize(job='translate', customquery: Optional[str] = None, language: Optional[str] = None, format: Optional[str] = None):
    query = None
    if not language:
        language = 'English'
    return "Summarize %s" % customquery

@app.get("/tranformers")
def transformers(job='sql_generator', customquery: Optional[str] = None, format: Optional[str] = None):
    query = None
    if not format:
        format = 'html'
    llm = LLMFrame(config=cfg[job], job=job)
    df = llm.loader()
    print(query)
    if not customquery:
        query = cfg[job]['query']
    print("Q2: %s" % query)
    msg = llm.create_message(table_name = "df", query = query, customquery=customquery)

    m = llm.create_message(table_name = "df", query = query, customquery=customquery)
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

