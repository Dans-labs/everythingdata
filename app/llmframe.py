import pandas as pd
import duckdb
import time
from config import Config
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import accelerate
import bitsandbytes

class LLMFrame():
    def __init__(self, config=False, job=False, debug=False):
        self.DEBUG = debug
        self.df = False
        if job:
            self.config = config
        
    def loader(self, path="../data"):
        csvfiles = [x for x in os.listdir(path = path) if ".csv" in x]
        xlsfiles = [x for x in os.listdir(path = path) if ".xls" in x]
        if csvfiles:
            self.df = pd.concat((pd.read_csv(path +"/" + f) for f in csvfiles), ignore_index=True)
        if xlsfiles:
            self.df = pd.concat((pd.read_excel(path +"/" + f) for f in xlsfiles), ignore_index=False)
        return self.df
        
    def create_message(self, table_name, query):
        class message:
            def __init__(message, system, user, column_names, column_attr):
                message.system = system
                message.user = user
                message.column_names = column_names
                message.column_attr = column_attr

   
        system_template = self.config['instruction']
        user_template = self.config['template']

        tbl_describe = duckdb.sql("DESCRIBE SELECT * FROM " + table_name +  ";")
        col_attr = tbl_describe.df()[["column_name", "column_type"]]
        col_attr["column_joint"] = col_attr["column_name"] + " " +  col_attr["column_type"]
        col_names = str(list(col_attr["column_joint"].values)).replace('[', '').replace(']', '').replace('\'', '')

        system = system_template.format(table_name, col_names)
        user = user_template.format(query)

        m = message(system = system, user = user, column_names = col_attr["column_name"], column_attr = col_attr["column_type"])
        return m
    
    def add_quotes(self, query, col_names):
        for i in col_names:
            if i in query:
                query = str(query).replace(i, '"' + i + '"')
        return(query)
    
    def prepare_message(self, m):
        messages = [
        {
          "role": "system",
          "content": m.system
        },
        {
          "role": "user",
          "content": m.user
        }
        ]
        return messages

    def debug_messages(self, msg):
        print(msg.system)
        print(msg.user)
        print(msg.column_names)
        print(msg.column_attr)
        return

    def run_pipeline(self, messages):
        #todo: migrate to using config
        pipe = pipeline("text-generation",
                model=os.environ['MODEL'],
                torch_dtype=torch.bfloat16,
                device_map="auto")

        prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        #todo: migrate model parameters to config
        outputs = pipe(prompt,
               max_new_tokens=256,
               do_sample=True,
               temperature=0.1,
               top_k=1,
               top_p=0.95)
        print(outputs[0]["generated_text"])
        return outputs


